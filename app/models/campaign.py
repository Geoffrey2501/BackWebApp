from __future__ import annotations

from enum import Enum

from app import db


class CampaignStatus(str, Enum):
    CREATED = "created"
    OPTIMIZED = "optimized"
    VALIDATED = "validated"



class Campaign(db.Model):
    __tablename__ = 'campaigns'

    id = db.Column(db.String(10), primary_key=True) # Format "c1"...
    max_weight_per_box = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="created") # created, optimized, validated

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "max_weight_per_box": self.max_weight_per_box,
            "status": self.status
        }
