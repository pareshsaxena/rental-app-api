"""Configuration module
"""


class BaseConfig():
    """Base configuration for all environments
    """
    DEBUG = False
    TESTING = False
    LOGFILE = './log/rental_be.log'
    SECRET_KEY = '6rvy9754giyt7xevfjhvyujbnopiuytbcfv'
    LANGUAGE_CODE = 'en'


class DevConfig(BaseConfig):
    """`Dev` environment configuration
    """
    ENV = 'development'
    DEBUG = True
    TESTING = True
    MONGODB_SETTINGS = {
        'db': 'rental',
        'host': '0.0.0.0',
        'port': 27017,
        'username': '',
        'password': '',
        'authentication_source': 'admin',
        'tlsAllowInvalidCertificates': True,
        'retrywrites': False,
        # NOTE: Uncomment the SSL setting below to connect to Azure Cosmos DB
        # 'ssl': True,
    }


class ProdConfig(BaseConfig):
    """`Prod` environment configuration
    """
    ENV = 'production'
    MONGODB_SETTINGS = None


class TestConfig(BaseConfig):
    """`Test` environment configuration
    """
    ENV = 'development'
    TESTING = True
    MONGODB_SETTINGS = {
        'db': 'test',
        'host': '0.0.0.0',
        'port': 27017,
    }
