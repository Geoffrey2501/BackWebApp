from flask import Flask

from app.config import config_by_name


def create_app(config_name: str = "dev") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    from app.routes import register_blueprints

    register_blueprints(app)
    return app
