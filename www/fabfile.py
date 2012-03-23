#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
from fabric.api import *

from fabric.contrib import django
import sys

# http://readthedocs.org/docs/fabric/en/1.4.0/api/contrib/django.html

#django.project('www')
#django.settings_module('www.dev.settings')

from django.conf import settings

# globals
BIN_DIRECTORY = 'bin'
NGINX_CONF = 'conf/nginx.conf'

#################################
# Development
################################


def hello():
    print("Hello world!")

def start():
    """ instructions """
    print """run in separate shells with active virtualenv:
        fab run_redis
        fab run_celeryd
        fab run_django
        fab run_celerycam"""

def run_redis():
    """ Run redis server """
    local("redis-server /usr/local/etc/redis.conf")

def run_celeryd():
    """ Run celeryd """
    with lcd(BIN_DIRECTORY):
        local("python manage.py celeryd -E -B -l INFO")

def run_django():
    """ Run django server """
    with lcd(BIN_DIRECTORY):
        local("python manage.py runserver")

def run_celerycam():
    """ Run celerycam """
    with lcd(BIN_DIRECTORY):
        local("python manage.py celerycam")

def run_django_production():
    """ runs the server in production mode """
    print "IN DEVELOPMENT"
    with lcd(BIN_DIRECTORY):
        local("python manage.py collectstatic")
        local("python manage.py compress --force")
        local("python manage.py run_gunicorn --workers 5")

def run_nginx():
    local("nginx -c %c" % NGINX_CONF)


def test():
    """ Test the main app """
    with lcd(BIN_DIRECTORY):
        result = local('python manage.py test validitychecker -v 2', capture=True)
    if result.failed and not confirm("Tests failed. Continue anyway?"):
        abort("Aborting at user request.")

def install():
    """ Installs all dependencies """
    if sys.platform == 'darwin':
        local("easy_install pip")
        local("brew install sqlite3 redis memcached nginx")
    else:
        sudo("apt-get install python python-pip sqlite3 redis memcached nginx")
    local("pip install -r requirements.txt")
    syncdb()
    migrate()

def syncdb():
    """ Django's syncdb """
    with lcd(BIN_DIRECTORY):
        local("python manage.py syncdb --noinput")

def migrate():
    """ Migrates the schema """
    with lcd(BIN_DIRECTORY):
        local("python manage.py schemamigration validitychecker --auto")
        local("python manage.py migrate")

def update_pip():
    """ updates all installed python modules installed with pip """
    local("pip freeze --local | cut -d = -f 1  | xargs echo pip install -U")

def redis():
    """ redis stuff """
    print "use redis-cli (INFO|DBSIZE|KEYS *|FLUSHDB|MONITOR) to get info, get size, get active keys, cleanup, monitor"

def drop():
    """ Drops all databases """
    with lcd(BIN_DIRECTORY):
        local("python manage.py reset djcelery validitychecker")
    local("redis-cli FLUSHDB")

def commit():
    """ Commit changes """
    local("git add -p && git commit")

def write_requirements():
    """ Write requirements to file """
    local("pip freeze > requirements.txt")

def collect_messages():
    """ Collects messages from files for translations """
    local("python %s/manage.py makemessages -l de" % BIN_DIRECTORY)
    print "now go to '/rosetta' for translations"

#################################
# Deployment
################################

env.hosts = ['yourdomain.com']
env.user = "www-data"

def invoke(comman):
    """ invoke a command on the remote """
    run(command)

def update_django_project():
    """ Updates the remote django project.
    """
    with cd('/path/to/your/django/project'):
        run('git pull')
        run('pip install -r requirements.txt')
        with cd('bin_directory'):
            run('python manage.py syncdb')
            run('python manage.py migrate') # if you use south
            run('python manage.py collectstatic --noinput')

def restart_webserver():
    """ Restarts remote nginx and uwsgi.
    """
    sudo("service uwsgi restart")
    sudo("/etc/init.d/nginx restart")

def deploy():
    code_dir = '/srv/django/myproject'
    with settings(warn_only=True):
        if run("test -d %s" % code_dir).failed:
            run("git clone user@vcshost:/path/to/repo/.git %s" % code_dir)
    with cd(code_dir):
        run("git pull")
        run("touch app.wsgi")


def host_type():
    """ get host type """
    run('uname -s')
