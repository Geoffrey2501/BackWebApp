from flask import Flask


def register_blueprints(app: Flask) -> None:
    from app.routes.admin_articles import bp as articles_bp
    from app.routes.admin_campaigns import bp as campaigns_bp
    from app.routes.admin_dashboard import bp as dashboard_bp
    from app.routes.admin_history import bp as history_bp
    from app.routes.admin_subscribers import bp as subscribers_bp
    from app.routes.subscriber_routes import bp as subscriber_bp

    app.register_blueprint(articles_bp)
    app.register_blueprint(subscribers_bp)
    app.register_blueprint(campaigns_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(subscriber_bp)
