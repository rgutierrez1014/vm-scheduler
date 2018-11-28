from __future__ import absolute_import, unicode_literals
from datetime import datetime
import logging

from handlers.base import BaseFrontendHandler


class HomeHandler(BaseFrontendHandler):
    def get(self):
        context = {}
        self.render_response('views/home/home.html', **context)
