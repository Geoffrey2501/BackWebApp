from flask import Blueprint, jsonify

from app.services import dashboard_service

bp = Blueprint("admin_dashboard", __name__, url_prefix="/admin/dashboard")


@bp.route("", methods=["GET"])
def dashboard():
    stats = dashboard_service.get_dashboard_stats()
    return jsonify(stats)
