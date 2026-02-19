from __future__ import annotations

from collections import Counter

from app.store.memory_store import store


def get_dashboard_stats() -> dict:
    # Articles by category
    cat_counts: Counter = Counter()
    age_counts: Counter = Counter()
    cond_counts: Counter = Counter()
    for art in store.articles.values():
        cat_counts[art.category.value] += 1
        age_counts[art.age_range.value] += 1
        cond_counts[art.condition.value] += 1

    # Active subscribers
    active_subscribers = len(store.subscribers)

    # Subscribers by age range
    sub_age_counts: Counter = Counter()
    for sub in store.subscribers.values():
        sub_age_counts[sub.child_age_range.value] += 1

    # Average score of recent campaigns
    validated_boxes = [b for b in store.boxes if b.validated]
    avg_score = 0.0
    if validated_boxes:
        avg_score = sum(b.score for b in validated_boxes) / len(validated_boxes)

    return {
        "articles_by_category": dict(cat_counts),
        "articles_by_age_range": dict(age_counts),
        "articles_by_condition": dict(cond_counts),
        "total_articles": len(store.articles),
        "active_subscribers": active_subscribers,
        "subscribers_by_age_range": dict(sub_age_counts),
        "average_box_score": round(avg_score, 2),
        "total_validated_boxes": len(validated_boxes),
    }
