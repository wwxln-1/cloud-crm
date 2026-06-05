"""Template helpers for the generic CRUD templates."""
from django import template

register = template.Library()


@register.filter
def attr(obj, field_name):
    """Resolve a (possibly dotted) attribute; prefer human-readable display."""
    display = getattr(obj, f"get_{field_name}_display", None)
    if callable(display):
        try:
            return display()
        except Exception:
            pass
    value = obj
    for part in field_name.split("."):
        if value is None:
            return ""
        value = getattr(value, part, "")
        if callable(value):
            value = value()
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return value


@register.filter
def badgeclass(value):
    """Map a status/boolean string to a coloured pill class."""
    v = str(value).strip().lower()
    green = {"yes", "active", "won", "delivered", "completed", "received", "confirmed", "incoming"}
    red = {"no", "inactive", "lost", "cancelled"}
    amber = {"pending", "draft", "new", "in transit", "in_transit", "ordered", "contacted", "qualified", "outgoing", "reserved"}
    if v in green:
        return "pill-green"
    if v in red:
        return "pill-red"
    if v in amber:
        return "pill-amber"
    return "pill-slate"
