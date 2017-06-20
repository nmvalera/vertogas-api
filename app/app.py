from flask import Flask

from .common import config
from .extensions import db

__all__ = [
    'create_app',
]


def create_app(register_blueprints=True):
    app = Flask(__name__)
    set_config(app)
    configure_extensions(app)

    if register_blueprints:
        configure_blueprints(app)

    return app


def set_config(app):
    app.config.from_object(config)


def configure_extensions(app):
    db.init_app(app)


def configure_blueprints(app):
    from .resources import blueprints_list
    for bp in blueprints_list:
        app.register_blueprint(bp)
