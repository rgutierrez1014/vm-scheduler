import logging

from google.appengine.ext import db
from google.appengine.ext import ndb

from utils.keygen import generate_key


class BaseModel(ndb.Model):
    @classmethod
    def generate_id(cls):
        return generate_key()

    @property
    def id(self):
        return self.key.id()

    @classmethod
    def get_key(cls, id):
        return ndb.Key(cls, id)

    @classmethod
    def create(cls, **kwargs):
        @ndb.transactional
        def attempt_insert(id):
            if kwargs.has_key('parent'):
                entity = cls.get_by_id(id, parent=kwargs['parent'])
            else:
                entity = cls.get_by_id(id)
            if entity is None:
                entity = cls(id=id, **kwargs)
                entity.put()
                return entity
            else:
                raise DuplicateKeyError("id '%s' is already in use" % id)
        entity = None
        tries = 0
        requested_id = kwargs.pop('id', None)
        if requested_id:
            entity = attempt_insert(requested_id)
        else:
            while entity is None:
                try:
                    entity = attempt_insert(cls.generate_id())
                except db.BadKeyError:
                    tries += 1
                    if tries >= 3:
                        raise
        return entity

    def update(self, **kwargs):
        for prop in kwargs:
            if prop in self._properties and \
                    prop not in ('key', 'id', 'parent', 'namespace'):
                setattr(self, prop, kwargs[prop])
        self.put()


class DuplicateKeyError(db.BadKeyError):
    pass


class TimestampedModel(ndb.Model):
    created_at = ndb.DateTimeProperty(auto_now_add=True, indexed=False)
    updated_at = ndb.DateTimeProperty(auto_now=True, indexed=False)
