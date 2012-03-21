#!/bin/sh
python manage.py syncdb --noinput &&
python manage.py schemamigration validitychecker --auto &&
python manage.py migrate
