#!/bin/bash
DJANGODIR=/var/www/exhibia
 
echo "starting tornado as `whoami`"
 
# Activate the virtual environment
cd $DJANGODIR
source env/bin/activate
cd $DJANGODIR/app/websocket
 

# Start Tornado
exec ../../env/bin/python websocket.py