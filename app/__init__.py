from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import config_by_name

# On crée l'objet db ici
db = SQLAlchemy()

def create_app(config_name: str = "dev") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialisation de db avec les paramètres de l'app
    db.init_app(app)

    from app.routes import register_blueprints
    register_blueprints(app)

    # Création des tables MySQL au démarrage (optionnel si vous utilisez Flask-Migrate)
    with app.app_context():
        db.create_all()

    return app
