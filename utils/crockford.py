"""Encode and decode using Douglas Crockford's base32 encoding scheme.

Note that these functions return and expect unpadded encoded strings.

Adapted from https://github.com/ingydotnet/crockford-py
"""

import base64
import string
import uuid

from utils.strings import to_unicode, to_bytes


__STD_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
__CROCKFORD_CHARS = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'
__STD_TO_CROCKFORD = string.maketrans(__STD_CHARS, __CROCKFORD_CHARS)
__CROCKFORD_TO_STD = string.maketrans(__CROCKFORD_CHARS, __STD_CHARS)


def b32encode(s):
    s = to_bytes(s)
    return to_unicode(base64.b32encode(s).translate(__STD_TO_CROCKFORD, '='))


def b32decode(s):
    s = to_bytes(s).upper()
    s += '=' * ((8 - len(s) % 8) % 8)
    return base64.b32decode(s.translate(__CROCKFORD_TO_STD))


def isvalidb32(s):
    s = to_bytes(s).upper()
    return all(c in __CROCKFORD_CHARS for c in s)
