from __future__ import annotations
from collections import Counter
from app.models.article import Article
from app.models.subscriber import Subscriber
from app.models.box import Box

def get_dashboard_stats() -> dict:
    # 1. Récupération de toutes les données nécessaires depuis la DB
    all_articles = Article.query.all()
    all_subscribers = Subscriber.query.all()
    validated_boxes = Box.query.filter_by(validated=True).all()

    # 2. Statistiques des Articles
    cat_counts: Counter = Counter()
    age_counts: Counter = Counter()
    cond_counts: Counter = Counter()
    for art in all_articles:
        cat_counts[art.category] += 1
        age_counts[art.age_range] += 1
        cond_counts[art.condition] += 1

    # 3. Statistiques des Abonnés
    sub_age_counts: Counter = Counter()
    for sub in all_subscribers:
        sub_age_counts[sub.child_age_range] += 1

    # 4. Score moyen des campagnes récentes
    avg_score = 0.0
    if validated_boxes:
        avg_score = sum(b.score for b in validated_boxes) / len(validated_boxes)

    return {
        "articles_by_category": dict(cat_counts),
        "articles_by_age_range": dict(age_counts),
        "articles_by_condition": dict(cond_counts),
        "total_articles": len(all_articles),
        "active_subscribers": len(all_subscribers),
        "subscribers_by_age_range": dict(sub_age_counts),
        "average_box_score": round(avg_score, 2),
        "total_validated_boxes": len(validated_boxes),
    }