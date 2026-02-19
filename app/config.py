import os


class Config:
    TESTING = False
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root@localhost/toyboxing_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(Config):
    DEBUG = True


class TestConfig(Config):
    TESTING = True


class ProdConfig(Config):
    pass


config_by_name = {
    "dev": DevConfig,
    "test": TestConfig,
    "prod": ProdConfig,
}
