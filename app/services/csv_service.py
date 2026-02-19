"""Import/export CSV for the web app, bridging to optimizer format."""

from __future__ import annotations

from app.store.memory_store import store


def export_optimizer_input(max_weight: int) -> str:
    """Generate CSV input string for the optimizer from current store data."""
    lines = ["articles"]
    for art in store.articles.values():
        lines.append(
            f"{art.id};{art.designation};{art.category.value};"
            f"{art.age_range.value};{art.condition.value};{art.price};{art.weight}"
        )
    lines.append("")
    lines.append("abonnes")
    for sub in store.subscribers.values():
        prefs = ",".join(c.value for c in sub.category_preferences)
        lines.append(f"{sub.id};{sub.first_name};{sub.child_age_range.value};{prefs}")
    lines.append("")
    lines.append("parametres")
    lines.append(str(max_weight))
    return "\n".join(lines)
