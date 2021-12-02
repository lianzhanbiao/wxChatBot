#!/bin/bash 
source ./venv/bin/activate
# nohup python -u robot.py >./log/nohup.log 2>&1 &
gunicorn -c pygun.py main:app --log-level=debug --preload
