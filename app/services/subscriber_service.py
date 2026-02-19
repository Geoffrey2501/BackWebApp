from __future__ import annotations

from app.models.article import AgeRange, Category
from app.models.subscriber import Subscriber

def register_subscriber(
    first_name: str,
    last_name: str,
    email: str,
    child_age_range: AgeRange,
    category_preferences: list[Category],
) -> Subscriber:
    existing = find_by_email(email)
    if existing:
        existing.first_name = first_name
        existing.last_name = last_name
        existing.child_age_range = child_age_range
        existing.category_preferences = category_preferences
        return existing

    sid = store.next_subscriber_id()
    subscriber = Subscriber(
        id=sid,
        first_name=first_name,
        last_name=last_name,
        email=email,
        child_age_range=child_age_range,
        category_preferences=category_preferences,
    )
    store.subscribers[sid] = subscriber
    return subscriber


def find_by_email(email: str) -> Subscriber | None:
    for sub in store.subscribers.values():
        if sub.email == email:
            return sub
    return None


def list_subscribers() -> list[Subscriber]:
    return list(store.subscribers.values())


def update_preferences(
    email: str,
    child_age_range: AgeRange | None = None,
    category_preferences: list[Category] | None = None,
) -> Subscriber | None:
    sub = find_by_email(email)
    if sub is None:
        return None
    if child_age_range is not None:
        sub.child_age_range = child_age_range
    if category_preferences is not None:
        sub.category_preferences = category_preferences
    return sub
