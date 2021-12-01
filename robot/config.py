#config.py
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1

backlog = 2048
worker_class = "eventlet"
worker_connections = 1000
daemon = True
pidfile = 'log/gunicorn.pid'
accesslog = 'log/access.log'
errorlog = 'log/gunicorn.log'

