from __future__ import unicode_literals

import os
from google.appengine.ext import blobstore
from google.appengine.api import app_identity


class BlobFile(object):
    """
    Contains GCS filename and serving url
    GCS files can have a blobkey. A GCS blobkey does NOT have a BlobInfo object.
    A Blobfile entity is like a blobstore.BlobInfo object

    The incoming filename should be in the standard Cloud Storage
    format, which is "path/to/filename.extension".
    If the file is in the root bucket directory, it will just be
    "filename.extension"
    """

    def __init__(self, filename, bucket_name=None):
        """
        Use this method to instantiate
        """
        if not filename:
            raise ValueError("Unable to determine file name from {}. A non-zero-length string must be provided.".format(repr(filename)))
        if filename.startswith('/'):
            filename = filename[1:]
        self.filename = filename
        self.bucket = bucket_name or app_identity.get_default_gcs_bucket_name()
        self.gcs_filename = self.get_gcs_filename(self.filename, self.bucket)
        self.blobkey = self.get_blobkey(self.gcs_filename)

    def blob_reader(self):
        """
        a BlobInfo like open returns a BlobReader
        """
        return blobstore.BlobReader(blobstore.BlobKey(self.blobkey))

    @classmethod
    def get_gcs_filename(cls, filename, bucket):
        return '/{}/{}'.format(bucket, filename)

    @classmethod
    def get_blobkey(cls, gcs_filename):
        return blobstore.create_gs_key('/gs' + gcs_filename)
