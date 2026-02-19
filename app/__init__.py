from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from app.config import config_by_name
from app.routes import register_blueprints

# On crée l'objet db ici
db = SQLAlchemy()

def create_app(config_name: str = "dev") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    CORS(app, origins=[
        "https://toyboxing.th-fchs.fr",
        "http://localhost:5173",
        "http://localhost:3000",
    ])
    # Initialisation de db avec les paramètres de l'app
    db.init_app(app)
    register_blueprints(app)


    # Création des tables MySQL au démarrage (optionnel si vous utilisez Flask-Migrate)
    with app.app_context():
        db.create_all()

    return app
