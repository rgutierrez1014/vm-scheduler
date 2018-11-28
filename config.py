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
        'webapp2_extras.sessions': {
            'secret_key': 'Tx\xb8m%\xe1a3\x9f\x8a\x8c\x12\xfe\xc2\x97\xb32\xd5!\xedF\xcf\xf6\xa4',
        },
        'webapp2_extras.i18n': {
            'default_locale': 'en_US',
            'default_timezone': 'America/Los_Angeles',
            'date_formats': {
                'time': 'medium',
                'date': 'medium',
                'datetime': 'medium',
                'time.short': 'h:mm a zzz',
                'time.medium': 'h:mm:ss a zzz',
                'time.full': None,
                'time.long': None,
                'date.short': 'M/dd/yyyy',
                'date.medium': None,
                'date.full': None,
                'date.long': None,
                'datetime.short': 'M/dd/yyyy h:mm a zzz',
                'datetime.medium': 'MMM d, yyyy h:mm:ss a zzz',
                'datetime.full': None,
                'datetime.long': None,
                },
        },
        'webapp2_extras.jinja2': {
            'environment_args': {
                'autoescape': True,
                'extensions': [
                    'jinja2.ext.autoescape',
                    'jinja2.ext.with_',
                    'jinja2.ext.i18n'
                ]
            }
        }
    }
    return config
