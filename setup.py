#!/usr/bin/env python
from distutils.core import setup
import py2exe, sys, os

# The default call is "python setup.py py2exe"
# With the line below, you just run "setup.py"
sys.argv.append('py2exe')

setup(
	console=[{'script': 'checkUrl.py'}],
	options = {'py2exe': {'bundle_files': 1, 'compressed': True}},
	zipfile = None,
)