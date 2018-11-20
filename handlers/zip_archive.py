from __future__ import unicode_literals

import os
import webapp2
import json
from datetime import datetime
import logging
import zipfile
import itsdangerous

import cloudstorage as gcs
from google.appengine.ext import blobstore
from google.appengine.api import taskqueue

from models import BlobFile
from handlers.base import BaseHandler


class ZipArchiveHandler(BaseHandler):
    """
    Class for creating a zip archive from a
    set of Cloud Storage files
    """

    def post(self):
        """
        Given a list of filenames, stream the files from
        Cloud Storage, save them into a ZIP file, then
        write the ZIP file to Cloud Storage.

        Expects JSON in the following format:
        {
            "lesson_type": "Offering",
            "lesson_id": 42
            "files": [
                "path/to/file1.docx",
                "path/to/file2.pptx"
            ]
        }

        Returns a JSON object which includes the status
        of the function and the Cloud Storage URL of the
        ZIP file.

        Returns:
        {
            "status": "success",
            "result": {
                "lesson_type": "Offering",
                "lesson_id": 42,
                "files": [
                    "path/to/offering_42_materials.zip"
                ]
            }
        }
        """
        secrets = {}
        logging.info(self.request.body, self.request.__dict__)
        with open('client_secrets.json', 'r') as f:
            secrets = json.load(f)
        api_key = secrets['api']['secret_key']
        max_age = self.app.config.get('signature_max_age', 600)
        s = itsdangerous.TimedSerializer(api_key)
        data = s.loads(self.request.body, max_age=max_age)
        try:
            lesson_type = data.pop('lesson_type')
            lesson_id = data.pop('lesson_id')
            files = data.pop('files')
        except KeyError as e:
            logging.exception(e)
            resp_dict = {
                'status' : 'failure',
                'result' : {
                    'lesson_type' : lesson_type,
                    'lesson_id' : lesson_id,
                    'message' : '{} not found in request body!'.format(str(e))
                }
            }
            self.response.set_status(400)
            self.write_json(resp_dict)
            return
        except:
            raise
        if not isinstance(files, list) or len(files) == 0:
            resp_dict = {
                'status' : 'failure',
                'result' : {
                    'lesson_type' : lesson_type,
                    'lesson_id' : lesson_id,
                    'message' : 'no file names were supplied!'
                }
            }
            self.response.set_status(400)
            self.write_json(resp_dict)
            return
        params = {
            'lesson_type' : lesson_type.lower(),
            'lesson_id': lesson_id,
            'files': files
        }
        the_retry_options = taskqueue.TaskRetryOptions(task_retry_limit=0)
        taskqueue.add(url='/_services/zip_archive/do', queue_name='zip-archive',
                params=params, retry_options=the_retry_options)
        resp_dict = {
            'status' : 'success',
            'result' : None
        }
        self.response.set_status(200)
        self.write_json(resp_dict)
        return

    def do_zip_archive(self):
        lesson_type = self.request.POST.get('lesson_type')
        lesson_id = self.request.POST.get('lesson_id')
        files = self.request.POST.getall('files')
        logging.info('Creating ZIP archive for %s %s with the following files: %s', lesson_type, lesson_id, files)
        zip_filename = self._blob_archive(lesson_type, lesson_id, files)
        resp_dict = {
            'status' : 'success',
            'result' : {
                'lesson_type' : lesson_type,
                'lesson_id' : lesson_id,
                'files' : [
                    zip_filename
                ]
            }
        }
        self.response.set_status(200)
        self.send_outbound_message(self.app.config['zip_return_endpoint'], resp_dict)

    def _blob_archive(self, lesson_type, lesson_id, files):
        blobfiles = []
        for f in files:
            blobfiles.append(BlobFile(f,
                    bucket_name=self.app.config['gcs_bucket']))
        temp_archive_filename = self.app.config['temp_zip_filename_pattern'].format(lesson_type, lesson_id, datetime.utcnow().strftime("%Y%m%dt%H%M%S"))
        temp_archive_file = os.path.join(self.app.config['zip_folder'], temp_archive_filename)
        archive_filename = self.app.config['zip_filename_pattern'].format(lesson_type, lesson_id)
        archive_file = os.path.join(self.app.config['zip_folder'], archive_filename)
        new_zf = BlobFile(temp_archive_file,
                bucket_name=self.app.config['gcs_bucket'])
        old_zf = BlobFile(archive_file,
                bucket_name=self.app.config['gcs_bucket'])
        # The cloudstorage library has a built-in retry mechanism,
        # so no need to specify it here
        with gcs.open(new_zf.gcs_filename, 'w', content_type=b'multipart/x-zip',
                options={b'x-goog-acl': b'public-read'}) as nzf:
            with zipfile.ZipFile(nzf, 'w') as zf:
                for gcs_file in blobfiles:
                    try:
                        blob = gcs_file.blob_reader().read()
                    except blobstore.BlobNotFoundError:
                        logging.exception('Unable to find file: %s', gcs_file.filename)
                        raise
                    except:
                        raise
                    gcs_file_basename = os.path.basename(gcs_file.filename)
                    logging.info('{} => {}'.format(gcs_file.filename, gcs_file_basename))
                    zf.writestr(gcs_file_basename.encode('utf-8'), blob)
        # Delete old zip
        try:
            gcs.delete(old_zf.gcs_filename)
        except gcs.NotFoundError:
            logging.info('{} does not exist'.format(old_zf.gcs_filename))
        except:
            raise
        # Copy temp zip to official zip name
        gcs.copy2(new_zf.gcs_filename, old_zf.gcs_filename, metadata={b'x-goog-acl': b'public-read', b'Content-Type': b'multipart/x-zip'})
        # Delete temp zip
        gcs.delete(new_zf.gcs_filename)
        # Return the zip filename
        # In this case, the zip filename we want to return will
        # be the same as the old zip filename
        return old_zf.filename
