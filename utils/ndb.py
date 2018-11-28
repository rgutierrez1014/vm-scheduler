from __future__ import absolute_import, unicode_literals
import logging
import os
import os.path
from functools import wraps

from google.appengine.api.files import records
from google.appengine.datastore import entity_pb
from google.appengine.ext import ndb


def require_key_name(value, optional=False):
    """Returns a key name from the given value, if possible."""
    if isinstance(value, ndb.Model):
        return value.key.id()
    elif isinstance(value, basestring):
        return value
    elif value is None and optional:
        return None
    else:
        raise ValueError('expected a model or key name')


def require_key(value, kind=None, optional=False):
    """Returns a key from the given value, if possible."""
    if isinstance(value, ndb.Model):
        key = value.key
    elif isinstance(value, ndb.Key):
        key = value
    elif value is None and optional:
        return None
    else:
        raise ValueError('expected a model or key')
    if kind and key.kind() != kind:
        raise ValueError('expected a key with kind %s; got %s' % (kind, key.kind()))
    return key


def require_entity(value, kind=None, optional=False):
    """Returns a entity from the given value, if possible."""
    if isinstance(value, ndb.Model):
        if kind and value.key.kind() != kind:
            raise ValueError('expected a key with kind %s; got %s' % (kind, entity.key.kind()))
        return value
    elif isinstance(value, ndb.Key):
        if kind and value.kind() != kind:
            raise ValueError('expected a key with kind %s; got %s' % (kind, value.kind()))
        entity = value.get()
        if entity is None:
            raise ValueError('no entity for given key')
        return entity
    elif value is None and optional:
        return None
    else:
        raise ValueError('expected a model or key')

def get_first(kind, query_param=None, query_eq='default_value'):
    '''Returns first object matching query_param == query_eq, or just first, or []'''
    if query_param and query_eq != 'default_value':
        query_result = kind.query(query_param == query_eq).fetch(limit=1)
        if query_result:
            return query_result[0]
        else:
            return []
    elif query_param and query_eq == 'default_value':
        raise ValueError('get_first requires both query_param & query_eq, or neither')
    elif not query_param and query_eq == 'default_value':
        return kind.query().get()
    else:
        raise ValueError('get_first requires both query_param & query_eq, or neither')


def entity_to_protobuf(e):
    return ndb.ModelAdapter().entity_to_pb(e).Encode()


def protobuf_to_entity(pb):
    return ndb.ModelAdapter().pb_to_entity(entity_pb.EntityProto(pb))


def _localize_key(key, app):
    if key:
        return ndb.Key(*key.flat(), app=app)
    else:
        return None


def _localize_key_properties(entity, app):
    if entity:
        entity.key = _localize_key(entity.key, app)
        for name, prop in entity._properties.items():
            if isinstance(prop, ndb.KeyProperty):
                if prop._repeated:
                    setattr(entity, name, [_localize_key(k, app) for k in getattr(entity, name)])
                else:
                    setattr(entity, name, _localize_key(getattr(entity, name), app))
            elif isinstance(prop, ndb.StructuredProperty):
                if prop._repeated:
                    for value in getattr(entity, name):
                        _localize_key_properties(value, app)
                else:
                    _localize_key_properties(getattr(entity, name), app)


def import_datastore_backup_file(filename):
    app = ndb.Key('Foo', 'Bar').app()
    kind = None
    i = 0
    raw = open(filename, 'r')
    reader = records.RecordsReader(raw)
    to_put = list()
    for record in reader:
        entity = protobuf_to_entity(record)
        _localize_key_properties(entity, app)
        kind = kind or entity.key.kind()
        to_put.append(entity)
        if len(to_put) == 100:
            ndb.put_multi(to_put)
            to_put = list()
            i += 100
    ndb.put_multi(to_put)
    i += len(to_put)
    logging.info('imported %d %s entities', i, kind)


def import_datastore_backup(path, y, m, d, include=None, exclude=None):
    files = []
    date_part = '%04d_%02d_%02d' % (y, m, d)
    for dirpath, dirnames, filenames in os.walk(path, onerror=lambda e: logging.exception(e), followlinks=True):
        for fn in filenames:
            filepath = os.path.join(dirpath, fn)
            if filepath.find(date_part) != -1:
                files.append(filepath)
    for filename in files:
        if include and not any(filename.find(x) != -1 for x in include):
            continue
        if exclude and any(filename.find(x) != -1 for x in exclude):
            continue
        logging.info('importing from file %s', filename)
        import_datastore_backup_file(filename)

def batch_query(query, page_size=100):
    """Generator that fetches all entities for the given query a page at a time,
    and yields the resulting entities one at a time."""
    entities, cursor, more = query.fetch_page(page_size)
    while entities:
        for e in entities:
            yield e
        entities, cursor, more = query.fetch_page(page_size, start_cursor=cursor)

def batch_update(query, update_fn, page_size=100):
    """Fetches all entities for the given query a page at a time,
    applies the given update function to each entitity, and
    puts the updated entities.  The update function is expected to
    mutate entities."""
    entities, cursor, more = query.fetch_page(page_size)
    while entities:
        for e in entities:
            update_fn(e)
        ndb.put_multi(entities)
        entities, cursor, more = query.fetch_page(page_size, start_cursor=cursor)

def paged_iterator(query, batch_size=50):
    '''
    Sort of like batch_update, but a decorator.
    Wraps function `func` around provided query.
    Does not save changes (or do anything else) by default.
    Write func as if it were just taking all of the objects. e.g., 
    to print every Person key:

    @paged_iterator(Person.query())
    def print_keys(persons):
        for person in persons:
            print person.key

    [...]
    >>> print_keys()
    ndb.Key('Person', 'abcd...')
    ndb.Key('Person', 'efgh...')
    '''
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            objects, next_cursor, more = query.fetch_page(batch_size)
            while objects:
                func(objects)
                if more and next_cursor:
                    objects, next_cursor, more = query.fetch_page(batch_size, start_cursor=next_cursor)
                else:
                    break
        return wrapper
    return decorator
