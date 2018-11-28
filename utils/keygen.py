import base64
import string
import uuid

from utils import crockford


def generate_key():
    return crockford.b32encode(uuid.uuid4().bytes)
