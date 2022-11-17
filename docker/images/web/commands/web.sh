#!/bin/sh

set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

uwsgi --ini uwsgi.ini
