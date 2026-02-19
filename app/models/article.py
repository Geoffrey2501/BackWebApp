from __future__ import annotations

from enum import Enum

from app import db


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


class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.String(10), primary_key=True) # Format "a1", "a2"...
    designation = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(10), nullable=False) # Enum SOC, FIG, etc.
    age_range = db.Column(db.String(5), nullable=False) # Enum BB, PE, etc.
    condition = db.Column(db.String(5), nullable=False) # Enum N, TB, B
    price = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    is_locked = db.Column(db.Boolean, default=False) # Pour bloquer la modif après validation

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "designation": self.designation,
            "category": self.category,
            "age_range": self.age_range,
            "condition": self.condition,
            "price": self.price,
            "weight": self.weight,
            "is_locked": self.is_locked
        }
