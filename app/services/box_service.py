from __future__ import annotations

from app.models.box import Box

def get_validated_box(subscriber_id: str) -> list[Box] | None:
    boxs = []
    for box in store.boxes:
        if box.subscriber_id == subscriber_id and box.validated:
            boxs.append(box)
    return boxs


def get_boxes_details(boxes: list[Box]) -> list[dict]:
    """
    Prend une liste d'objets Box et retourne une liste de dictionnaires
    enrichis avec le détail des articles et le nom de l'abonné.
    """
    result = []
    for box in boxes:
        # On commence par transformer l'objet Box en dictionnaire
        # La méthode to_dict() est définie dans app/models/box.py
        data = box.to_dict()

        # On initialise la liste des articles détaillés
        data["articles"] = []

        # On parcourt les IDs d'articles stockés dans la box
        for art_id in box.article_ids:
            # On récupère l'article complet depuis le store
            art = store.articles.get(art_id)
            if art:
                # On ajoute le dictionnaire de l'article
                data["articles"].append(art.to_dict())

        # On récupère les informations de l'abonné
        sub = store.subscribers.get(box.subscriber_id)
        if sub:
            data["subscriber_name"] = f"{sub.first_name} {sub.last_name}"

        result.append(data)

    return result


def get_subscriber_history(subscriber_id: str) -> list[dict]:
    entries = [
        e for e in store.box_history if e.subscriber_id == subscriber_id
    ]
    result = []
    for entry in entries:
        d = entry.to_dict()
        d["articles"] = []
        for art_id in entry.article_ids:
            art = store.articles.get(art_id)
            if art:
                d["articles"].append(art.to_dict())
        result.append(d)
    return result
