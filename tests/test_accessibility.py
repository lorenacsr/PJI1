"""Contratos de acessibilidade; não substituem teste com leitor de tela."""
import ast
import unittest
from pathlib import Path
import flet as ft
from app.accessibility import apply_text_size, configure_accessibility
from app import theme


def contrast(a, b):
    def luminance(value):
        rgb = [int(value[i:i+2],16)/255 for i in (1,3,5)]
        linear = [v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4 for v in rgb]
        return sum(v*w for v,w in zip(linear,(0.2126,0.7152,0.0722)))
    x,y=sorted((luminance(a),luminance(b)))
    return (y+0.05)/(x+0.05)


class Accessibility(unittest.TestCase):
    def test_core_palette_has_text_contrast(self):
        for color in [theme.PRIMARY,theme.SECONDARY,theme.ERROR,*theme.STATUS_COLORS.values(),*theme.DEPT_COLORS.values()]:
            self.assertGreaterEqual(contrast(color,'#FFFFFF'),4.5,color)
        for color in [theme.ON_SURFACE,theme.ON_SURFACE_VARIANT]:
            self.assertGreaterEqual(contrast(color,theme.BG),4.5)

    def test_scale_is_idempotent_and_covers_inputs(self):
        text=ft.Text('Tarefa longa',size=10,max_lines=1,no_wrap=True)
        field=ft.TextField(label='E-mail')
        button=ft.FilledButton('Enviar',height=40)
        view=ft.View(controls=[ft.Column([text,field,button])])
        for _ in range(3):apply_text_size(view,2)
        self.assertEqual(text.size,28)
        self.assertEqual(field.text_size,32)
        self.assertEqual(button.style.text_style.size,32)
        self.assertIsNone(text.max_lines)
        self.assertFalse(text.no_wrap)
        self.assertIsNone(button.height)
        apply_text_size(view,1)
        self.assertEqual(text.size,14)

    def test_menu_is_added_once_and_scale_is_per_session(self):
        class Page:
            def __init__(self):self.views=[ft.View(controls=[ft.Text('Olá')])]
        a,b=Page(),Page()
        configure_accessibility(a);configure_accessibility(b)
        a._a11y_scale=2
        a.before_update();a.before_update();b.before_update()
        self.assertEqual(len(a.views[0].appbar.actions),1)
        self.assertEqual(b._a11y_scale,1)

    def test_every_image_has_explicit_description(self):
        root=Path(__file__).resolve().parents[1]/'frontend'
        count=0
        for path in root.rglob('*.py'):
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='Image':
                    count+=1
                    self.assertIn('semantics_label',{k.arg for k in node.keywords},str(path))
        self.assertGreaterEqual(count,11)


if __name__=='__main__':unittest.main(verbosity=2)
