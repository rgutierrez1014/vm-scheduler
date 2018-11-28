from __future__ import absolute_import, unicode_literals
import datetime
import functools
import json

import pytz


def parse_datetime(dt):
    pass


def format_datetime(dt):
    pass


def parse_date(dt):
    pass


def format_date(dt):
    pass


def parse_date(s):
    if s:
        return datetime.datetime.strptime(s, '%Y-%m-%d').date()
    else:
        return None


def parse_datetime(s, with_tzinfo=False):
    if s:
        dt = datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ')
        return pytz.utc.localize(dt) if with_tzinfo else dt
    else:
        return None


def format_date(d):
    if d:
        return d.strftime('%Y-%m-%d')
    else:
        return None


def format_datetime(dt):
    if dt:
        if dt.tzinfo:
            dt = dt.astimezone(pytz.utc)
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    else:
        return None


class FancyJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(datetime, obj):
            return format_datetime(obj)
        elif isinstance(date, obj):
            return format_date(obj)
        else:
            return json.JSONEncoder.default(self, obj)


dump = functools.partial(json.dump, cls=FancyJsonEncoder)

dumps = functools.partial(json.dumps, cls=FancyJsonEncoder)

load = json.load

loads = json.loads
