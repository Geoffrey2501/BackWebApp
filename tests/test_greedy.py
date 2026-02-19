"""Tests for the greedy optimizer."""

from optimizer.csv_io import parse_input
from optimizer.greedy import optimize
from optimizer.scorer import score_composition


def test_greedy_sample_data():
    """Optimizer should produce a score >= 62 on the PDF example."""
    with open("tests/data/sample_input.csv", encoding="utf-8") as f:
        text = f.read()

    articles, subscribers, max_weight = parse_input(text)
    composition = optimize(articles, subscribers, max_weight)
    score = score_composition(composition, subscribers, max_weight)

    assert score >= 62


def test_greedy_respects_weight():
    """All boxes should respect max weight."""
    with open("tests/data/sample_input.csv", encoding="utf-8") as f:
        text = f.read()

    articles, subscribers, max_weight = parse_input(text)
    composition = optimize(articles, subscribers, max_weight)

    for sub in subscribers:
        assignment = composition.assignments.get(sub.id)
        if assignment:
            total_weight = sum(a.weight for a in assignment.articles)
            assert total_weight <= max_weight, (
                f"{sub.name} box weight {total_weight} > {max_weight}"
            )


def test_greedy_respects_age_compatibility():
    """R2: all articles in a box must match subscriber's age range."""
    with open("tests/data/sample_input.csv", encoding="utf-8") as f:
        text = f.read()

    articles, subscribers, max_weight = parse_input(text)
    composition = optimize(articles, subscribers, max_weight)

    for sub in subscribers:
        assignment = composition.assignments.get(sub.id)
        if assignment:
            for art in assignment.articles:
                assert art.age_range == sub.age_range, (
                    f"Article {art.id} ({art.age_range}) assigned to "
                    f"{sub.name} ({sub.age_range})"
                )


def test_greedy_article_uniqueness():
    """R1: each article appears in at most one box."""
    with open("tests/data/sample_input.csv", encoding="utf-8") as f:
        text = f.read()

    articles, subscribers, max_weight = parse_input(text)
    composition = optimize(articles, subscribers, max_weight)

    seen: set[str] = set()
    for assignment in composition.assignments.values():
        for art in assignment.articles:
            assert art.id not in seen, f"Article {art.id} assigned twice"
            seen.add(art.id)
