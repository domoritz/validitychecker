#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from django import get_version
from django.core.management import execute_from_command_line, LaxOptionParser
from django.core.management.base import BaseCommand


# Work out the project module name and root directory, assuming that this file
# is located at [project]/bin/manage.py
PROJECT_ROOT, PROJECT_MODULE_NAME = os.path.split(
                os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

#print "PROJECT_ROOT:", PROJECT_ROOT
#print "PROJECT_MODULE_NAME:", PROJECT_MODULE_NAME

# Check that the project module can be imported.
try:
    __import__(PROJECT_MODULE_NAME)
except ImportError:
    # Couldn't import the project, place it on the Python path and try again.
    sys.path.append(PROJECT_ROOT)
    try:
        __import__(PROJECT_MODULE_NAME)
    except ImportError:
        sys.stderr.write("Error: Can't import the \"%s\" project module." %
                         PROJECT_MODULE_NAME)
        sys.exit(1)

def has_settings_option():
    parser = LaxOptionParser(usage="%prog subcommand [options] [args]",
                             version=get_version(),
                             option_list=BaseCommand.option_list)
    try:
        options = parser.parse_args(sys.argv[:])[0]
    except:
        return False # Ignore any option errors at this point.
    return bool(options.settings)

if not has_settings_option() and not 'DJANGO_SETTINGS_MODULE' in os.environ:
    settings_module = '%s.conf.dev.settings' % PROJECT_MODULE_NAME
    os.environ['DJANGO_SETTINGS_MODULE'] = settings_module

print "Use settings:", os.environ['DJANGO_SETTINGS_MODULE']

os.environ['DJANGO_PROJECT_ROOT'] = PROJECT_ROOT

execute_from_command_line()

