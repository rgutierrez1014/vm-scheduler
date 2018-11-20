#!/usr/bin/env python

import os
import subprocess
import sys

parent_dir = os.path.dirname(os.path.dirname(__file__))
if os.path.exists(os.path.join(parent_dir, 'app.yaml')):
    app_root = os.path.abspath(parent_dir)
    sys.path.insert(0, os.path.join(app_root, 'local'))
    sys.path.insert(0, app_root)
else:
    raise RuntimeError('unable to determine application root directory')

import appdirs


APP_ID = 'vm-scheduler'
USER_DATA_DIR = appdirs.user_data_dir(APP_ID, 'vm-scheduler')


if not os.path.isdir(USER_DATA_DIR):
    os.makedirs(USER_DATA_DIR)


configs = ['dispatch.yaml']
modules = ['app.yaml']
options = [
        '--application', APP_ID,
        '--storage_path', os.path.join(USER_DATA_DIR, 'store'),
        '--allow_skipped_files', 'True'
        ]
options += sys.argv[1:]

args = ['dev_appserver.py'] + options + configs + modules

try:
    subprocess.call(args)
except KeyboardInterrupt:
    pass
