from flask import Flask
from flask_cors import CORS

from app.config import config_by_name


def create_app(config_name: str = "dev") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    CORS(app, origins=[
        "https://toyboxing.th-fchs.fr",
        "http://localhost:5173",
        "http://localhost:3000",
    ])

    from app.routes import register_blueprints
    register_blueprints(app)

    return app
