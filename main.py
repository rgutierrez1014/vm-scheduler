from __future__ import unicode_literals
import os
import webapp2
import logging
import os

from google.appengine.api import app_identity
from webapp2_extras.routes import PathPrefixRoute as _PathPrefixRoute


class PathPrefixRoute(_PathPrefixRoute):
    @webapp2.cached_property
    def regex(self):
        regex, reverse_template, args_count, kwargs_count, variables = \
            webapp2._parse_route_template(self.prefix + '<:.*>')
        return regex

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
        'gcs_bucket' : 'teaching-commons-appfiles',
        'zip_folder' : 'documents/zip_files',
        'temp_zip_filename_pattern' : '{}_{}_materials_{}.zip', # .format(lesson_type, lesson_id, datetime.utcnow().strftime("%Y%m%dt%H%M%S"))
        'zip_filename_pattern' : '{}_{}_materials.zip', # .format(lesson_type, lesson_id)
        'zip_return_endpoint' : 'https://teaching-commons.appspot.com/admin/_incoming/zip_archive/',
        'signature_max_age' : 600 # age in seconds
    }
    if config['app_env'] == 'staging':
        config['zip_return_endpoint'] = 'https://teaching-commons-staging.appspot.com/admin/_incoming/zip_archive/'
        config['gcs_bucket'] = 'teaching-commons-staging.appspot.com'
    if config['app_env'] == 'development':
        config['gcs_bucket'] = 'dev__{}'.format(config['gcs_bucket'])
        config['zip_return_endpoint'] = 'http://localhost:8000/admin/_incoming/zip_archive/'
    return config


class StartService(webapp2.RequestHandler):
    def get(self):
        logging.debug('Starting instance of service "services"')


class StopService(webapp2.RequestHandler):
    def get(self):
        logging.debug('Idle timeout reached, shutting down instance of service "services"')

routes = [
    PathPrefixRoute('/_services', [
        webapp2.Route('/zip_archive/do',
                handler='handlers.zip_archive.ZipArchiveHandler:do_zip_archive'),
        webapp2.Route('/zip_archive', methods=['POST'],
                handler='handlers.zip_archive.ZipArchiveHandler:post')
    ]),
    webapp2.Route('/_ah/start',
        handler=StartService),
    webapp2.Route('/_ah/stop',
        handler=StopService)
]
app = webapp2.WSGIApplication(routes=routes, config=get_config(), debug=True)
