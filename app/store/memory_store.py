from __future__ import annotations

from app.models.article import Article
from app.models.box import Box, BoxHistoryEntry
from app.models.campaign import Campaign
from app.models.subscriber import Subscriber


class MemoryStore:
    _instance: MemoryStore | None = None

    def __new__(cls) -> MemoryStore:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_store()
        return cls._instance

    def _init_store(self) -> None:
        self.articles: dict[str, Article] = {}
        self.subscribers: dict[str, Subscriber] = {}
        self.campaigns: dict[str, Campaign] = {}
        self.boxes: list[Box] = []
        self.box_history: list[BoxHistoryEntry] = []
        self.validated_article_campaigns: dict[str, set[str]] = {}
        self._article_counter = 0
        self._subscriber_counter = 0
        self._campaign_counter = 0

    def next_article_id(self) -> str:
        self._article_counter += 1
        return f"a{self._article_counter}"

    def next_subscriber_id(self) -> str:
        self._subscriber_counter += 1
        return f"s{self._subscriber_counter}"

    def next_campaign_id(self) -> str:
        self._campaign_counter += 1
        return f"c{self._campaign_counter}"

    def clear(self) -> None:
        self._init_store()


store = MemoryStore()
