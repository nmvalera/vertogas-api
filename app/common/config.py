import os


class DatabaseConfig:
    # Database URI
    DATABASE_URI = "postgresql://postgres:postgres@vertogastokenapp_postgres_1:5432/postgres"


class ParityServerConfig:
    # Address of the parity server
    PARITY_SERVER_HOST = 'vps412488.ovh.net'
    PARITY_SERVER_PORT = '1935'


class Web3Config(ParityServerConfig):
    # Number of block to wait before inserting an event in the database
    SAFETY_BLOCK_COUNT = 10


class CeleryConfig:
    CELERY_MODULE_NAME = 'app'  # CELERY_MODULE_NAME is not a default celery's config

    BROKER_URL = 'redis://redis:6379/0'
    CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
    CELERY_ACCEPT_CONTENT = ['json']


class FlaskConfig:
    DEBUG = os.environ.get('FLASK_DEBUG', True)


class Config(DatabaseConfig, Web3Config, CeleryConfig, FlaskConfig):
    pass

config = Config
