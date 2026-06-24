#!/bin/bash
# verify_backups.sh - Проверка целостности бэкапов

BACKUP_DIR="/backups/postgresql"
LOG_FILE="/var/log/backup_verify.log"

echo "$(date) - Проверка целостности" >> $LOG_FILE

for dump in $(find $BACKUP_DIR -name "*.dump.zst" -mtime -7); do
    zstd -d -c $dump | pg_restore --list > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ $dump - OK" >> $LOG_FILE
    else
        echo "❌ $dump - ПОВРЕЖДЕН!" >> $LOG_FILE
        # Отправка алерта
        curl -X POST -H 'Content-type: application/json' \
             --data '{"text":"Поврежден бэкап: '"$dump"'"}' \
             https://hooks.slack.com/services/YOUR/WEBHOOK/URL
    fi
done