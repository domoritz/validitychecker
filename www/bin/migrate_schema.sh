#!/bin/sh
python manage.py syncdb &&
python manage.py schemamigration validitychecker --auto &&
python manage.py migrate
