from flask import Blueprint, jsonify

from app.services import subscriber_service

bp = Blueprint("admin_subscribers", __name__, url_prefix="/admin/subscribers")


@bp.route("", methods=["GET"])
def list_subscribers():
    subs = subscriber_service.list_subscribers()
    return jsonify([s.to_dict() for s in subs])
