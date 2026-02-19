"""Tests for CSV parsing and output formatting."""

from optimizer.csv_io import format_output, parse_input
from optimizer.models import Assignment, Composition, OptArticle


def test_parse_sample_input():
    with open("tests/data/sample_input.csv", encoding="utf-8") as f:
        text = f.read()

    articles, subscribers, max_weight = parse_input(text)

    assert len(articles) == 8
    assert len(subscribers) == 3
    assert max_weight == 1200

    assert articles[0].id == "a1"
    assert articles[0].designation == "Monopoly Junior"
    assert articles[0].category == "SOC"
    assert articles[0].age_range == "PE"
    assert articles[0].condition == "N"
    assert articles[0].price == 8
    assert articles[0].weight == 400

    assert subscribers[0].name == "Alice"
    assert subscribers[0].age_range == "PE"
    assert subscribers[0].preferences == ["SOC", "FIG", "EVL", "CON", "LIV", "EXT"]


def test_parse_handles_trailing_semicolons():
    """CSV with trailing ; after headers should parse correctly."""
    text = """articles;
a1;Test;SOC;PE;N;5;200

abonnes;
s1;Alice;PE;SOC,FIG,EVL,CON,LIV,EXT

parametres;
1000
"""
    articles, subscribers, max_weight = parse_input(text)
    assert len(articles) == 1
    assert len(subscribers) == 1
    assert max_weight == 1000


def test_format_output():
    a1 = OptArticle("a1", "Test", "SOC", "PE", "N", 5, 200)
    comp = Composition(assignments={
        "s1": Assignment("Alice", "s1", [a1]),
    })
    output = format_output(comp, 42)
    lines = output.strip().split("\n")
    assert lines[0] == "42"
    assert lines[1] == "Alice;a1;SOC;PE;N"
