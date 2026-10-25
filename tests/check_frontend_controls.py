"""Construct real Flet 0.84 controls with API adapters; not a browser/usability test.
Run separately from backend tests because both apps use the package name `app`.
"""
import asyncio
from contextlib import ExitStack
from unittest.mock import patch
from types import SimpleNamespace
import inspect
import flet as ft
from app.state import AppState
from app.api_client import APIClient
from app.pages.login_page import build_login_view
from app.pages.employee.home_page import build_employee_view
from app.pages.employee.checklist_page import build_checklist_view
from app.pages.manager.dashboard_page import build_manager_view
from app.pages.manager.review_page import build_review_view
from app.pages.manager.new_user_page import build_new_user_view
from app.pages.manager.templates_page import build_templates_content
from app.pages.notifications_page import build_notifications_view
from app.pages.onboarding.setup_page import build_setup_view
from app.pages.terms_page import build_terms_view
from app import theme

class Page:
    def __init__(self,width):
        self.width=width;self.height=800;self.overlay=[];self.services=[];self.dialogs=[]
        self.window=SimpleNamespace(width=width,height=800)
        self.client_storage=SimpleNamespace(get=lambda key:None,set=lambda *a:None,remove=lambda *a:None)
    def update(self):pass
    async def push_route(self,route):pass
    def show_dialog(self,dialog):self.dialogs.append(dialog)

async def run():
    failures=[];errors=[]
    loop=asyncio.get_running_loop();loop.set_exception_handler(lambda loop,ctx:errors.append(str(ctx.get('exception') or ctx)))
    data={'id':'00000000-0000-0000-0000-000000000001','template_id':1,'date':'2026-10-25','status':'IN_PROGRESS','employee_name':'Funcionário teste','items':[{'id':'00000000-0000-0000-0000-000000000002','status':'DONE','photo_url':'/uploads/test.png','notes':'Teste','item_template':{'id':1,'title':'Conferir limpeza','requires_photo':True,'order_index':0}}], 'template':{'id':1,'name':'Teste','phase':'ENTRADA'},'progress':0}
    async def reply(self,*a,**kw):
        method=kw.pop('_method','')
        if method=='get_checklist':return dict(data)
        if method=='get_pending_review':return [dict(data,status='SUBMITTED')]
        if method=='get_all_checklists':return [dict(data,status='APPROVED')]
        if method=='get_my_checklists':return [dict(data)]
        if method in ('get_today_stats','get_my_stats','get_my_streak'):return {}
        return []
    with ExitStack() as stack:
        for name,method in inspect.getmembers(APIClient,inspect.iscoroutinefunction):
            if name.startswith('_'):continue
            async def mocked(self,*a,_method=name,**kw):return await reply(self,*a,_method=_method,**kw)
            stack.enter_context(patch.object(APIClient,name,mocked))
        for width in (360,1366):
            state=AppState();state.token='fake';state.user={'id':data['id'],'name':'Gestor teste','email':'test@example.org','role':'manager','department_id':1}
            builders=[(build_login_view,()),(build_employee_view,()),(build_checklist_view,(data['id'],)),(build_manager_view,()),(build_review_view,(data['id'],)),(build_new_user_view,()),(build_templates_content,()),(build_notifications_view,()),(build_setup_view,())]
            for builder,args in builders:
                page=Page(width)
                try:
                    result=builder(page,state,*args)
                    assert isinstance(result[0] if isinstance(result,tuple) else result,ft.Control)
                    await asyncio.sleep(.03)
                    print('OK',width,builder.__name__)
                except Exception as e:
                    failures.append((width,builder.__name__,repr(e)));print('FAIL',failures[-1])
                for task in asyncio.all_tasks():
                    if task is not asyncio.current_task():task.cancel()
                await asyncio.sleep(0)
            try:
                build_terms_view(Page(width),'/login');theme.show_edit_profile_dialog(Page(width),APIClient(state),state);theme.show_password_change_dialog(Page(width),APIClient(state))
                print('OK',width,'terms/profile/password')
            except Exception as e:failures.append((width,'dialogs',repr(e)))
    print('FAILURES',failures);print('ASYNC_ERRORS',errors)
    assert not failures and not errors

if __name__=='__main__':asyncio.run(run())
