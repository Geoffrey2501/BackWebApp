from __future__ import annotations
from app import db
from app.models.box import Box, BoxHistoryEntry
from app.models.campaign import Campaign, CampaignStatus
from app.models.article import Article
from app.models.subscriber import Subscriber
from optimizer.api import run_optimization


def create_campaign(max_weight_per_box: int) -> Campaign:
    # Génération de l'ID au format c1, c2...
    count = Campaign.query.count()
    cid = f"c{count + 1}"

    campaign = Campaign(id=cid, max_weight_per_box=max_weight_per_box)
    db.session.add(campaign)
    db.session.commit()
    return campaign


def get_campaign(campaign_id: str) -> Campaign | None:
    return Campaign.query.get(campaign_id)


def list_campaigns() -> list[Campaign]:
    return Campaign.query.all()


def optimize_campaign(campaign_id: str) -> tuple[list[Box] | None, str | None]:
    campaign = Campaign.query.get(campaign_id)
    if campaign is None:
        return None, "Campagne non trouvée"
    if campaign.status != CampaignStatus.CREATED:
        return None, "Campagne déjà optimisée"

    # Récupération des données depuis la DB
    articles = Article.query.all()
    subscribers = Subscriber.query.all()

    if not subscribers:
        return None, "Aucun abonné enregistré"

    # Lancement de l'algorithme
    boxes = run_optimization(articles, subscribers, campaign.max_weight_per_box)

    # Nettoyage des anciennes box non validées pour cette campagne
    Box.query.filter_by(campaign_id=campaign_id, validated=False).delete()

    for box in boxes:
        box.campaign_id = campaign_id
        db.session.add(box)

    campaign.status = CampaignStatus.OPTIMIZED
    db.session.commit()
    return boxes, None


def get_campaign_boxes(campaign_id: str) -> list[Box]:
    return Box.query.filter_by(campaign_id=campaign_id, validated=False).all()


def validate_box(campaign_id: str, subscriber_id: str) -> tuple[Box | None, str | None]:
    campaign = Campaign.query.get(campaign_id)
    if campaign is None:
        return None, "Campagne non trouvée"

    box = Box.query.filter_by(campaign_id=campaign_id, subscriber_id=subscriber_id).first()

    if box is None:
        return None, "Box non trouvée"
    if box.validated:
        return None, "Box déjà validée"

    box.validated = True

    # Verrouillage des articles (is_locked)
    for art_id in box.article_ids:
        article = Article.query.get(art_id)
        if article:
            article.is_locked = True

    # Ajout à l'historique
    entry = BoxHistoryEntry(
        campaign_id=campaign_id,
        subscriber_id=subscriber_id,
        article_ids=list(box.article_ids),
        score=box.score,
        total_weight=box.total_weight,
        total_price=box.total_price,
    )
    db.session.add(entry)
    db.session.commit()

    return box, None