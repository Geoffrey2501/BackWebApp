from flask import Blueprint, jsonify, make_response, request

from app.services import box_service, subscriber_service
from app.utils.validators import validate_age_range, validate_email, validate_preferences

bp = Blueprint("subscriber", __name__, url_prefix="/subscriber")


@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    errors = []

    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()
    email = data.get("email", "").strip()

    if not first_name:
        errors.append("first_name requis")
    if not last_name:
        errors.append("last_name requis")
    if not email or not validate_email(email):
        errors.append("email invalide")

    age_range = validate_age_range(data.get("child_age_range", ""))
    if age_range is None:
        errors.append("child_age_range invalide")

    prefs = validate_preferences(data.get("category_preferences", []))
    if prefs is None:
        errors.append("category_preferences invalide (6 catégories uniques)")

    if errors:
        return jsonify({"errors": errors}), 400

    sub = subscriber_service.register_subscriber(
        first_name=first_name,
        last_name=last_name,
        email=email,
        child_age_range=age_range,
        category_preferences=prefs,
    )
    resp = make_response(jsonify(sub.to_dict()), 201)
    resp.set_cookie("subscriber_email", email, max_age=365 * 24 * 3600)
    return resp


@bp.route("/box", methods=["GET"])
def get_box():
    email = request.args.get("email", "").strip()
    if not email:
        return jsonify({"error": "email requis"}), 400

    sub = subscriber_service.find_by_email(email)
    if sub is None:
        return jsonify({"error": "Abonné non trouvé"}), 404

    # Récupère la liste des box validées
    boxs = box_service.get_validated_box(sub.id)

    # Correction : On vérifie si la liste est vide
    if not boxs:
        return jsonify({"error": "Aucune box validée"}), 404

    # On enrichit les détails et on ne renvoie que la PREMIÈRE (la plus récente)
    # box_service.get_boxes_details renvoie une liste de dicts, on prend l'index [0]
    details = box_service.get_boxes_details(boxs)
    return jsonify(details)


@bp.route("/preferences", methods=["PUT"])
def update_preferences():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    if not email:
        return jsonify({"error": "email requis"}), 400

    age_range = None
    if "child_age_range" in data:
        age_range = validate_age_range(data["child_age_range"])
        if age_range is None:
            return jsonify({"error": "child_age_range invalide"}), 400

    prefs = None
    if "category_preferences" in data:
        prefs = validate_preferences(data["category_preferences"])
        if prefs is None:
            return jsonify({"error": "category_preferences invalide"}), 400

    sub = subscriber_service.update_preferences(
        email=email, child_age_range=age_range, category_preferences=prefs
    )
    if sub is None:
        return jsonify({"error": "Abonné non trouvé"}), 404
    return jsonify(sub.to_dict())


@bp.route("/history", methods=["GET"])
def history():
    email = request.args.get("email", "").strip()
    if not email:
        return jsonify({"error": "email requis"}), 400
    sub = subscriber_service.find_by_email(email)
    if sub is None:
        return jsonify({"error": "Abonné non trouvé"}), 404
    entries = box_service.get_subscriber_history(sub.id)
    return jsonify(entries)
