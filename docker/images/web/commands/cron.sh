#!/usr/bin/env bash

set -e

touch /webapp/logs/cron.log
python3 /generate_configs.py
echo "" >> /cron.txt
crontab /cron.txt
cron && tail -f /webapp/logs/cron.log
