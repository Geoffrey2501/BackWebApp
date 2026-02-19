from __future__ import annotations

from app.models.box import Box
from app.store.memory_store import store


def get_validated_box(subscriber_id: str) -> Box | None:
    for box in store.boxes:
        if box.subscriber_id == subscriber_id and box.validated:
            return box
    return None


def box_detail(box: Box) -> dict:
    data = box.to_dict()
    data["articles"] = []
    for art_id in box.article_ids:
        art = store.articles.get(art_id)
        if art:
            data["articles"].append(art.to_dict())
    sub = store.subscribers.get(box.subscriber_id)
    if sub:
        data["subscriber_name"] = f"{sub.first_name} {sub.last_name}"
    return data


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
