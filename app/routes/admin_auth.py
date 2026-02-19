from flask import Blueprint, request, jsonify
from app.services import auth_service

bp = Blueprint("admin_auth", __name__, url_prefix="/admin")


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    token = auth_service.verify_admin_credentials(username, password)
    if token:
        return jsonify({"token": token}), 200
    return jsonify({"error": "Identifiants invalides"}), 401