import base64
import binascii
import configparser
import json
import logging
import os
import sys

from rental_be.config import settings                                           # noqa F401


# Configure Flask app based on APP_ENV env var
RENTAL_BE_ENV = os.environ.get('RENTAL_BE_ENV', 'Dev')

_current_config = getattr(sys.modules['rental_be.config.settings'],
                          f'{RENTAL_BE_ENV}Config')()

_secrets = configparser.ConfigParser()
_secrets.read(os.environ.get('SECRET_PATH', 'rental_be/config/secrets.ini'))
if not _secrets.sections():
    logging.warning('No secret file found!')


for attrib in [x for x in dir(_current_config) if '__' not in x]:
    # NOTE: vars in secrets take precedence
    # NOTE: env vars in secrets has second priority
    if _secrets.sections() and attrib in _secrets['BaseConfig']:
        value = _secrets['BaseConfig'][attrib]
    else:
        value = os.environ.get(attrib, getattr(_current_config, attrib))
    setattr(sys.modules[__name__], attrib, value)

# NOTE: If `MONGODB_SETTINGS` is a base64 encoded JSON string convert to dict
mongodb_b64 = getattr(sys.modules[__name__], 'MONGODB_SETTINGS')
if isinstance(mongodb_b64, str):
    try:
        mongodb_json = base64.b64decode(mongodb_b64).decode()
        mongodb_dict = json.loads(mongodb_json)
        if not isinstance(mongodb_dict, dict):
            logging.error(
                '`MONGODB_SETTINGS` value is not of type dict: %s',
                mongodb_dict
            )
            raise Exception('`MONGODB_SETTINGS` value is not of type dict')
        setattr(sys.modules[__name__], 'MONGODB_SETTINGS', mongodb_dict)
    except binascii.Error as err:
        logging.error(
            'Error decoding base64 decoded string for `MONGODB_SETTINGS`: %s',
            err
        )
        sys.exit(1)
    except json.decoder.JSONDecodeError:
        logging.error(
            'Invalid JSON string value for `MONGODB_SETTINGS`: %s',
            mongodb_json,
        )
        sys.exit(1)
    except Exception as excp:
        logging.error(excp)
        sys.exit(1)


def as_dict():
    """Dict representation of Flask app configuration

    :returns: dict
    """
    conf = {}
    for attrib in [x for x in dir(config) if '__' not in x]:                    # noqa F821
        value = getattr(config, attrib)                                         # noqa F821
        conf[attrib] = value
    return conf
