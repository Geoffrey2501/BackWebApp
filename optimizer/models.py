from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class OptArticle:
    id: str
    designation: str
    category: str
    age_range: str
    condition: str
    price: int
    weight: int


@dataclass
class OptSubscriber:
    id: str
    name: str
    age_range: str
    preferences: list[str] = field(default_factory=list)


@dataclass
class Assignment:
    subscriber_name: str
    subscriber_id: str
    articles: list[OptArticle] = field(default_factory=list)


@dataclass
class Composition:
    assignments: dict[str, Assignment] = field(default_factory=dict)
    score: int = 0
