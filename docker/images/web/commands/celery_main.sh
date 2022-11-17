#!/bin/sh

set -e

celery -A src.celery worker -n main --max-tasks-per-child=100 --max-memory-per-child=25000 --loglevel=INFO --logfile=/webapp/logs/celery_main.log
