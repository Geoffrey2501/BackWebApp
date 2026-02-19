from __future__ import annotations

from app import db


class Subscriber(db.Model):
    __tablename__ = 'subscribers'

    id = db.Column(db.String(10), primary_key=True) # Format "s1", "s2"...
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    child_age_range = db.Column(db.String(5), nullable=False)
    # Stockage des 6 catégories classées par préférence
    category_preferences = db.Column(db.JSON, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "child_age_range": self.child_age_range,
            "category_preferences": self.category_preferences
        }
