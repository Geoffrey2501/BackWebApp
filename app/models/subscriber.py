from __future__ import annotations

from dataclasses import dataclass, field

from app.models.article import AgeRange, Category


@dataclass
class Subscriber:
    id: str
    first_name: str
    last_name: str
    email: str
    child_age_range: AgeRange
    category_preferences: list[Category] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "child_age_range": self.child_age_range.value,
            "category_preferences": [c.value for c in self.category_preferences],
        }
