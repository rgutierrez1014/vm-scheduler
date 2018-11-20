#!/usr/bin/env python

import subprocess


subprocess.call('pip install -U -t lib -r requirements.txt --no-deps'.split(' '))
subprocess.call('pip install -U -t local -r requirements-dev.txt'.split(' '))
