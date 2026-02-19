from flask import Blueprint, jsonify, request

from app.services import article_service
from app.utils.pagination import paginate
from app.utils.validators import validate_age_range, validate_category, validate_condition

bp = Blueprint("admin_articles", __name__, url_prefix="/admin/articles")


@bp.route("", methods=["POST"])
def create_article():
    data = request.get_json(silent=True) or {}
    errors = []

    designation = data.get("designation")
    if not designation:
        errors.append("designation requis")

    category = validate_category(data.get("category", ""))
    if category is None:
        errors.append("category invalide")

    age_range = validate_age_range(data.get("age_range", ""))
    if age_range is None:
        errors.append("age_range invalide")

    condition = validate_condition(data.get("condition", ""))
    if condition is None:
        errors.append("condition invalide")

    price = data.get("price")
    if not isinstance(price, int) or price < 0:
        errors.append("price invalide (entier positif)")

    weight = data.get("weight")
    if not isinstance(weight, int) or weight <= 0:
        errors.append("weight invalide (entier positif)")

    if errors:
        return jsonify({"errors": errors}), 400

    article = article_service.add_article(
        designation=designation,
        category=category,
        age_range=age_range,
        condition=condition,
        price=price,
        weight=weight,
    )
    return jsonify(article.to_dict()), 201


@bp.route("", methods=["GET"])
def list_articles():
    page = request.args.get("page", 1, type=int)
    category = request.args.get("category")
    age_range = request.args.get("age_range")
    condition = request.args.get("condition")

    articles = article_service.list_articles(
        category=category, age_range=age_range, condition=condition
    )
    result = paginate([a.to_dict() for a in articles], page)
    return jsonify(result)


@bp.route("/<article_id>", methods=["GET"])
def get_article(article_id: str):
    article = article_service.get_article(article_id)
    if article is None:
        return jsonify({"error": "Article non trouvé"}), 404
    return jsonify(article.to_dict())


@bp.route("/<article_id>", methods=["PUT"])
def update_article(article_id: str):
    data = request.get_json(silent=True) or {}
    fields: dict = {}

    if "designation" in data:
        fields["designation"] = data["designation"]
    if "category" in data:
        cat = validate_category(data["category"])
        if cat is None:
            return jsonify({"error": "category invalide"}), 400
        fields["category"] = cat
    if "age_range" in data:
        ar = validate_age_range(data["age_range"])
        if ar is None:
            return jsonify({"error": "age_range invalide"}), 400
        fields["age_range"] = ar
    if "condition" in data:
        cond = validate_condition(data["condition"])
        if cond is None:
            return jsonify({"error": "condition invalide"}), 400
        fields["condition"] = cond
    if "price" in data:
        fields["price"] = data["price"]
    if "weight" in data:
        fields["weight"] = data["weight"]

    article, error = article_service.update_article(article_id, **fields)
    if error and "validée" in error:
        return jsonify({"error": error}), 409
    if error:
        return jsonify({"error": error}), 404
    return jsonify(article.to_dict())
