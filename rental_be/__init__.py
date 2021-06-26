from importlib import import_module

from flask import Flask
from flask_cors import CORS                                 # type: ignore[import]

from rental_be import config
from rental_be.db.mongo import MongoEngine

# Globals
mongo = MongoEngine()


def create_app(config_module=config) -> Flask:
    """Create a Rental-BE Flask app

    :returns: Flask app
    """
    app = Flask(__name__.split('.')[0])
    CORS(app, resources={r"/*": {"origins": "*"}})
    # Configure Flask app
    app.config.from_object(config)
    # Initialize Flask extensions
    mongo.init_app(app)
    app.mongo = mongo                                                           # type: ignore[attr-defined]    # noqa E501

    with app.app_context():
        # NOTE: Blueprints should be imported after initializing app
        # to avoid circular dependencies
        for version in ['v1']:
            module = import_module(f'rental_be.api.{version}')
            app.register_blueprint(module.rental_bp)                            # type: ignore[attr-defined]    # noqa E501

    return app
