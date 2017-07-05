import os


class DatabaseConfig:
    # Database URI
    DB_NAME = os.environ['DB_NAME']
    DB_USER = os.environ['DB_USER']
    DB_PASS = os.environ['DB_PASS']
    DB_SERVICE = os.environ['DB_SERVICE']
    DB_PORT = os.environ['DB_PORT']

    SQLALCHEMY_DATABASE_URI = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
        DB_USER, DB_PASS, DB_SERVICE, DB_PORT, DB_NAME
    )

    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', "postgresql://postgres:postgres@localhost:5432/postgres")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ParityServerConfig:
    # Address of the parity server
    PARITY_SERVER_HOST = os.environ.get('PARITY_HOST')
    PARITY_SERVER_PORT = os.environ.get('PARITY_PORT', 80)
    PARITY_SSL = os.environ.get('PARITY_SSL', False)

class Web3Config(ParityServerConfig):
    # Number of block to wait before inserting an event in the database
    SAFETY_BLOCK_COUNT = 2


class CeleryConfig:
    CELERY_MODULE_NAME = 'app'  # CELERY_MODULE_NAME is not a default celery's config

    BROKER_URL = os.environ.get('BROKER_URL', 'redis://redis:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
    CELERY_ACCEPT_CONTENT = ['json']


class FlaskConfig:
    DEBUG = os.environ.get('FLASK_DEBUG', True)


class Config(DatabaseConfig, Web3Config, CeleryConfig, FlaskConfig):
    pass

config = Config
