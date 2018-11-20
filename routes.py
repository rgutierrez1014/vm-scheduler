from __future__ import unicode_literals
import webapp2
import logging

from webapp2_extras.routes import PathPrefixRoute as _PathPrefixRoute


class PathPrefixRoute(_PathPrefixRoute):
    @webapp2.cached_property
    def regex(self):
        regex, reverse_template, args_count, kwargs_count, variables = \
            webapp2._parse_route_template(self.prefix + '<:.*>')
        return regex


class StartService(webapp2.RequestHandler):
    def get(self):
        logging.debug('Starting instance of service "default"')


class StopService(webapp2.RequestHandler):
    def get(self):
        logging.debug('Idle timeout reached, shutting down instance of service "default"')

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
