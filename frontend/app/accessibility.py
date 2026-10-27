"""Acessibilidade por sessão, sem alterar banco, credenciais ou armazenamento."""
from dataclasses import fields, is_dataclass
import flet as ft


def walk_controls(root):
    """Percorre os campos públicos dos controles, incluindo views e diálogos."""
    seen = set()
    def visit(value):
        if isinstance(value, ft.BaseControl):
            if id(value) in seen:
                return
            seen.add(id(value))
            yield value
            if is_dataclass(value):
                for field in fields(value):
                    if (not field.name.startswith('_') or field.name == '_dialogs') and field.name not in ('data', 'services'):
                        yield from visit(getattr(value, field.name, None))
        elif isinstance(value, (list, tuple)):
            for item in value:
                yield from visit(item)
        elif isinstance(value, dict):
            for item in value.values():
                yield from visit(item)
    yield from visit(root)


def apply_text_size(root, scale=1.0):
    """Amplia sempre a partir do tamanho base; atualizações não acumulam zoom."""
    scale = max(1.0, min(2.0, float(scale)))
    for control in walk_controls(root):
        if isinstance(control, ft.Text):
            # Subtítulos brancos translúcidos perdiam contraste sobre o vermelho.
            if isinstance(control.color, str) and control.color.startswith('white,'):
                control.color = '#FFFFFF'
            if not hasattr(control, '_a11y_base_size'):
                control._a11y_base_size = max(14, control.size or 14)
            control.size = control._a11y_base_size * scale
            control.no_wrap = False
            control.max_lines = None
            control.overflow = ft.TextOverflow.VISIBLE
        elif isinstance(control, (ft.TextField, ft.Dropdown)):
            if not hasattr(control, '_a11y_base_size'):
                control._a11y_base_size = max(16, control.text_size or 16)
            control.text_size = control._a11y_base_size * scale
            if isinstance(control, ft.TextField):
                control.label_style = ft.TextStyle(size=14 * scale)
                control.hint_style = ft.TextStyle(size=16 * scale)
                control.error_style = ft.TextStyle(size=14 * scale)
        elif isinstance(control, (ft.FilledButton, ft.OutlinedButton, ft.TextButton)):
            if control.style is None:
                control.style = ft.ButtonStyle()
            control.style.text_style = ft.TextStyle(size=16 * scale)
            # Altura fixa pode recortar os rótulos quando a fonte aumenta.
            control.height = None


def show_accessibility(page):
    percent = ft.Text(f'{round(page._a11y_scale * 100)}%')
    def change(event):
        page._a11y_scale = max(1.0, min(2.0, float(event.control.value) / 100))
        percent.value = f'{round(page._a11y_scale * 100)}%'
        page.update()
    slider = ft.Slider(min=100, max=200, divisions=4, value=page._a11y_scale * 100,
                       label='{value}%', on_change=change)
    def reset(event):
        page._a11y_scale = 1.0
        slider.value = 100
        percent.value = '100%'
        page.update()
    def close(event):
        dialog.open = False
        page.update()
    dialog = ft.AlertDialog(
        title=ft.Text('Acessibilidade', size=20), scrollable=True,
        content=ft.Column([
            ft.Text('Tamanho do texto de 100% a 200%. A preferência vale nesta sessão.'),
            percent,
            ft.Semantics(content=slider, label='Aumentar o tamanho do texto de 100 a 200 por cento'),
            ft.Text('Você também pode usar o zoom do navegador. As situações do checklist têm rótulos além das cores.'),
            ft.Column([
                ft.TextButton('Restaurar 100%', on_click=reset, width=float('inf')),
                ft.TextButton('Fechar', on_click=close, width=float('inf')),
            ], tight=True, spacing=8),
        ], tight=True, spacing=12, width=max(180, min(440, (page.width or 360) - 96))),
    )
    page.show_dialog(dialog)


def configure_accessibility(page):
    """Hook público do Flet: inclui também conteúdo carregado após a navegação."""
    page._a11y_scale = 1.0
    previous = getattr(page, 'before_update', lambda: None)
    def before_update():
        previous()
        for view in page.views:
            if not getattr(view, '_a11y_menu_added', False):
                button = ft.IconButton(ft.Icons.ACCESSIBILITY_NEW,
                                       tooltip='Acessibilidade e tamanho do texto',
                                       icon_color='#FFFFFF',
                                       on_click=lambda event: show_accessibility(page))
                if view.appbar is None:
                    view.appbar = ft.AppBar(bgcolor='#C62828', toolbar_height=48,
                                           automatically_imply_leading=False, actions=[button])
                else:
                    view.appbar.actions = [*(view.appbar.actions or []), button]
                view._a11y_menu_added = True
            if view.appbar is not None:
                if not hasattr(view.appbar, '_a11y_base_height'):
                    view.appbar._a11y_base_height = view.appbar.toolbar_height or 64
                view.appbar.toolbar_height = view.appbar._a11y_base_height * page._a11y_scale
        apply_text_size(page, page._a11y_scale)
    page.before_update = before_update
