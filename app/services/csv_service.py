"""Import/export CSV for the web app, bridging to optimizer format."""

from __future__ import annotations

from app.models.article import Article
from app.models.subscriber import Subscriber


def export_optimizer_input(max_weight: int) -> str:
    """Generate CSV input string for the optimizer from current database data."""
    lines = ["articles"]

    # Récupération de tous les articles en base de données
    articles = Article.query.all()
    for art in articles:
        # .value si Enum, sinon attribut direct (String en base)
        lines.append(
            f"{art.id};{art.designation};{art.category};"
            f"{art.age_range};{art.condition};{art.price};{art.weight}"
        )

    lines.append("")
    lines.append("abonnes")

    # Récupération de tous les abonnés en base de données
    subscribers = Subscriber.query.all()
    for sub in subscribers:
        # category_preferences est stocké en JSON (liste) dans la base de données
        prefs = ",".join(sub.category_preferences)
        lines.append(f"{sub.id};{sub.first_name};{sub.child_age_range};{prefs}")

    lines.append("")
    lines.append("parametres")
    lines.append(str(max_weight))

    return "\n".join(lines)
