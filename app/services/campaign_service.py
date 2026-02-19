from __future__ import annotations

from app.models.box import Box, BoxHistoryEntry
from app.models.campaign import Campaign, CampaignStatus
from app.store.memory_store import store
from optimizer.api import run_optimization


def create_campaign(max_weight_per_box: int) -> Campaign:
    cid = store.next_campaign_id()
    campaign = Campaign(id=cid, max_weight_per_box=max_weight_per_box)
    store.campaigns[cid] = campaign
    return campaign


def get_campaign(campaign_id: str) -> Campaign | None:
    return store.campaigns.get(campaign_id)


def list_campaigns() -> list[Campaign]:
    return list(store.campaigns.values())


def optimize_campaign(campaign_id: str) -> tuple[list[Box] | None, str | None]:
    campaign = store.campaigns.get(campaign_id)
    if campaign is None:
        return None, "Campagne non trouvée"
    if campaign.status != CampaignStatus.CREATED:
        return None, "Campagne déjà optimisée"

    articles = list(store.articles.values())
    subscribers = list(store.subscribers.values())

    if not subscribers:
        return None, "Aucun abonné enregistré"

    boxes = run_optimization(articles, subscribers, campaign.max_weight_per_box)
    for box in boxes:
        box.campaign_id = campaign_id

    # Replace current boxes for this campaign
    store.boxes = [b for b in store.boxes if b.campaign_id != campaign_id] + boxes
    campaign.status = CampaignStatus.OPTIMIZED
    return boxes, None


def get_campaign_boxes(campaign_id: str) -> list[Box]:
    return [b for b in store.boxes if b.campaign_id == campaign_id]


def validate_box(campaign_id: str, subscriber_id: str) -> tuple[Box | None, str | None]:
    campaign = store.campaigns.get(campaign_id)
    if campaign is None:
        return None, "Campagne non trouvée"

    box = None
    for b in store.boxes:
        if b.campaign_id == campaign_id and b.subscriber_id == subscriber_id:
            box = b
            break

    if box is None:
        return None, "Box non trouvée"
    if box.validated:
        return None, "Box déjà validée"

    box.validated = True

    # Lock articles
    for art_id in box.article_ids:
        store.validated_article_campaigns.setdefault(art_id, set()).add(campaign_id)

    # Add to history
    entry = BoxHistoryEntry(
        campaign_id=campaign_id,
        subscriber_id=subscriber_id,
        article_ids=list(box.article_ids),
        score=box.score,
        total_weight=box.total_weight,
        total_price=box.total_price,
    )
    store.box_history.append(entry)

    return box, None
