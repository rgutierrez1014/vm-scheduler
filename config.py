from __future__ import unicode_literals
import os

from google.appengine.api import app_identity


def get_app_env():
    if os.environ.get('SERVER_SOFTWARE', '').startswith('Google'):
        if app_identity.get_application_id().endswith('-staging'):
            default_app_env = 'staging'
        else:
            default_app_env = 'production'
        app_env = os.environ.get('APP_ENV', default_app_env)
    else:
        app_env = 'development'
    return app_env

def get_config():
    config = {
        'app_env' : get_app_env(),
    }
    return config
