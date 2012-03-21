#!/bin/sh
python manage.py reset djcelery &&
python manage.py reset validitychecker && 
python manage.py syncdb --noinput
