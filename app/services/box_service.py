from __future__ import annotations
from app.models.box import Box, BoxHistoryEntry
from app.models.article import Article
from app.models.subscriber import Subscriber


def get_validated_box(subscriber_id: str) -> list[Box]:
    # Récupère toutes les box validées pour cet abonné
    return Box.query.filter_by(subscriber_id=subscriber_id, validated=True).all()


def get_boxes_details(boxes: list[Box]) -> list[dict]:
    """
    Prend une liste d'objets Box et retourne une liste de dictionnaires
    enrichis avec le détail des articles et le nom de l'abonné depuis la DB.
    """
    result = []
    for box in boxes:
        data = box.to_dict()
        data["articles"] = []

        # Récupération des détails de chaque article en DB
        for art_id in box.article_ids:
            art = Article.query.get(art_id)
            if art:
                data["articles"].append(art.to_dict())

        # Récupération du nom de l'abonné
        sub = Subscriber.query.get(box.subscriber_id)
        if sub:
            data["subscriber_name"] = f"{sub.first_name} {sub.last_name}"

        result.append(data)

    return result


def get_subscriber_history(subscriber_id: str) -> list[dict]:
    # Récupère l'historique figé depuis la table box_history
    entries = BoxHistoryEntry.query.filter_by(subscriber_id=subscriber_id).all()

    result = []
    for entry in entries:
        d = entry.to_dict()
        d["articles"] = []
        # On enrichit avec les détails actuels des articles pour l'affichage
        for art_id in entry.article_ids:
            art = Article.query.get(art_id)
            if art:
                d["articles"].append(art.to_dict())
        result.append(d)
    return result