from typing import Dict

import mongoengine                                          # type: ignore[import]
from pymongo import ReadPreference, uri_parser              # type: ignore[import]


__all__ = (
    'create_connections',
    'get_connection_settings',
    'InvalidSettingsError',
)


MONGODB_CONF_VARS = (
    'MONGODB_ALIAS',
    'MONGODB_DB',
    'MONGODB_HOST',
    'MONGODB_IS_MOCK',
    'MONGODB_PASSWORD',
    'MONGODB_PORT',
    'MONGODB_USERNAME',
    'MONGODB_CONNECT',
    'MONGODB_TZ_AWARE',
)


class InvalidSettingsError(Exception):
    pass


def _sanitize_settings(settings: Dict) -> Dict:
    """Given a dict of connection settings, sanitize the keys and fall
    back to some sane defaults.
    """
    # Remove the 'MONGODB_' prefix and make all settings keys lower case.
    resolved_settings = {}
    for k, v in settings.items():
        if k.startswith('MONGODB_'):
            k = k[len('MONGODB_'):]
        k = k.lower()
        resolved_settings[k] = v

    # Handle uri style connections
    if '://' in resolved_settings.get('host', ''):
        # PyMongo requires URI to start with mongodb:// to parse
        # this workaround allows mongomock to work
        uri_to_check = resolved_settings['host']

        if uri_to_check.startswith('mongomock://'):
            uri_to_check = uri_to_check.replace('mongomock://', 'mongodb://')

        uri_dict = uri_parser.parse_uri(uri_to_check)
        resolved_settings['db'] = uri_dict['database']

    # Add a default name param or use the "db" key if exists
    if resolved_settings.get('db'):
        resolved_settings['name'] = resolved_settings.pop('db')
    else:
        resolved_settings['name'] = 'test'

    # Add various default values.
    resolved_settings['alias'] = resolved_settings.get(
        'alias', mongoengine.DEFAULT_CONNECTION_NAME
    )
    resolved_settings['host'] = resolved_settings.get(
        'host', 'localhost'
    )
    resolved_settings['port'] = resolved_settings.get(
        'port', 27017
    )
    # Default to ReadPreference.PRIMARY if no read_preference is supplied
    resolved_settings['read_preference'] = resolved_settings.get(
        'read_preference', ReadPreference.PRIMARY
    )

    # Clean up empty values
    for k, v in list(resolved_settings.items()):
        if v is None:
            del resolved_settings[k]

    return resolved_settings


def get_connection_settings(config: Dict) -> Dict:
    """
    Given a config dict, returns a sanitized dict of connection settings.

    MongoDB Wire protocol compatible database settings should exist in
    a "MONGODB_SETTINGS" section/key in the initialization file/dictionary.
    for backward compactibility we also support several config keys
    prefixed by "MONGODB_", e.g. "MONGODB_HOST", "MONGODB_PORT", etc.
    """
    # Sanitize all the settings living under a "MONGODB_SETTINGS" config var
    if 'MONGODB_SETTINGS' in config:
        settings = config['MONGODB_SETTINGS']
        return _sanitize_settings(settings)
    # If "MONGODB_SETTINGS" doesn't exist, sanitize the "MONGODB_" keys
    # as if they all describe a single connection
    else:
        config = dict(
            (k, v)
            for k, v in config.items()
            if k in MONGODB_CONF_VARS
        )
        return _sanitize_settings(config)


def create_connections(config):
    """Given Flask application's config dict, extract relevant config vars
    out of it and establish MongoEngine connection(s) based on them.
    """
    # Validate that the config is a dict
    if config is None or not isinstance(config, dict):
        raise InvalidSettingsError('Invalid application configuration')

    # Get sanitized connection settings based on the config
    conn_settings = get_connection_settings(config)
    return _connect(conn_settings)


def _connect(conn_settings):
    """Given a dict of connection settings, create a connection to
    MongoDB by calling mongoengine.connect and return its result.
    """
    db_name = conn_settings.pop('name')
    return mongoengine.connect(db_name, **conn_settings)
