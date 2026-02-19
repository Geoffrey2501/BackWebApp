from __future__ import annotations

from app.models.article import AgeRange, Article, Category, Condition
from app.store.memory_store import store


def add_article(
    designation: str,
    category: Category,
    age_range: AgeRange,
    condition: Condition,
    price: int,
    weight: int,
) -> Article:
    aid = store.next_article_id()
    article = Article(
        id=aid,
        designation=designation,
        category=category,
        age_range=age_range,
        condition=condition,
        price=price,
        weight=weight,
    )
    store.articles[aid] = article
    return article


def get_article(article_id: str) -> Article | None:
    return store.articles.get(article_id)


def list_articles(
    category: str | None = None,
    age_range: str | None = None,
    condition: str | None = None,
) -> list[Article]:
    result = list(store.articles.values())
    if category:
        result = [a for a in result if a.category.value == category]
    if age_range:
        result = [a for a in result if a.age_range.value == age_range]
    if condition:
        result = [a for a in result if a.condition.value == condition]
    return result


def update_article(
    article_id: str, **fields: object
) -> tuple[Article | None, str | None]:
    article = store.articles.get(article_id)
    if article is None:
        return None, "Article non trouvé"

    if article_id in store.validated_article_campaigns:
        return None, "Article dans une box validée, modification interdite"

    for key, value in fields.items():
        if value is not None and hasattr(article, key):
            setattr(article, key, value)
    return article, None


def is_article_locked(article_id: str) -> bool:
    return article_id in store.validated_article_campaigns
