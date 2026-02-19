"""CSV I/O for the optimizer — parsing/writing the subject's format (separator ;)."""

from __future__ import annotations

from optimizer.models import Composition, OptArticle, OptSubscriber


def parse_input(text: str) -> tuple[list[OptArticle], list[OptSubscriber], int]:
    """Parse CSV input text. Returns (articles, subscribers, max_weight)."""
    lines = [line.strip() for line in text.strip().splitlines()]
    articles: list[OptArticle] = []
    subscribers: list[OptSubscriber] = []
    max_weight = 0

    section = None
    for line in lines:
        if not line:
            section = None
            continue

        # Use 'contains' not '==' for headers (trailing ; possible)
        if "articles" in line.lower() and section is None:
            section = "articles"
            continue
        if "abonnes" in line.lower() and section != "articles":
            section = "abonnes"
            continue
        if "parametres" in line.lower():
            section = "parametres"
            continue

        if section == "articles":
            parts = line.split(";")
            if len(parts) >= 7:
                articles.append(OptArticle(
                    id=parts[0].strip(),
                    designation=parts[1].strip(),
                    category=parts[2].strip(),
                    age_range=parts[3].strip(),
                    condition=parts[4].strip(),
                    price=int(parts[5].strip()),
                    weight=int(parts[6].strip()),
                ))
        elif section == "abonnes":
            parts = line.split(";")
            if len(parts) >= 4:
                sub_id = parts[0].strip()
                name = parts[1].strip()
                age_range = parts[2].strip()
                prefs_str = parts[3].strip()
                prefs = [p.strip() for p in prefs_str.split(",")]
                subscribers.append(OptSubscriber(
                    id=sub_id,
                    name=name,
                    age_range=age_range,
                    preferences=prefs,
                ))
        elif section == "parametres":
            try:
                max_weight = int(line.strip().rstrip(";"))
            except ValueError:
                pass

    return articles, subscribers, max_weight


def format_output(composition: Composition, score: int) -> str:
    """Format composition to CSV output string."""
    lines = [str(score)]
    for assignment in composition.assignments.values():
        for art in assignment.articles:
            lines.append(
                f"{assignment.subscriber_name};{art.id};{art.category};{art.age_range};{art.condition}"
            )
    return "\n".join(lines) + "\n"


def write_output(filepath: str, composition: Composition, score: int) -> None:
    """Write composition to a file."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(format_output(composition, score))
