#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
from fabric.api import local, settings, abort, run, cd, env, prefix, sudo
from fabric.contrib.console import confirm


# http://readthedocs.org/docs/fabric/en/1.4.0/api/contrib/django.html

#################################
# Development
################################

def hello():
    print("Hello world!")

def start():
    """ run climate goggles """
    local("python ./bin/manage.py runserver")

def test():
    """ test the main app """
    local("python ./bin/manage.py test validitychecker")

def install():
    """ installs all dependencies """
    local("python ./bin/manage.py runserver")

def commit():
    """ commit changes """
    local("git add -p && git commit")


#################################
# Deployment
################################

env.hosts = ['yourdomain.com']
env.user = "your-user"

def update_django_project():
    """ Updates the remote django project.
    """
    with cd('/path/to/your/django/project'):
        run('git pull')
        run('pip install -r requirements.txt')
        with cd('bin'):
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
