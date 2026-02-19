"""Greedy optimizer for toy box composition."""

from __future__ import annotations

import heapq

from optimizer.models import Assignment, Composition, OptArticle, OptSubscriber
from optimizer.scorer import CONDITION_BONUS, points_for_rank, preference_rank


def _marginal_gain(
    subscriber: OptSubscriber,
    article: OptArticle,
    current_articles: list[OptArticle],
) -> int:
    """Compute the marginal score gain of adding article to subscriber's box."""
    cat = article.category
    base_rank = preference_rank(subscriber, cat)

    # Count how many articles of same category already in box
    same_cat_count = sum(1 for a in current_articles if a.category == cat)

    if base_rank < 0:
        pts = 1
    else:
        effective_rank = base_rank + same_cat_count
        pts = points_for_rank(effective_rank)

    bonus = CONDITION_BONUS.get(article.condition, 0)
    return pts + bonus


def optimize(
    articles: list[OptArticle],
    subscribers: list[OptSubscriber],
    max_weight: int,
) -> Composition:
    """Greedy assignment maximizing total score."""
    composition = Composition()

    # Initialize assignments
    for sub in subscribers:
        composition.assignments[sub.id] = Assignment(
            subscriber_name=sub.name,
            subscriber_id=sub.id,
            articles=[],
        )

    # Group articles by age range for R2
    articles_by_age: dict[str, list[OptArticle]] = {}
    for art in articles:
        articles_by_age.setdefault(art.age_range, []).append(art)

    assigned_articles: set[str] = set()  # R1: uniqueness
    box_weights: dict[str, int] = {s.id: 0 for s in subscribers}

    # Build initial heap: (negative_gain, article_id, subscriber_id)
    # Use negative because heapq is a min-heap
    heap: list[tuple[int, str, str]] = []
    counter = 0  # tiebreaker

    for sub in subscribers:
        available = articles_by_age.get(sub.age_range, [])
        for art in available:
            gain = _marginal_gain(sub, art, [])
            counter += 1
            heapq.heappush(heap, (-gain, counter, art.id, sub.id))

    while heap:
        neg_gain, _, art_id, sub_id = heapq.heappop(heap)

        # Skip if article already assigned
        if art_id in assigned_articles:
            continue

        art = None
        for a in articles:
            if a.id == art_id:
                art = a
                break
        if art is None:
            continue

        sub = None
        for s in subscribers:
            if s.id == sub_id:
                sub = s
                break
        if sub is None:
            continue

        current_box = composition.assignments[sub_id].articles

        # R3: weight check
        if box_weights[sub_id] + art.weight > max_weight:
            continue

        # Recompute actual marginal gain (may have changed)
        actual_gain = _marginal_gain(sub, art, current_box)
        if actual_gain != -neg_gain:
            # Re-insert with correct gain
            counter += 1
            heapq.heappush(heap, (-actual_gain, counter, art_id, sub_id))
            continue

        # Assign
        assigned_articles.add(art_id)
        current_box.append(art)
        box_weights[sub_id] += art.weight

    # Balancing phase (R8): try to move articles from max to min count subscribers
    _balance(composition, subscribers, max_weight, box_weights, assigned_articles, articles)

    return composition


def _balance(
    composition: Composition,
    subscribers: list[OptSubscriber],
    max_weight: int,
    box_weights: dict[str, int],
    assigned_articles: set[str],
    all_articles: list[OptArticle],
) -> None:
    """Try to reduce equity penalties by assigning unassigned articles to smaller boxes."""
    articles_by_age: dict[str, list[OptArticle]] = {}
    for art in all_articles:
        articles_by_age.setdefault(art.age_range, []).append(art)

    for _ in range(10):  # max iterations
        counts = {
            s.id: len(composition.assignments[s.id].articles) for s in subscribers
        }
        if not counts:
            break
        max_count = max(counts.values())
        min_count = min(counts.values())
        if max_count - min_count < 2:
            break

        # Find subscribers with min count
        deficit_subs = [s for s in subscribers if counts[s.id] == min_count]
        improved = False

        for sub in deficit_subs:
            available = articles_by_age.get(sub.age_range, [])
            unassigned = [a for a in available if a.id not in assigned_articles]

            best_art = None
            best_gain = -1
            for art in unassigned:
                if box_weights[sub.id] + art.weight <= max_weight:
                    gain = _marginal_gain(
                        sub, art, composition.assignments[sub.id].articles
                    )
                    if gain > best_gain:
                        best_gain = gain
                        best_art = art

            if best_art is not None:
                assigned_articles.add(best_art.id)
                composition.assignments[sub.id].articles.append(best_art)
                box_weights[sub.id] += best_art.weight
                improved = True

        if not improved:
            break
