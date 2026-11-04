"""Acessibilidade por sessão, sem alterar banco, credenciais ou armazenamento."""
from dataclasses import fields, is_dataclass
import flet as ft

from app import a11y


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


def configure_accessibility(page):
    """Hook público do Flet: inclui também conteúdo carregado após a navegação."""
    previous = getattr(page, 'before_update', lambda: None)
    def before_update():
        previous()
        scale = a11y.font_scale(page)
        a11y.decorate_views(page)
        for view in page.views:
            if view.appbar is not None:
                if not hasattr(view.appbar, '_a11y_base_height'):
                    view.appbar._a11y_base_height = view.appbar.toolbar_height or 64
                view.appbar.toolbar_height = view.appbar._a11y_base_height * scale
        apply_text_size([page, *page.views], scale)
    page.before_update = before_update
