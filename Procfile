web: gunicorn commerce.wsgi --log-file - --log-level debug
python manage.py collectstatic --noinput
manage.py migrate --run-syncdb
python stat.py
