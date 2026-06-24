#!/bin/bash
# backup_wms.sh - Скрипт для бэкапа WMS (PostgreSQL)
# Версия: 1.0

set -e

# ===== Конфигурация =====
DB_NAME="wms_production"
DB_USER="backup_user"
DB_PASS="${DB_PASS:-password}"
BACKUP_DIR="/backup/wms"
S3_BUCKET="magnolia-backup"
S3_PREFIX="postgresql/wms/"
RETENTION_DAYS=30
LOG_FILE="/var/log/backup_wms.log"

# ===== Функция логирования =====
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# ===== Проверка дискового пространства =====
check_disk_space() {
    local free_gb=$(df -BG "$BACKUP_DIR" | tail -1 | awk '{print $4}' | sed 's/G//')
    if [ "$free_gb" -lt 50 ]; then
        log "ERROR: Недостаточно места на диске (${free_gb}GB)"
        return 1
    fi
    log "Свободно на диске: ${free_gb}GB"
    return 0
}

# ===== Создание полного бэкапа =====
create_full_backup() {
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_file="${BACKUP_DIR}/full_${timestamp}.dump.zst"
    
    log "Создание полного бэкапа..."
    
    # Создание дампа
    PGPASSWORD="$DB_PASS" pg_dump -U "$DB_USER" -h localhost \
        -F c -b -v "$DB_NAME" | zstd -15 > "$backup_file"
    
    if [ $? -eq 0 ]; then
        log "Полный бэкап создан: $backup_file"
        echo "$backup_file"
    else
        log "Ошибка создания полного бэкапа"
        return 1
    fi
}

# ===== WAL-архивация =====
archive_wal() {
    local wal_dir="/var/lib/postgresql/wal_archive"
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    
    log "Архивация WAL-файлов..."
    
    # Сбор WAL-файлов за последний час
    find "$wal_dir" -name "*.wal" -mmin -60 -type f | while read wal_file; do
        local filename=$(basename "$wal_file")
        local compressed_file="${BACKUP_DIR}/wal_${timestamp}_${filename}.zst"
        
        # Сжатие
        zstd -15 "$wal_file" -o "$compressed_file"
        
        # Загрузка в S3
        aws s3 cp "$compressed_file" \
            "s3://${S3_BUCKET}/${S3_PREFIX}wal/${timestamp}/${filename}.zst" \
            --storage-class STANDARD_IA
        
        if [ $? -eq 0 ]; then
            log "WAL-файл загружен: $filename"
            rm -f "$wal_file"  # Удаляем после загрузки
        else
            log "ERROR: Ошибка загрузки WAL-файла: $filename"
        fi
        
        rm -f "$compressed_file"
    done
}

# ===== Загрузка в S3 =====
upload_to_s3() {
    local file="$1"
    local s3_key="$2"
    
    log "Загрузка в S3: $s3_key"
    
    aws s3 cp "$file" "s3://${S3_BUCKET}/${s3_key}" \
        --storage-class STANDARD_IA \
        --metadata "{\"created_at\":\"$(date -Iseconds)\"}"
    
    return $?
}

# ===== Очистка старых бэкапов =====
cleanup_old() {
    log "Очистка бэкапов старше ${RETENTION_DAYS} дней..."
    
    find "$BACKUP_DIR" -name "*.zst" -mtime +$RETENTION_DAYS -type f -delete
    log "Очистка завершена"
}

# ===== Основная функция =====
main() {
    log "=========================================="
    log "Запуск бэкапа WMS"
    
    # 1. Проверка диска
    check_disk_space || exit 1
    
    # 2. Создание директории для бэкапов
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$BACKUP_DIR/wal"
    
    # 3. Создание полного бэкапа (если нужно)
    if [ "$1" == "full" ] || [ ! -f "$BACKUP_DIR/latest_full.dump.zst" ]; then
        local full_backup=$(create_full_backup)
        if [ $? -eq 0 ]; then
            ln -sf "$full_backup" "$BACKUP_DIR/latest_full.dump.zst"
            
            # Загрузка в S3
            upload_to_s3 "$full_backup" "${S3_PREFIX}full/$(basename $full_backup)"
        fi
    fi
    
    # 4. WAL-архивация
    archive_wal
    
    # 5. Очистка
    cleanup_old
    
    # 6. Отправка метрики
    echo "wms_backup_status 1" > /var/lib/node_exporter/textfile/wms_backup.prom
    echo "wms_backup_timestamp $(date +%s)" >> /var/lib/node_exporter/textfile/wms_backup.prom
    
    log "Бэкап WMS завершен успешно"
    log "=========================================="
}

# ===== Запуск =====
main "$@"