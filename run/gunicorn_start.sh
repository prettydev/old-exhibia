#!/bin/bash
DJANGODIR=/var/www/exhibia
USER=root # the user to run as
GROUP=root # the group to run as
NUM_WORKERS=5 # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE=settings # which settings file should Django use
DJANGO_WSGI_MODULE=wsgi # WSGI module name
 
echo "starting gunicorn as `whoami`"
 
# Activate the virtual environment
cd $DJANGODIR
source env/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH
 
# Start Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec env/bin/python manage.py run_gunicorn \
--bind=0.0.0.0:8000 \
--workers $NUM_WORKERS \
--user=$USER --group=$GROUP \
--log-level=debug \
--log-file=-