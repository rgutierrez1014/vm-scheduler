#!/usr/bin/env python

import subprocess


try:
    subprocess.call('dev_appserver.py app.yaml --admin_port 8001'.split(' '))
except KeyboardInterrupt:
    pass
