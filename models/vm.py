from __future__ import absolute_import, unicode_literals
from datetime import datetime, timedelta, date
import logging

from google.appengine.ext import ndb

from models.base import BaseModel, TimestampedModel

from utils.ndb import require_entity, require_key


class VM(BaseModel, TimestampedModel):
    """
    A small model representing a Compute Engine VM, as
    well as some associated properties.

    Key('VM', 'vm-instance-name')
    """
    instance_name = ndb.ComputedProperty(lambda self: self.key.id())
    deployment_name = ndb.StringProperty(required=True)
    expires_at = ndb.DateTimeProperty(required=True)

    @classmethod
    def create(cls, id, **kwargs):
        """
        Because the key id of a VM model is the Compute
        Engine instance name, we want to make sure it is
        always supplied to the create method.
        """
        if not isinstance(id, basestring):
            raise ValueError("'id' must be of type basestring")
        kwargs['id'] = id
        return super(VM, self).create(**kwargs)
