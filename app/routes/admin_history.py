from flask import Blueprint, jsonify


bp = Blueprint("admin_history", __name__, url_prefix="/admin/history")


@bp.route("", methods=["GET"])
def history():
    # Group by campaign
    campaigns_data: dict[str, dict] = {}
    for entry in store.box_history:
        cid = entry.campaign_id
        if cid not in campaigns_data:
            campaigns_data[cid] = {
                "campaign_id": cid,
                "boxes": [],
                "total_articles": 0,
                "total_score": 0,
            }
        campaigns_data[cid]["boxes"].append(entry.to_dict())
        campaigns_data[cid]["total_articles"] += len(entry.article_ids)
        campaigns_data[cid]["total_score"] += entry.score

    result = []
    for cid, data in campaigns_data.items():
        nb_boxes = len(data["boxes"])
        data["nb_boxes"] = nb_boxes
        data["average_score"] = round(data["total_score"] / nb_boxes, 2) if nb_boxes else 0
        result.append(data)

    return jsonify(result)
