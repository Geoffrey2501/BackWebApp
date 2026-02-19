"""Tests for the scorer — validation against the PDF examples (scores 62 and 70)."""

from optimizer.models import Assignment, Composition, OptArticle, OptSubscriber
from optimizer.scorer import score_composition, score_subscriber_box


def _make_articles():
    return {
        "a1": OptArticle("a1", "Monopoly Junior", "SOC", "PE", "N", 8, 400),
        "a2": OptArticle("a2", "Barbie Aventurière", "FIG", "PE", "TB", 5, 300),
        "a3": OptArticle("a3", "Puzzle éducatif", "EVL", "PE", "TB", 7, 350),
        "a4": OptArticle("a4", "Cubes alphabet", "CON", "PE", "N", 4, 300),
        "a5": OptArticle("a5", "Livre cache-cache", "LIV", "PE", "N", 3, 200),
        "a6": OptArticle("a6", "Kapla 200 pièces", "CON", "EN", "B", 10, 600),
        "a7": OptArticle("a7", "Cerf-volant Pirate", "EXT", "EN", "N", 6, 400),
        "a8": OptArticle("a8", "Le Petit Nicolas", "LIV", "EN", "TB", 5, 200),
    }


def _make_subscribers():
    return [
        OptSubscriber("s1", "Alice", "PE", ["SOC", "FIG", "EVL", "CON", "LIV", "EXT"]),
        OptSubscriber("s2", "Bob", "EN", ["EXT", "CON", "SOC", "EVL", "FIG", "LIV"]),
        OptSubscriber("s3", "Clara", "PE", ["EVL", "LIV", "FIG", "SOC", "CON", "EXT"]),
    ]


def test_composition_score_62():
    """First composition from the PDF: score = 62."""
    arts = _make_articles()
    subs = _make_subscribers()

    comp = Composition(assignments={
        "s1": Assignment("Alice", "s1", [arts["a1"], arts["a2"], arts["a3"]]),
        "s2": Assignment("Bob", "s2", [arts["a7"], arts["a6"]]),
        "s3": Assignment("Clara", "s3", [arts["a4"], arts["a5"]]),
    })

    score = score_composition(comp, subs, 1200)
    assert score == 62


def test_composition_score_70():
    """Better composition from the PDF: score = 70."""
    arts = _make_articles()
    subs = _make_subscribers()

    comp = Composition(assignments={
        "s1": Assignment("Alice", "s1", [arts["a1"], arts["a2"], arts["a4"]]),
        "s2": Assignment("Bob", "s2", [arts["a7"], arts["a6"], arts["a8"]]),
        "s3": Assignment("Clara", "s3", [arts["a3"], arts["a5"]]),
    })

    score = score_composition(comp, subs, 1200)
    assert score == 70


def test_alice_box_score_28():
    """Alice's box in first composition: a1(SOC)+a2(FIG)+a3(EVL) = 12+9+7 = 28."""
    alice = OptSubscriber("s1", "Alice", "PE", ["SOC", "FIG", "EVL", "CON", "LIV", "EXT"])
    arts = _make_articles()
    score = score_subscriber_box(alice, [arts["a1"], arts["a2"], arts["a3"]])
    assert score == 28


def test_bob_box_score_20():
    """Bob's box in first composition: a7(EXT)+a6(CON) = 12+8 = 20."""
    bob = OptSubscriber("s2", "Bob", "EN", ["EXT", "CON", "SOC", "EVL", "FIG", "LIV"])
    arts = _make_articles()
    score = score_subscriber_box(bob, [arts["a7"], arts["a6"]])
    assert score == 20


def test_clara_box_score_14():
    """Clara's box in first composition: a4(CON)+a5(LIV) = 4+10 = 14."""
    clara = OptSubscriber("s3", "Clara", "PE", ["EVL", "LIV", "FIG", "SOC", "CON", "EXT"])
    arts = _make_articles()
    score = score_subscriber_box(clara, [arts["a4"], arts["a5"]])
    assert score == 14


def test_empty_box_malus():
    """R7: empty box gives -10 malus."""
    subs = [OptSubscriber("s1", "Alice", "PE", ["SOC", "FIG", "EVL", "CON", "LIV", "EXT"])]
    comp = Composition(assignments={
        "s1": Assignment("Alice", "s1", []),
    })
    score = score_composition(comp, subs, 1200)
    assert score == -10


def test_equity_malus():
    """R8: 2+ articles difference gives -10 per subscriber."""
    arts = _make_articles()
    subs = _make_subscribers()

    # Alice gets 3, Bob gets 0, Clara gets 0 → two -10 malus for empty + equity
    comp = Composition(assignments={
        "s1": Assignment("Alice", "s1", [arts["a1"], arts["a2"], arts["a3"]]),
        "s2": Assignment("Bob", "s2", []),
        "s3": Assignment("Clara", "s3", []),
    })
    score = score_composition(comp, subs, 1200)
    # Alice: 28, Bob: -10 (empty), Clara: -10 (empty)
    # R8: Bob is 3 less → -10, Clara is 3 less → -10
    assert score == 28 - 10 - 10 - 10 - 10  # = -12


def test_diminishing_returns_same_category():
    """R6: two articles of same category → second uses shifted rank."""
    alice = OptSubscriber("s1", "Alice", "PE", ["SOC", "FIG", "EVL", "CON", "LIV", "EXT"])
    a1 = OptArticle("a1", "Monopoly Junior", "SOC", "PE", "N", 8, 400)
    a_extra = OptArticle("ax", "Extra SOC", "SOC", "PE", "N", 5, 200)
    # First SOC: rank 0 → 10 + 2(N) = 12
    # Second SOC: rank 1 → 8 + 2(N) = 10
    score = score_subscriber_box(alice, [a1, a_extra])
    assert score == 22
