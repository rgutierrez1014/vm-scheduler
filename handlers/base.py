from __future__ import unicode_literals
import logging
import json
import traceback
import time
import random
import webapp2

from google.appengine.api import urlfetch, urlfetch_errors
import itsdangerous


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

    def send_outbound_message(self, url, value):
        """
        Instead of returning a response, serialize some
        data and send a POST request to the specified
        url.
        """
        with open('client_secrets.json', 'r') as f:
            secrets = json.load(f)
        api_key = secrets['api']['secret_key']
        s = itsdangerous.TimedSerializer(api_key)
        signed = s.dumps(value)
        logging.info('Sending outbound message to the URL %s', url)
        retries = 0
        while True:
            try:
                post_result = urlfetch.fetch(
                        url,
                        payload=signed,
                        method=urlfetch.POST,
                        deadline=10,
                        follow_redirects=False)
                break
            except urlfetch_errors.DeadlineExceededError:
                if retries < 5:
                    logging.warning('Deadline exceeded while waiting for HTTP response from the URL %s', url)
                    # Apply exponential backoff.
                    time.sleep((2 ** retries) + random.randint(0, 1000) / 1000)
                    retries += 1
                    continue
                else:
                    raise
            except:
                raise
        logging.info('Successfully sent message')
        logging.info('Response: (%s) %s', post_result.status_code, post_result.content)
        self.response.set_status(200)
        return
