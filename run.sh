#!/bin/bash 
source ./venv/bin/activate
nohup python -u robot.py >./log/nohup.log 2>&1 &
# gunicorn robot:robot.wsgi
