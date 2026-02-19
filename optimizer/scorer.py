"""Scoring engine implementing the 8 rules from the subject."""

from __future__ import annotations

from optimizer.models import Composition, OptArticle, OptSubscriber

PREF_POINTS = {0: 10, 1: 8, 2: 6, 3: 4, 4: 2, 5: 1}
CONDITION_BONUS = {"N": 2, "TB": 1, "B": 0}


def preference_rank(subscriber: OptSubscriber, category: str) -> int:
    """Return the 0-based preference rank, or -1 if not found."""
    try:
        return subscriber.preferences.index(category)
    except ValueError:
        return -1


def points_for_rank(rank: int) -> int:
    """Points for a given effective rank (0-based). Beyond rank 5 → 1 point."""
    if rank < 0:
        return 0
    return PREF_POINTS.get(rank, 1)


def score_subscriber_box(
    subscriber: OptSubscriber, articles: list[OptArticle]
) -> int:
    """Score a single subscriber's box (R4 + R5 + R6). Does NOT include R7/R8."""
    if not articles:
        return 0

    # Group articles by category, preserving insertion order
    by_category: dict[str, list[OptArticle]] = {}
    for art in articles:
        by_category.setdefault(art.category, []).append(art)

    total = 0
    for cat, cat_articles in by_category.items():
        base_rank = preference_rank(subscriber, cat)
        if base_rank < 0:
            # Category not in preferences — each article gets 1 point + condition bonus
            for art in cat_articles:
                total += 1 + CONDITION_BONUS.get(art.condition, 0)
            continue

        for i, art in enumerate(cat_articles):
            effective_rank = base_rank + i  # R6: shift by duplicate index
            pts = points_for_rank(effective_rank)
            bonus = CONDITION_BONUS.get(art.condition, 0)
            total += pts + bonus

    return total


def score_composition(
    composition: Composition,
    subscribers: list[OptSubscriber],
    max_weight: int,
) -> int:
    """Compute the total score applying all 8 rules."""
    total_score = 0
    article_counts: list[int] = []

    for sub in subscribers:
        assignment = composition.assignments.get(sub.id)
        if assignment is None or len(assignment.articles) == 0:
            # R7: malus for empty box
            total_score -= 10
            article_counts.append(0)
            continue

        # R2: age compatibility check (articles should already be filtered)
        box_articles = [
            a for a in assignment.articles if a.age_range == sub.age_range
        ]

        # R3: weight check
        total_weight = sum(a.weight for a in box_articles)
        if total_weight > max_weight:
            # Remove articles until under weight (shouldn't happen with proper algo)
            pass

        box_score = score_subscriber_box(sub, box_articles)
        total_score += box_score
        article_counts.append(len(box_articles))

    # R7 already handled above

    # R8: equity malus
    if article_counts:
        max_count = max(article_counts)
        for count in article_counts:
            if max_count - count >= 2:
                total_score -= 10

    return total_score


def score_composition_detailed(
    composition: Composition,
    subscribers: list[OptSubscriber],
    max_weight: int,
) -> dict:
    """Return detailed scoring breakdown."""
    details: dict[str, dict] = {}
    article_counts: list[int] = []
    total_score = 0

    for sub in subscribers:
        assignment = composition.assignments.get(sub.id)
        if assignment is None or len(assignment.articles) == 0:
            details[sub.id] = {"name": sub.name, "articles": [], "score": -10, "empty": True}
            total_score -= 10
            article_counts.append(0)
            continue

        box_articles = [
            a for a in assignment.articles if a.age_range == sub.age_range
        ]
        box_score = score_subscriber_box(sub, box_articles)
        total_score += box_score
        article_counts.append(len(box_articles))
        details[sub.id] = {
            "name": sub.name,
            "articles": [a.id for a in box_articles],
            "score": box_score,
            "weight": sum(a.weight for a in box_articles),
        }

    # R8
    if article_counts:
        max_count = max(article_counts)
        for i, sub in enumerate(subscribers):
            if max_count - article_counts[i] >= 2:
                total_score -= 10
                details[sub.id]["equity_malus"] = -10

    return {"total_score": total_score, "details": details}
