from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CampaignStatus(str, Enum):
    CREATED = "created"
    OPTIMIZED = "optimized"
    VALIDATED = "validated"


@dataclass
class Campaign:
    id: str
    max_weight_per_box: int
    status: CampaignStatus = CampaignStatus.CREATED

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "max_weight_per_box": self.max_weight_per_box,
            "status": self.status.value,
        }
