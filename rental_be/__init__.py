from importlib import import_module
from typing import Type

from flask import Flask
from flask_cors import CORS

from rental_be import config
from rental_be.db.mongo import MongoEngine

# Globals
mongo = MongoEngine()


def create_app(config_module=config) -> Type[Flask]:
    """Create a Rental-BE Flask app

    :returns: Flask app
    """
    app = Flask(__name__.split('.')[0])
    CORS(app, resources={r"/*": {"origins": "*"}})
    # Configure Flask app
    app.config.from_object(config)
    # Initialize Flask extensions
    mongo.init_app(app)
    app.mongo = mongo

    with app.app_context():
        # NOTE: Blueprints should be imported after initializing app
        # to avoid circular dependencies
        for version in ['v1']:
            module = import_module(f'rental_be.api.{version}')
            app.register_blueprint(module.rental_bp)

    return app
