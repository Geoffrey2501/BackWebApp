from __future__ import annotations

import re

from app.models.article import AgeRange, Category, Condition

VALID_CATEGORIES = {c.value for c in Category}
VALID_AGE_RANGES = {a.value for a in AgeRange}
VALID_CONDITIONS = {c.value for c in Condition}

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_category(value: str) -> Category | None:
    if value in VALID_CATEGORIES:
        return Category(value)
    return None


def validate_age_range(value: str) -> AgeRange | None:
    if value in VALID_AGE_RANGES:
        return AgeRange(value)
    return None


def validate_condition(value: str) -> Condition | None:
    if value in VALID_CONDITIONS:
        return Condition(value)
    return None


def validate_email(value: str) -> bool:
    return bool(EMAIL_RE.match(value))


def validate_preferences(prefs: list[str]) -> list[Category] | None:
    if len(prefs) != 6:
        return None
    seen = set()
    result = []
    for p in prefs:
        cat = validate_category(p)
        if cat is None or cat.value in seen:
            return None
        seen.add(cat.value)
        result.append(cat)
    return result
