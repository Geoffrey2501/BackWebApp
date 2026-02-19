from __future__ import annotations

from dataclasses import dataclass, field
from app import db
from datetime import datetime

class Box(db.Model):
    __tablename__ = 'boxes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    campaign_id = db.Column(db.String(10), db.ForeignKey('campaigns.id'), nullable=False)
    subscriber_id = db.Column(db.String(10), db.ForeignKey('subscribers.id'), nullable=False)
    article_ids = db.Column(db.JSON, nullable=False) # Liste des IDs
    validated = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, default=0)
    total_weight = db.Column(db.Integer, default=0)
    total_price = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # Pour l'historique

    def to_dict(self) -> dict:
        return {
            "campaign_id": self.campaign_id,
            "subscriber_id": self.subscriber_id,
            "article_ids": self.article_ids,
            "validated": self.validated,
            "score": self.score,
            "total_weight": self.total_weight,
            "total_price": self.total_price,
            "timestamp": self.created_at.isoformat()
        }


class BoxHistoryEntry(db.Model):
    __tablename__ = 'box_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    campaign_id = db.Column(db.String(10), nullable=False)
    subscriber_id = db.Column(db.String(10), nullable=False)
    # article_ids est stocké en JSON pour figer la liste au moment de la validation
    article_ids = db.Column(db.JSON, nullable=False)
    score = db.Column(db.Integer, default=0)
    total_weight = db.Column(db.Integer, default=0)
    total_price = db.Column(db.Integer, default=0)
    # On utilise le type DateTime natif de SQL pour plus de précision
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "campaign_id": self.campaign_id,
            "subscriber_id": self.subscriber_id,
            "article_ids": self.article_ids,
            "score": self.score,
            "total_weight": self.total_weight,
            "total_price": self.total_price,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }