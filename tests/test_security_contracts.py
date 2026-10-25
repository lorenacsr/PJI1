import asyncio
from io import BytesIO
from datetime import timedelta
import pytest
from fastapi import HTTPException, UploadFile
from app.core.config import Settings
from app.core.security import create_access_token, decode_token
from app.core.media import media_link, valid_media_ticket
from app.core.images import read_image
from urllib.parse import parse_qs,urlsplit
from app.routers.checklists import _csv_cell

@pytest.mark.parametrize('secret',['short','pizzaria-secret-key-change-in-production','pizzaria-secret-key-change-in-production-2024'])
def test_production_rejects_default_or_short_secret(secret):
    with pytest.raises(ValueError):Settings(_env_file=None,ENV='production',SECRET_KEY=secret)

def test_production_accepts_explicit_private_configuration():
    Settings(_env_file=None,ENV='production',SECRET_KEY='T'*48,SEED_ADMIN_PASSWORD='Admin-Teste-Longa-123',SEED_MANAGER_PASSWORD='Gestor-Teste-Longa-123')

def test_jwt_expiry_and_media_scope():
    assert decode_token(create_access_token('test',timedelta(seconds=-1))) is None
    link=media_link('/uploads/test.png');ticket=parse_qs(urlsplit(link).query)['ticket'][0]
    assert valid_media_ticket(ticket,'test.png')
    assert not valid_media_ticket(ticket,'other.png')
    assert not valid_media_ticket(create_access_token('user'),'test.png')

@pytest.mark.parametrize('value',['=CMD()','+1+1','-1+1','@SUM(A1)','  =2+2'])
def test_csv_formulas_are_neutralized(value):assert _csv_cell(value).startswith("'")

@pytest.mark.parametrize('name,content',[('fake.png',b'fake'),('fake.webp',b'RIFF1234WAVE'),('file.exe',b'MZ')])
def test_rejects_forged_images(name,content):
    with pytest.raises(HTTPException):asyncio.run(read_image(UploadFile(filename=name,file=BytesIO(content)),500))

def test_image_read_is_bounded():
    class ReadSpy:
        filename='image.png'
        async def read(self,n):assert n==101;return b'x'*n
    with pytest.raises(HTTPException) as e:asyncio.run(read_image(ReadSpy(),100))
    assert e.value.status_code==413

def test_notifications_sent_only_after_commit(monkeypatch):
    from app.db import session as module
    from app.routers.ws import manager
    order=[]
    class Session:
        info={}
        async def __aenter__(self):self.info={};return self
        async def __aexit__(self,*a):pass
        async def commit(self):order.append('commit')
        async def rollback(self):order.append('rollback')
    async def send(uid,data):order.append('send')
    monkeypatch.setattr(module,'AsyncSessionLocal',Session)
    monkeypatch.setattr(manager,'send_notification',send)
    async def run():
        gen=module.get_db();s=await anext(gen)
        module.queue_notification(s,'user',{'message':'teste'})
        assert order==[]
        with pytest.raises(StopAsyncIteration):await anext(gen)
    asyncio.run(run());assert order==['commit','send']


def test_rollback_does_not_send_notification(monkeypatch):
    from app.db import session as module
    from app.routers.ws import manager
    order=[]
    class Session:
        async def __aenter__(self):self.info={};return self
        async def __aexit__(self,*a):pass
        async def commit(self):raise ValueError('simulated commit failure')
        async def rollback(self):order.append('rollback')
    async def send(uid,data):order.append('send')
    monkeypatch.setattr(module,'AsyncSessionLocal',Session)
    monkeypatch.setattr(manager,'send_notification',send)
    async def run():
        gen=module.get_db();s=await anext(gen);module.queue_notification(s,'user',{})
        with pytest.raises(ValueError):await anext(gen)
    asyncio.run(run());assert order==['rollback']


def test_live_notification_manager_removes_dead_connections():
    from app.routers.ws import ConnectionManager
    messages=[]
    class Socket:
        def __init__(self,dead=False):self.dead=dead
        async def accept(self):pass
        async def send_text(self,data):
            if self.dead:raise RuntimeError('disconnected')
            messages.append(data)
    async def run():
        manager=ConnectionManager();good=Socket();bad=Socket(True)
        await manager.connect('user',good);await manager.connect('user',bad)
        await manager.send_notification('user',{'type':'checklist_submitted'})
        assert manager._connections['user']==[good]
        manager.disconnect('user',good);assert manager._connections=={}
    asyncio.run(run());assert len(messages)==1
