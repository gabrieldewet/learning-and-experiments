gunicorn --bind unix:/run/myproject/myproject.sock --workers 3 --user youruser --group www-data myproject.wsgi:application
