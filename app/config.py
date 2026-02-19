class Config:
    TESTING = False
    DEBUG = False


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
