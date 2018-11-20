from __future__ import absolute_import, unicode_literals
from datetime import datetime
import logging

from google.appengine.api import users
import webapp2
from webapp2_extras import i18n
from webapp2_extras import jinja2
from webapp2_extras import json
from webapp2_extras import sessions

import utils.jinja2.filters
from utils.strings import bool_display


def get_flashes():
    """
    A standalone method to get flashes from the current session.
    It is suitable for use as a template global.
    """
    session_store = sessions.get_store()
    session = session_store.get_session()
    return session.get_flashes()


class BaseFrontendHandler(webapp2.RequestHandler):
    """
    Base handler for requests that render HTML pages.
    """

    def dispatch(self):
        self.session_store = sessions.get_store(request=self.request)
        if self.current_user:
            logging.debug('current_user=%s', self.current_user.email())
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    def handle_exception(self, exception, debug):
        logging.exception(exception)
        if isinstance(exception, webapp2.HTTPException):
            self.response.set_status(exception.code)
        else:
            self.response.set_status(500)
        self.render_response('errors/base.html',
                exception=exception,
                exception_code=exception_code,
                request=self.request,
                now=datetime.utcnow())

    def write_json(self, value):
        """
        Convert the value to JSON, then write to response.
        This will mostly be used by API handlers.
        """
        response = json.dumps(value)
        self.response.headers[b'Content-Type'] = b'application/json'
        self.response.write(response)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session()

    def add_flash(self, message, level=None):
        self.session.add_flash(message, level)

    def jinja2_factory(self, app):
        j = jinja2.Jinja2(app)
        j.environment.globals.update({
            'APP_ENV': app.config['app_env'],
            'uri_for': webapp2.uri_for,
            'get_flashes': get_flashes
            })
        j.environment.filters.update({
            'get_entity': utils.jinja2.filters.get_entity,
            'tojson': utils.jinja2.filters.tojson,
            'rebase_datetime': utils.jinja2.filters.rebase_datetime,
            'bool_display': bool_display
            })
        return j

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app, factory=self.jinja2_factory, key='base.jinja2')

    @webapp2.cached_property
    def i18n(self):
        return i18n.get_i18n(request=self.request)

    @webapp2.cached_property
    def current_user(self):
        return users.get_current_user()

    def render_response(self, template, **context):
        """Renders a template and writes the result to the response."""
        context.update({
            'current_user': self.current_user,
            'logout_url': users.create_logout_url('/')
            })
        context.setdefault('now', datetime.utcnow())
        rv = self.jinja2.render_template(template, **context)
        self.response.write(rv)
