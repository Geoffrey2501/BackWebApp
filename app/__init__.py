from flask import Flask
from flask_cors import CORS  # Importer l'extension
from app.config import config_by_name


def create_app(config_name: str = "dev") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Activer CORS pour toutes les routes
    # En production, il est recommandé de restreindre origins=["http://ton-domaine-front.fr"]
    CORS(app)

    from app.routes import register_blueprints
    register_blueprints(app)

    return app
