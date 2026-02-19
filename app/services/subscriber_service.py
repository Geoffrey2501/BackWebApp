from __future__ import annotations

from app import db
from app.models.article import AgeRange, Category
from app.models.subscriber import Subscriber


def register_subscriber(
        first_name: str,
        last_name: str,
        email: str,
        child_age_range: AgeRange,
        category_preferences: list[Category],
) -> Subscriber:
    # 1. Vérifier si l'abonné existe déjà par son email
    existing = find_by_email(email)
    if existing:
        existing.first_name = first_name
        existing.last_name = last_name
        existing.child_age_range = child_age_range
        existing.category_preferences = category_preferences
        db.session.commit()
        return existing

    # 2. Calculer le prochain ID (ex: s1, s2...)
    count = Subscriber.query.count()
    new_id = f"s{count + 1}"

    # 3. Créer le nouvel abonné
    subscriber = Subscriber(
        id=new_id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        child_age_range=child_age_range,
        category_preferences=category_preferences,
    )

    db.session.add(subscriber)
    db.session.commit()
    return subscriber


def find_by_email(email: str) -> Subscriber | None:
    # Recherche directement en base de données
    return Subscriber.query.filter_by(email=email).first()


def list_subscribers() -> list[Subscriber]:
    # Récupère tous les abonnés
    return Subscriber.query.all()


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

    db.session.commit()
    return sub
