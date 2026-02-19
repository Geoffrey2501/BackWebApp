from flask import Blueprint, jsonify, request

from app.services import campaign_service

bp = Blueprint("admin_campaigns", __name__, url_prefix="/admin/campaigns")


@bp.route("", methods=["POST"])
def create_campaign():
    data = request.get_json(silent=True) or {}
    max_weight = data.get("max_weight_per_box")
    if not isinstance(max_weight, int) or max_weight <= 0:
        return jsonify({"error": "max_weight_per_box invalide (entier positif)"}), 400
    campaign = campaign_service.create_campaign(max_weight)
    return jsonify(campaign.to_dict()), 201


@bp.route("", methods=["GET"])
def list_campaigns():
    campaigns = campaign_service.list_campaigns()
    return jsonify([c.to_dict() for c in campaigns])


@bp.route("/<campaign_id>/optimize", methods=["POST"])
def optimize_campaign(campaign_id: str):
    boxes, error = campaign_service.optimize_campaign(campaign_id)
    if error:
        return jsonify({"error": error}), 400
    return jsonify([b.to_dict() for b in boxes])


@bp.route("/<campaign_id>/boxes", methods=["GET"])
def get_boxes(campaign_id: str):
    campaign = campaign_service.get_campaign(campaign_id)
    if campaign is None:
        return jsonify({"error": "Campagne non trouvée"}), 404
    boxes = campaign_service.get_campaign_boxes(campaign_id)
    result = []
    for box in boxes:
        box_data = box.to_dict()
        # Enrich with article details
        box_data["articles"] = []
        for art_id in box.article_ids:
            art = store.articles.get(art_id)
            if art:
                box_data["articles"].append(art.to_dict())
        # Enrich with subscriber info
        sub = store.subscribers.get(box.subscriber_id)
        if sub:
            box_data["subscriber_name"] = f"{sub.first_name} {sub.last_name}"
        result.append(box_data)
    return jsonify(result)


@bp.route("/<campaign_id>/boxes/<subscriber_id>/validate", methods=["POST"])
def validate_box(campaign_id: str, subscriber_id: str):
    box, error = campaign_service.validate_box(campaign_id, subscriber_id)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(box.to_dict())
