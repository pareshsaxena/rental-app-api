"""Mongoengine: Flask ODM extension
"""
from bson import json_util                                  # type: ignore[import]
from typing import Dict, Optional, Type

from flask import Flask, current_app
from flask.json import JSONEncoder
from mongoengine.base import BaseDocument                   # type: ignore[import]
from mongoengine.queryset import QuerySet                   # type: ignore[import]
from pymongo import MongoClient                             # type: ignore[import]

from rental_be.db.mongo_connection import create_connections


class MongoJSONEncoder(JSONEncoder):
    """JSON encoder which provides serialization of MongoEngine
    documents and queryset objects
    """
    def default(self, obj):
        if isinstance(obj, BaseDocument):
            return json_util._json_convert(obj.to_mongo())
        elif isinstance(obj, QuerySet):
            return json_util._json_convert(obj.as_pymongo())
        return super().default(obj)


class MongoEngine:
    """MongoDB ODM extension to Flask
    """
    def __init__(
            self,
            app: Optional[Flask] = None,
            config: Dict = None
        ) -> None:                                                              # noqa E125
        self.app = app
        if app is not None:
            self.init_app(app, config)

    def init_app(self, app: Flask, config: Dict = None) -> None:
        """Initializes a Flask app to use a database which implements
        MongoDB Wire protocol
        """
        if not app or not isinstance(app, Flask):
            raise Exception('Invalid Flask application instance')
        # Store the app on the MongoEngine instance - use case: multiple applications
        self.app = app
        app.extensions = getattr(app, "extensions", {})

        # Attach a custom JSON encoder class to Flask app
        app.json_encoder = MongoJSONEncoder

        if 'mongoengine' not in app.extensions:
            app.extensions['mongoengine'] = {}

        if self in app.extensions['mongoengine']:
            # Raise an exception as new configuration would not be loaded
            raise Exception("MongoEngine extension already initialized")

        if not config:
            config = app.config

        # Obtain DB connection(s)
        connections = create_connections(config)

        # Store objects in application instance so that multiple apps do not
        # end up accessing the same objects
        s = {'app': app, 'conn': connections}
        app.extensions['mongoengine'][self] = s

    @property
    def connection(self) -> Type[MongoClient]:
        """Returns database connection(s) associated with this MongoEngine
        instance
        """
        return current_app.extensions['mongoengine'][self]['conn']


def current_mongoengine_instance() -> Optional[MongoEngine]:
    """Returns the MongoEngine object associated with the current Flask app
    """
    me = current_app.extensions.get('mongoengine', {})
    for k, _ in me.items():
        if isinstance(k, MongoEngine):
            return k
    return None
