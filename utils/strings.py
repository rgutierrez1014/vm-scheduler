from __future__ import absolute_import, unicode_literals


def isbasestring(obj):
    """Determine if obj is a byte string or unicode string"""
    return isinstance(obj, basestring)


def isbytestring(obj):
    """Determine if obj is a byte string"""
    return isinstance(obj, str)


def isunicodestring(obj):
    """Determine if obj is a unicode string"""
    return isinstance(obj, unicode)


def to_unicode(obj):
    """Convert a given object to a unicode string"""
    if isunicodestring(obj):
        return obj
    elif isbytestring(obj):
        return unicode(obj, 'utf-8')
    else:
        raise TypeError('expected a byte or unicode string')


def to_bytes(obj):
    """Convert a given object to a byte string"""
    if isbytestring(obj):
        return obj
    elif isunicodestring(obj):
        return obj.encode('utf-8')
    else:
        raise TypeError('expected a byte or unicode string')


def is_blank(obj):
    """Return True if obj is None or a blank string, False otherwise
    """
    if obj is None:
        return True
    elif isbasestring(obj):
        return obj.strip() == ''
    else:
        return False


def str_to_bool(s):
    if isinstance(s, bool):
        return s
    if not isinstance(s, basestring):
        raise ValueError('Argument must be of type basestring')
    true_values = ['true', 't', 'yes', 'y', '1']
    false_values = ['false', 'f', 'no', 'n', '0']
    if s.lower() in true_values:
        return True
    elif s.lower() in false_values:
        return False
    else:
        msg = 'Unable to convert {} to a bool. ' \
                'Accepted values are: True => {}, False => {}' \
                .format([s, true_values, false_values])
        raise ValueError(msg)


def bool_display(b):
    if b == True:
        return 'yes'
    elif b == False:
        return 'no'
    else:
        raise ValueError('Unrecognized value: {}'.format(b))
