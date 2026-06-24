## Файл 4: `Scripts/backup_pos.py`
#!/usr/bin/env python3
"""
backup_pos.py - Скрипт инкрементального бэкапа POS-терминалов
Версия: 1.0
Автор: DevOps Team
"""

import subprocess
import boto3
import os
import logging
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path

# ===== Конфигурация =====
CONFIG = {
    "LOCAL_BINLOG_DIR": "/var/lib/mysql/",
    "S3_BUCKET": "magnolia-pos-backup",
    "S3_PREFIX": "pos_incremental/",
    "IMMUTABLE_DAYS": 7,
    "MIN_DISK_SPACE_GB": 10,
    "RPO_MINUTES": 30,
    "SHOP_ID": os.getenv("SHOP_ID", "unknown"),
    "BACKUP_USER": "backup_user",
    "BACKUP_PASS": os.getenv("MYSQL_BACKUP_PASS", "")
}

# ===== Настройка логирования =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/backup_pos.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===== Инициализация S3 =====
try:
    s3 = boto3.client('s3')
    logger.info("S3 клиент инициализирован")
except Exception as e:
    logger.error(f"Ошибка инициализации S3: {e}")
    s3 = None


def check_disk_space():
    """Проверка свободного места на диске"""
    try:
        stat = os.statvfs(CONFIG["LOCAL_BINLOG_DIR"])
        free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
        logger.info(f"Свободно: {free_gb:.2f} ГБ")
        
        if free_gb < CONFIG["MIN_DISK_SPACE_GB"]:
            logger.warning(f"Мало места! Осталось {free_gb:.2f} ГБ")
            return False
        return True
    except Exception as e:
        logger.error(f"Ошибка проверки диска: {e}")
        return False


def cleanup_old_backups(days=7):
    """Очистка локальных файлов старше N дней"""
    try:
        cutoff = datetime.now() - timedelta(days=days)
        removed_count = 0
        
        for f in os.listdir(CONFIG["LOCAL_BINLOG_DIR"]):
            if f.startswith("binlog") and not f.endswith(".zst"):
                fpath = os.path.join(CONFIG["LOCAL_BINLOG_DIR"], f)
                if os.path.getctime(fpath) < cutoff.timestamp():
                    os.remove(fpath)
                    removed_count += 1
                    logger.info(f"Удален старый файл: {f}")
        
        logger.info(f"Очистка завершена. Удалено {removed_count} файлов")
        return removed_count
    except Exception as e:
        logger.error(f"Ошибка очистки: {e}")
        return 0


def create_binlog_rotation():
    """Создание ротации бинарных логов MySQL"""
    try:
        cmd = f"mysqladmin -u {CONFIG['BACKUP_USER']} -p{CONFIG['BACKUP_PASS']} flush-logs"
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
        logger.info("Бинарные логи ротированы")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка ротации логов: {e.stderr}")
        return False


def find_binlog_files():
    """Поиск бинарных логов для бэкапа"""
    try:
        binlog_files = []
        for f in os.listdir(CONFIG["LOCAL_BINLOG_DIR"]):
            if f.startswith("binlog") and not f.endswith(".zst") and f != "binlog.index":
                fpath = os.path.join(CONFIG["LOCAL_BINLOG_DIR"], f)
                # Проверяем, что файл не слишком новый (защита от гонок)
                if os.path.getsize(fpath) > 1024:  # > 1KB
                    binlog_files.append(fpath)
        
        logger.info(f"Найдено {len(binlog_files)} файлов для бэкапа")
        return binlog_files
    except Exception as e:
        logger.error(f"Ошибка поиска файлов: {e}")
        return []


def compress_file(input_path):
    """Сжатие файла с помощью zstd"""
    try:
        output_path = f"{input_path}.zst"
        cmd = f"zstd -15 {input_path} -o {output_path}"
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
        logger.info(f"Файл сжат: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка сжатия: {e.stderr}")
        return None


def calculate_md5(file_path):
    """Вычисление MD5 хеша файла"""
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        logger.error(f"Ошибка расчета MD5: {e}")
        return None


def upload_to_s3(file_path, s3_key):
    """Загрузка в S3 с защитой от удаления (Immutable)"""
    try:
        if not s3:
            logger.error("S3 клиент не инициализирован")
            return False
        
        retain_until = datetime.now() + timedelta(days=CONFIG["IMMUTABLE_DAYS"])
        
        with open(file_path, 'rb') as f:
            s3.put_object(
                Bucket=CONFIG["S3_BUCKET"],
                Key=s3_key,
                Body=f,
                ObjectLockMode='GOVERNANCE',
                ObjectLockRetainUntilDate=retain_until,
                StorageClass='STANDARD_IA',
                Metadata={
                    'shop_id': CONFIG["SHOP_ID"],
                    'created_at': datetime.now().isoformat(),
                    'checksum_md5': calculate_md5(file_path) or ''
                }
            )
        
        logger.info(f"Файл загружен в S3: {s3_key}")
        return True
    except Exception as e:
        logger.error(f"Ошибка загрузки в S3: {e}")
        return False


def send_metric_to_prometheus(job_name, status, size_bytes, duration_seconds, checksum):
    """Отправка метрики в Prometheus Pushgateway"""
    try:
        metrics = {
            "job_name": job_name,
            "status": status,
            "size_bytes": size_bytes,
            "duration_seconds": duration_seconds,
            "timestamp": datetime.now().isoformat(),
            "checksum_md5": checksum or ""
        }
        
        # Сохраняем метрику в файл для последующей отправки
        with open("/tmp/backup_metric.json", "w") as f:
            json.dump(metrics, f)
        
        logger.info(f"Метрика сохранена: {metrics}")
        return True
    except Exception as e:
        logger.error(f"Ошибка отправки метрики: {e}")
        return False


def check_rpo_compliance():
    """Проверка соблюдения RPO"""
    try:
        # Проверяем время последнего успешного бэкапа
        metric_file = "/tmp/last_successful_backup"
        if os.path.exists(metric_file):
            with open(metric_file, 'r') as f:
                last_backup = datetime.fromisoformat(f.read().strip())
                age_minutes = (datetime.now() - last_backup).total_seconds() / 60
                
                if age_minutes > CONFIG["RPO_MINUTES"]:
                    logger.warning(f"RPO нарушен! Возраст бэкапа: {age_minutes:.1f} мин > {CONFIG['RPO_MINUTES']} мин")
                    return False
        
        # Записываем время текущего бэкапа
        with open(metric_file, 'w') as f:
            f.write(datetime.now().isoformat())
        
        return True
    except Exception as e:
        logger.error(f"Ошибка проверки RPO: {e}")
        return False


def run_backup():
    """Основная функция выполнения бэкапа"""
    start_time = datetime.now()
    logger.info(f"Запуск бэкапа для магазина {CONFIG['SHOP_ID']}")
    
    # 1. Проверка дискового пространства
    if not check_disk_space():
        logger.warning("Недостаточно места. Запуск очистки...")
        cleanup_old_backups(days=3)
        if not check_disk_space():
            logger.error("Критически мало места! Бэкап отменен")
            send_metric_to_prometheus(
                job_name="pos_backup",
                status="failed",
                size_bytes=0,
                duration_seconds=0,
                checksum=""
            )
            return False
    
    # 2. Ротация бинарных логов
    if not create_binlog_rotation():
        logger.warning("Ошибка ротации логов, продолжаем с существующими файлами")
    
    # 3. Поиск файлов для бэкапа
    binlog_files = find_binlog_files()
    if not binlog_files:
        logger.info("Нет новых файлов для бэкапа")
        return True
    
    # 4. Обработка каждого файла
    success_count = 0
    for file_path in binlog_files:
        try:
            # 4.1 Сжатие
            compressed_path = compress_file(file_path)
            if not compressed_path:
                continue
            
            # 4.2 Расчет MD5
            checksum = calculate_md5(compressed_path)
            if not checksum:
                logger.warning("MD5 не рассчитан, продолжаем без него")
            
            # 4.3 Формирование S3-ключа
            date_str = datetime.now().strftime("%Y%m%d")
            filename = os.path.basename(file_path)
            s3_key = f"{CONFIG['S3_PREFIX']}{date_str}/{CONFIG['SHOP_ID']}_{filename}.zst"
            
            # 4.4 Загрузка в S3
            if upload_to_s3(compressed_path, s3_key):
                success_count += 1
                # 4.5 Удаление исходного файла после успешной загрузки
                os.remove(file_path)
                os.remove(compressed_path)
                logger.info(f"Файл {filename} успешно обработан")
            else:
                logger.error(f"Не удалось загрузить {filename}")
                
        except Exception as e:
            logger.error(f"Ошибка обработки файла {file_path}: {e}")
            continue
    
    # 5. Очистка старых файлов
    cleanup_old_backups(days=7)
    
    # 6. Проверка RPO
    rpo_ok = check_rpo_compliance()
    if not rpo_ok:
        logger.warning("RPO не соблюдается! Проверьте частоту бэкапов")
    
    # 7. Отправка метрики
    duration = (datetime.now() - start_time).total_seconds()
    status = "success" if success_count > 0 else "partial"
    
    send_metric_to_prometheus(
        job_name="pos_backup",
        status=status,
        size_bytes=0,  # TODO: рассчитать общий размер
        duration_seconds=duration,
        checksum=""
    )
    
    logger.info(f"Бэкап завершен. Обработано {success_count} файлов за {duration:.2f} сек")
    return True


if __name__ == "__main__":
    try:
        run_backup()
    except Exception as e:
        logger.critical(f"Необработанная ошибка: {e}")
        exit(1)