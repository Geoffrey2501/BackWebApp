"""Bridge between Flask web app and the optimizer module."""

from __future__ import annotations

from app.models.article import Article
from app.models.box import Box
from app.models.subscriber import Subscriber
from optimizer.greedy import optimize
from optimizer.models import OptArticle, OptSubscriber
from optimizer.scorer import score_composition, score_subscriber_box


def _to_opt_article(a: Article) -> OptArticle:
    # Suppression de .value car les champs sont déjà des chaînes en DB
    return OptArticle(
        id=a.id,
        designation=a.designation,
        category=a.category,
        age_range=a.age_range,
        condition=a.condition,
        price=a.price,
        weight=a.weight,
    )


def _to_opt_subscriber(s: Subscriber) -> OptSubscriber:
    # child_age_range est une String et category_preferences est une liste de Strings
    return OptSubscriber(
        id=s.id,
        name=s.first_name,
        age_range=s.child_age_range,
        preferences=s.category_preferences,
    )


def run_optimization(
    articles: list[Article],
    subscribers: list[Subscriber],
    max_weight: int,
) -> list[Box]:
    """Run optimizer and return Box objects for the campaign."""
    opt_articles = [_to_opt_article(a) for a in articles]
    opt_subscribers = [_to_opt_subscriber(s) for s in subscribers]

    composition = optimize(opt_articles, opt_subscribers, max_weight)
    score_composition(composition, opt_subscribers, max_weight)

    boxes: list[Box] = []
    for sub in subscribers:
        assignment = composition.assignments.get(sub.id)
        arts = assignment.articles if assignment else []

        opt_sub = _to_opt_subscriber(sub)
        box_score = score_subscriber_box(opt_sub, arts)

        # Création de l'objet Box sans ID (MySQL le gérera)
        box = Box(
            campaign_id="",  # Défini par l'appelant dans campaign_service
            subscriber_id=sub.id,
            article_ids=[a.id for a in arts],
            score=box_score,
            total_weight=sum(a.weight for a in arts),
            total_price=sum(a.price for a in arts),
        )
        boxes.append(box)

    return boxes