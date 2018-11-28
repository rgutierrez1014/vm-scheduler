from __future__ import absolute_import, unicode_literals
from datetime import datetime
import json

from google.appengine.ext import ndb
import pytz
from webapp2_extras import i18n


def rebase_datetime(value, zone):
    """Rebases a datetime to the given timezone.
    """
    if not isinstance(value, datetime):
        return value
    if value.tzinfo is None:
        value = pytz.utc.localize(value)
    if isinstance(zone, basestring):
        try:
            tz = pytz.timezone(zone)
        except pytz.UnknownTimeZoneError:
            tz = None
    else:
        tz = None
    if tz:
        return value.astimezone(tz)
    else:
        return i18n.to_local_timezone(value)


def get_entity(key):
    """Get the Datastore entity for a given key.
    """
    if isinstance(key, ndb.Key):
        return key.get()
    else:
        return None


def tojson(value, **kwargs):
    """Encode the given value as JSON.
    """
    return json.dumps(value, **kwargs)

