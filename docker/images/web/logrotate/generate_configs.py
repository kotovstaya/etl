import os

LOG_DIRS = {
    '/webapp/logs/uwsgi/': 
''' {
    size 10M
    rotate 100000
    maxage 90
    missingok
    compress
    delaycompress
    copytruncate
    notifempty
    create 0640 root root
}
''',
    '/webapp/logs/':
''' {
    size 100M
    rotate 100000
    maxage 90
    missingok
    compress
    delaycompress
    notifempty
    create 0640 root root
}
''',
}

for dir, config in LOG_DIRS.items():
    log_files = filter(lambda x: x.endswith('.log'), os.listdir(dir))
    for log_file in log_files:
        config_path = os.path.join('/etc/logrotate.d/', log_file.replace('.log', ''))
        if not os.path.exists(config_path):
            with open(config_path, 'w') as f:
                f.write(os.path.join(dir, log_file) + config)

