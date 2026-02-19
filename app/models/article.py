from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Category(str, Enum):
    SOC = "SOC"
    FIG = "FIG"
    CON = "CON"
    EXT = "EXT"
    EVL = "EVL"
    LIV = "LIV"


class AgeRange(str, Enum):
    BB = "BB"
    PE = "PE"
    EN = "EN"
    AD = "AD"


class Condition(str, Enum):
    N = "N"
    TB = "TB"
    B = "B"


@dataclass
class Article:
    id: str
    designation: str
    category: Category
    age_range: AgeRange
    condition: Condition
    price: int
    weight: int

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "designation": self.designation,
            "category": self.category.value,
            "age_range": self.age_range.value,
            "condition": self.condition.value,
            "price": self.price,
            "weight": self.weight,
        }
