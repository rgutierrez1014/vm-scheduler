from __future__ import absolute_import, unicode_literals

import webapp2

from main import create_app


def setup_request_context(app=None, request=None):
    app = app or create_app()
    request = request or webapp2.Request.blank('/')
    request.app = app
    app.set_globals(app=app, request=request)
    return app, request
