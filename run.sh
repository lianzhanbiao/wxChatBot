#!/bin/bash 
source /home/lighthouse/WorkSpace/wxChatBot/venv/bin/activate
# nohup python -u robot.py >./log/nohup.log 2>&1 &
gunicorn -c /home/lighthouse/WorkSpace/wxChatBot/pygun.py main:app --log-level=debug --preload
