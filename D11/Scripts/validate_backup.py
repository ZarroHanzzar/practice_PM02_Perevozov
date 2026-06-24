#!/usr/bin/env python3
"""
validate_backup.py - Проверка целостности бэкапов
Версия: 1.0
"""

import hashlib
import os
import json
import boto3
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BackupValidator:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.s3_resource = boto3.resource('s3')
        
    def validate_local_file(self, file_path, expected_md5):
        """Проверка MD5 локального файла"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            
            actual_md5 = hash_md5.hexdigest()
            is_valid = actual_md5 == expected_md5
            
            logger.info(f"Файл: {file_path}")
            logger.info(f"  Ожидаемый MD5: {expected_md5}")
            logger.info(f"  Фактический MD5: {actual_md5}")
            logger.info(f"  Статус: {'✅ OK' if is_valid else '❌ НЕ СОВПАДАЕТ'}")
            
            return is_valid
        except Exception as e:
            logger.error(f"Ошибка проверки файла {file_path}: {e}")
            return False
    
    def validate_s3_object(self, bucket, key, expected_md5=None):
        """Проверка целостности объекта в S3"""
        try:
            # Получаем ETag объекта (это MD5 для незашифрованных файлов)
            response = self.s3.head_object(Bucket=bucket, Key=key)
            etag = response['ETag'].strip('"')
            
            # Если ожидаемый MD5 передан, сравниваем
            if expected_md5:
                is_valid = etag == expected_md5
                logger.info(f"Объект S3: s3://{bucket}/{key}")
                logger.info(f"  ETag: {etag}")
                logger.info(f"  Ожидаемый: {expected_md5}")
                logger.info(f"  Статус: {'✅ OK' if is_valid else '❌ НЕ СОВПАДАЕТ'}")
                return is_valid
            else:
                logger.info(f"Объект S3: s3://{bucket}/{key} - ETag: {etag}")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка проверки объекта S3: {e}")
            return False
    
    def validate_backup_report(self, report_json_path):
        """Проверка отчета о бэкапе на соответствие JSON-схеме"""
        try:
            with open(report_json_path, 'r') as f:
                report = json.load(f)
            
            required_fields = [
                "job_name", "status", "size_bytes", 
                "duration_seconds", "timestamp", "checksum_md5"
            ]
            
            for field in required_fields:
                if field not in report:
                    logger.error(f"Отсутствует обязательное поле: {field}")
                    return False
            
            # Проверяем формат timestamp
            try:
                datetime.fromisoformat(report['timestamp'])
            except:
                logger.error(f"Неверный формат timestamp: {report['timestamp']}")
                return False
            
            # Проверяем формат MD5
            if len(report['checksum_md5']) != 32:
                logger.error(f"Неверный формат MD5: {report['checksum_md5']}")
                return False
            
            logger.info(f"✅ Отчет валиден: {report_json_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки отчета: {e}")
            return False
    
    def scan_and_validate(self, backup_dir, days=7):
        """Сканирование и проверка всех бэкапов в директории"""
        results = {
            "total": 0,
            "valid": 0,
            "invalid": 0,
            "errors": []
        }
        
        cutoff = datetime.now() - timedelta(days=days)
        
        for root, dirs, files in os.walk(backup_dir):
            for file in files:
                if file.endswith('.zst') or file.endswith('.gz'):
                    file_path = os.path.join(root, file)
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    # Проверяем только файлы за последние N дней
                    if file_mtime < cutoff:
                        continue
                    
                    results["total"] += 1
                    
                    # Пытаемся найти файл с метаданными (MD5)
                    meta_file = file_path + '.md5'
                    if os.path.exists(meta_file):
                        with open(meta_file, 'r') as f:
                            expected_md5 = f.read().strip()
                        
                        if self.validate_local_file(file_path, expected_md5):
                            results["valid"] += 1
                        else:
                            results["invalid"] += 1
                            results["errors"].append(f"{file_path}: MD5 mismatch")
                    else:
                        logger.warning(f"Нет MD5 файла для {file_path}")
        
        logger.info(f"\n📊 Результаты проверки:")
        logger.info(f"  Всего проверено: {results['total']}")
        logger.info(f"  Валидных: {results['valid']}")
        logger.info(f"  Невалидных: {results['invalid']}")
        
        if results['invalid'] > 0:
            logger.error(f"  ❌ Найдены поврежденные бэкапы!")
            for error in results['errors']:
                logger.error(f"    - {error}")
        else:
            logger.info("  ✅ Все бэкапы валидны!")
        
        return results

def main():
    validator = BackupValidator()
    
    # 1. Проверка локальных бэкапов
    logger.info("=" * 50)
    logger.info("Проверка локальных бэкапов")
    logger.info("=" * 50)
    validator.scan_and_validate("/backup", days=7)
    
    # 2. Проверка отчета о бэкапе
    logger.info("\n" + "=" * 50)
    logger.info("Проверка отчета о бэкапе")
    logger.info("=" * 50)
    validator.validate_backup_report("/tmp/backup_metric.json")
    
    # 3. Проверка S3 объектов (выборочно)
    logger.info("\n" + "=" * 50)
    logger.info("Проверка объектов в S3")
    logger.info("=" * 50)
    validator.validate_s3_object("magnolia-pos-backup", "pos_incremental/20260617/shop_001_binlog.000001.zst")

if __name__ == "__main__":
    main()