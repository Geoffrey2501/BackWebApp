"""Standalone CLI entry point: python -m optimizer.cli input.csv [-o output.csv]"""

from __future__ import annotations

import argparse
import sys

from optimizer.csv_io import format_output, parse_input, write_output
from optimizer.greedy import optimize
from optimizer.scorer import score_composition


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="ToyBoxing optimizer CLI")
    parser.add_argument("input", help="Input CSV file path")
    parser.add_argument("-o", "--output", help="Output CSV file path (default: stdout)")

    args = parser.parse_args(argv)

    with open(args.input, encoding="utf-8") as f:
        text = f.read()

    articles, subscribers, max_weight = parse_input(text)
    composition = optimize(articles, subscribers, max_weight)
    score = score_composition(composition, subscribers, max_weight)
    composition.score = score

    if args.output:
        write_output(args.output, composition, score)
        print(f"Score: {score} — résultat écrit dans {args.output}")
    else:
        sys.stdout.write(format_output(composition, score))


if __name__ == "__main__":
    main()
