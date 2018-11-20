from __future__ import unicode_literals
import logging
import json
import traceback
import webapp2

from google.appengine.api import urlfetch, urlfetch_errors


class BaseHandler(webapp2.RequestHandler):

    def handle_exception(self, exception, debug):
        logging.exception(exception)
        resp_dict = {
            'status' : 'failure',
            'result' : traceback.format_exc().splitlines()[-1]
        }
        if isinstance(exception, webapp2.HTTPException):
            self.response.set_status(exception.code)
        else:
            self.response.set_status(500)
        self.write_json(resp_dict)

    def write_json(self, value):
        """
        Convert the value to JSON, then write to response.
        This will mostly be used by API handlers.
        """
        response = json.dumps(value)
        self.response.headers[b'Content-Type'] = b'application/json'
        self.response.write(response)
