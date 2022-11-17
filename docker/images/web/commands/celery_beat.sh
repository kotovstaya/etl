#!/bin/sh

set -e

celery -A src.celery beat --scheduler django_celery_beat.schedulers:DatabaseScheduler --loglevel=INFO --logfile=/webapp/logs/celery_beat.log
