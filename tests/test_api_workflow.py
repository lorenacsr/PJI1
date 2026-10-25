"""HTTP + ORM integration with disposable SQLite; PostgreSQL validation is separate.

Run: PYTHONPATH=backend .venv-audit/bin/python -m pytest tests/test_api_workflow.py -v
No production DATABASE_URL is used, and no real user records are read.
"""
import asyncio
from datetime import date
from io import BytesIO
import uuid
import pytest
from PIL import Image
from httpx import AsyncClient, ASGITransport
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.main import app
from app.db.session import Base, get_db
from app.models.user import User, UserRole
from app.models.department import Department
from app.core.security import get_password_hash, create_access_token
from app.core.config import settings


@pytest.fixture
def scenario(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, 'UPLOAD_DIR', str(tmp_path/'uploads'))
    async def run(check):
        engine = create_async_engine('sqlite+aiosqlite:///'+str(tmp_path/'test.sqlite'))
        @event.listens_for(engine.sync_engine, 'connect')
        def fk(dbapi, record): dbapi.execute('PRAGMA foreign_keys=ON')
        factory=async_sessionmaker(engine, expire_on_commit=False)
        async with engine.begin() as conn: await conn.run_sync(Base.metadata.create_all)
        async with factory() as s:
            d=Department(name='TEST', display_name='Setor de teste'); s.add(d); await s.flush()
            accounts={}
            for name,role,dept in [('admin',UserRole.admin,None),('manager',UserRole.manager,None),('employee',UserRole.employee,d.id),('other',UserRole.employee,d.id),('unassigned',UserRole.employee,None)]:
                u=User(name=name, email=name+'@example.org', hashed_password=get_password_hash('Senha-Teste-123'),role=role,department_id=dept)
                s.add(u);await s.flush();accounts[name]=u.id
            await s.commit(); department_id=d.id
        async def override():
            async with factory() as s:
                try:
                    yield s
                    await s.commit()
                    from app.routers.ws import manager
                    for uid,data in s.info.pop('notifications_after_commit',[]): await manager.send_notification(uid,data)
                except Exception:
                    await s.rollback();raise
        app.dependency_overrides[get_db]=override
        try:
            async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as c:
                def headers(name):return {'Authorization':'Bearer '+create_access_token(accounts[name])}
                async def req(method,path,name='employee',**kw):
                    return await c.request(method,'/api/v1'+path,headers=headers(name),**kw)
                await check(c,req,accounts,department_id,factory)
        finally:
            app.dependency_overrides.clear();await engine.dispose()
    return lambda check: asyncio.run(run(check))


def image_bytes():
    buf=BytesIO();Image.new('RGB',(8,8),'red').save(buf,format='PNG');return buf.getvalue()


async def new_checklist(req,dept):
    r=await req('POST','/checklists/templates','manager',json={'name':'Turno teste','department_id':dept,'phase':'FECHAMENTO'}); assert r.status_code==201,r.text
    tid=r.json()['id']
    for name,photo in [('Conferir bancada',False),('Foto da bancada',True)]:
        r=await req('POST',f'/checklists/templates/{tid}/items','manager',json={'title':name,'requires_photo':photo});assert r.status_code==200,r.text
    assert len(r.json()['items'])==2
    r=await req('POST','/checklists/',json={'template_id':tid,'date':date.today().isoformat()});assert r.status_code==201,r.text
    return tid,r.json()


def test_complete_workflow(scenario):
    async def check(c,req,accounts,dept,factory):
        login=await c.post('/api/v1/auth/login',json={'email':'EMPLOYEE@example.org','password':'Senha-Teste-123'});assert login.status_code==200,login.text
        tid,cl=await new_checklist(req,dept);cid=cl['id'];first,photo=cl['items']
        assert (await req('POST','/checklists/',json={'template_id':tid,'date':date.today().isoformat()})).status_code==400
        assert (await req('GET',f'/checklists/{cid}','other')).status_code==403
        assert (await req('PATCH',f'/checklists/{cid}/items/{first["id"]}','other',json={'status':'DONE'})).status_code==403
        assert (await req('POST',f'/checklists/{cid}/submit')).status_code==400
        assert (await req('PATCH',f'/checklists/{cid}/items/{first["id"]}',json={'status':'DONE','notes':'=1+1'})).status_code==200
        assert (await req('PATCH',f'/checklists/{cid}/items/{photo["id"]}',json={'status':'DONE'})).status_code==200
        assert (await req('POST',f'/checklists/{cid}/submit')).status_code==400
        assert (await req('POST',f'/checklists/{cid}/items/{photo["id"]}/photo',files={'file':('fake.png',b'not an image','image/png')})).status_code==400
        r=await req('POST',f'/checklists/{cid}/items/{photo["id"]}/photo',files={'file':('real.png',image_bytes(),'image/png')});assert r.status_code==200,r.text
        photo_url=r.json()['items'][1]['photo_url']
        assert (await c.get(photo_url)).status_code==200
        assert (await c.get(photo_url.split('?')[0])).status_code==403
        assert (await req('POST',f'/checklists/{cid}/submit')).status_code==200
        assert (await req('PATCH' ,f'/checklists/{cid}/items/{first["id"]}',json={'status':'PENDING'})).status_code==400
        pending=await req('GET','/checklists/pending-review','manager');assert len(pending.json())==1
        assert (await req('POST',f'/checklists/{cid}/review',json={'status':'APPROVED'})).status_code==403
        assert (await req('POST',f'/checklists/{cid}/review','manager',json={'status':'REJECTED'})).status_code==422
        assert (await req('POST',f'/checklists/{cid}/review','manager',json={'status':'REJECTED','notes':'Corrigir foto'})).status_code==200
        r=await req('POST',f'/checklists/{cid}/reopen');assert r.status_code==200,r.text
        assert r.json()['reviewed_at'] is None and r.json()['reviewer_id'] is None
        assert (await req('POST',f'/checklists/{cid}/submit')).status_code==200
        r=await req('POST',f'/checklists/{cid}/review','manager',json={'status':'APPROVED'});assert r.status_code==200,r.text
        assert r.json()['reviewer_id']==str(accounts['manager'])
        assert (await req('POST',f'/checklists/{cid}/reopen')).status_code==400
        assert (await req('GET','/checklists/notifications/me')).json()
        assert (await req('POST','/checklists/notifications/read-all')).status_code==200
        assert all(n['is_read'] for n in (await req('GET','/checklists/notifications/me')).json())
        assert (await req('PATCH',f'/checklists/templates/{tid}','manager',json={'name':'Alterar histórico'})).status_code==409
        assert (await req('GET','/checklists/export','manager')).status_code==200
        for route in ['today','team','daily','items','departments','today/missing-employees','me','me/streak']:
            actor='employee' if route.startswith('me') else 'manager'
            r=await req('GET','/checklists/stats/'+route,actor);assert r.status_code==200,(route,r.text)
    scenario(check)


@pytest.mark.parametrize('status',['IN_PROGRESS','SUBMITTED','other'])
def test_review_rejects_invalid_states(scenario,status):
    async def check(c,req,accounts,dept,factory):
        r=await req('POST',f'/checklists/{uuid.uuid4()}/review','manager',json={'status':status});assert r.status_code==422,r.text
    scenario(check)


@pytest.mark.parametrize('status',['APPROVED','REJECTED','other'])
def test_employee_cannot_assign_review_states(scenario,status):
    async def check(c,req,accounts,dept,factory):
        r=await req('PATCH',f'/checklists/{uuid.uuid4()}/items/{uuid.uuid4()}',json={'status':status});assert r.status_code==422,r.text
    scenario(check)


def test_permissions_and_account_changes(scenario):
    async def check(c,req,accounts,dept,factory):
        assert (await c.get('/api/v1/auth/me')).status_code in (401,403)
        bad={'Authorization':'Bearer '+create_access_token('invalid-uuid')}
        assert (await c.get('/api/v1/auth/me',headers=bad)).status_code==401
        assert (await req('GET','/users/')).status_code==403
        assert (await req('POST','/users/','manager',json={'name':'Escala indevida','email':'escalation@example.org','password':'Senha-Teste-123','role':'admin'})).status_code==403
        assert (await req('GET','/checklists/export')).status_code==403
        assert (await req('GET','/checklists/templates','unassigned')).json()==[]
        r=await req('POST','/users/','admin',json={'name':'Novo funcionário','email':'new@example.org','password':'Nova-Senha-123','department_id':dept});assert r.status_code==201,r.text
        r=await req('PATCH','/auth/me',json={'name':'Nome atualizado'});assert r.status_code==200,r.text
        assert (await req('POST','/auth/change-password',json={'current_password':'errada','new_password':'Nova-Senha-123'})).status_code==400
        assert (await req('POST','/auth/change-password',json={'current_password':'Senha-Teste-123','new_password':'Nova-Senha-123'})).status_code==200
        assert (await c.post('/api/v1/auth/login',json={'email':'employee@example.org','password':'Nova-Senha-123'})).status_code==200
    scenario(check)


def test_template_department_crud(scenario):
    async def check(c,req,accounts,dept,factory):
        r=await req('POST','/checklists/departments','admin',json={'display_name':'Setor novo'});assert r.status_code==201,r.text
        did=r.json()['id']
        assert (await req('POST','/checklists/departments','admin',json={'display_name':'Setor novo'})).status_code==409
        r=await req('PATCH',f'/checklists/departments/{did}','admin',json={'display_name':'Setor editado'});assert r.status_code==200,r.text
        r=await req('POST','/checklists/templates','manager',json={'name':'Modelo novo','department_id':did,'phase':'ENTRADA'});assert r.status_code==201,r.text
        tid=r.json()['id']
        r=await req('POST',f'/checklists/templates/{tid}/items','manager',json={'title':'Item novo'});assert r.status_code==200,r.text
        iid=r.json()['items'][0]['id']
        r=await req('PATCH',f'/checklists/templates/{tid}/items/{iid}','manager',json={'title':'Item alterado','requires_photo':True});assert r.status_code==200,r.text
        assert r.json()['items'][0]['title']=='Item alterado'
        r=await req('DELETE',f'/checklists/templates/{tid}/items/{iid}','manager');assert r.status_code==200,r.text
        assert r.json()['items']==[]
        assert (await req('POST',f'/checklists/templates/{tid}/items','manager',json={'title':'Item final'})).status_code==200
        assert (await req('DELETE',f'/checklists/departments/{did}','admin')).status_code==409
        r=await req('DELETE',f'/checklists/templates/{tid}','manager');assert r.status_code==204,r.text
        assert (await req('DELETE',f'/checklists/departments/{did}','admin')).status_code==204
        assert (await req('DELETE',f'/checklists/departments/{dept}','admin')).status_code==409
    scenario(check)
