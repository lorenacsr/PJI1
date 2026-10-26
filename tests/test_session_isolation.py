"""Regressão da criação de estado por sessão sem servidor ou dados reais."""
import ast
import asyncio
import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class SessionIsolation(unittest.IsolatedAsyncioTestCase):
    async def test_two_pages_have_independent_login_state(self):
        # Executa a função main real com adaptadores leves de página/Flet.
        # Não valida a renderização Flutter nem a API HTTP.
        state_ns = {}
        dotenv = types.SimpleNamespace(load_dotenv=lambda: None)
        with patch.dict(sys.modules, {"dotenv": dotenv}):
            exec(compile((ROOT / "frontend/app/state.py").read_text(), "state.py", "exec"), state_ns)
        AppState = state_ns["AppState"]
        parsed = ast.parse((ROOT / "frontend/main.py").read_text())
        main_node = next(n for n in parsed.body if isinstance(n, ast.AsyncFunctionDef) and n.name == "main")
        observed = []

        class Page:
            def __init__(self):
                self.window = types.SimpleNamespace()
                self.client_storage = types.SimpleNamespace(get=lambda key: None)
                self.services = []
                self.views = []
                self.route = "/login"

            async def push_route(self, route):
                self.route = route

            def update(self):
                pass

        class Preferences:
            async def get(self,key): return None
        ft = types.SimpleNamespace(SharedPreferences=Preferences, Page=Page, ThemeMode=types.SimpleNamespace(LIGHT="light"),
                                   RouteChangeEvent=object, ViewPopEvent=object)

        def login_view(page, state):
            observed.append(state)
            return object()

        namespace = {"ft": ft, "AppState": AppState, "get_theme": lambda: None,
                     "asyncio": asyncio, "_json": json, "build_login_view": login_view}
        module = ast.Module(body=[main_node], type_ignores=[])
        exec(compile(ast.fix_missing_locations(module), "frontend/main.py", "exec"), namespace)
        first, second = Page(), Page()
        await namespace["main"](first)
        await namespace["main"](second)
        await asyncio.sleep(0)
        self.assertEqual(len(observed), 2)
        self.assertIsNot(observed[0], observed[1])
        observed[0].token = "token-ficticio-primeira-sessao"
        observed[0].user = {"name": "Gestor fictício", "role": "manager"}
        observed[0].add_unread_listener(lambda count: None)
        self.assertIsNone(observed[1].token)
        self.assertFalse(observed[1].is_authenticated)
        self.assertFalse(observed[1].is_manager)
        self.assertEqual(observed[1]._unread_listeners, [])
        observed[1].token = "token-ficticio-segunda-sessao"
        observed[0].logout()
        self.assertEqual(observed[1].token, "token-ficticio-segunda-sessao")


if __name__ == "__main__":
    unittest.main(verbosity=2)
