from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Box:
    campaign_id: str
    subscriber_id: str
    article_ids: list[str] = field(default_factory=list)
    validated: bool = False
    score: int = 0
    total_weight: int = 0
    total_price: int = 0

    def to_dict(self) -> dict:
        return {
            "campaign_id": self.campaign_id,
            "subscriber_id": self.subscriber_id,
            "article_ids": self.article_ids,
            "validated": self.validated,
            "score": self.score,
            "total_weight": self.total_weight,
            "total_price": self.total_price,
        }


@dataclass
class BoxHistoryEntry:
    campaign_id: str
    subscriber_id: str
    article_ids: list[str] = field(default_factory=list)
    score: int = 0
    total_weight: int = 0
    total_price: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "campaign_id": self.campaign_id,
            "subscriber_id": self.subscriber_id,
            "article_ids": self.article_ids,
            "score": self.score,
            "total_weight": self.total_weight,
            "total_price": self.total_price,
            "timestamp": self.timestamp,
        }
