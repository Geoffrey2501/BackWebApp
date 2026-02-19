import os


def _build_db_uri() -> str:
    host = os.environ.get("DB_HOST", "localhost")
    user = os.environ.get("DB_USER", "root")
    password = os.environ.get("DB_PASSWORD", "")
    name = os.environ.get("DB_NAME", "toys_academy")
    if password:
        return f"mysql+pymysql://{user}:{password}@{host}/{name}"
    return f"mysql+pymysql://{user}@{host}/{name}"


class Config:
    TESTING = False
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = _build_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(Config):
    DEBUG = True


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProdConfig(Config):
    pass


config_by_name = {
    "dev": DevConfig,
    "test": TestConfig,
    "prod": ProdConfig,
    "production": ProdConfig,
}
