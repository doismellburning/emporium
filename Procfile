web: gunicorn --chdir emporium --bind [::]:$PORT emporium.wsgi
worker: emporium/manage.py rqworker default
