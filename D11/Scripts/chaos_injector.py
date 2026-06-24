#!/usr/bin/env python3
"""
chaos_injector.py - Инжектор хаоса для тестирования BDR Plan
Версия: 1.0
ВНИМАНИЕ: Запускать ТОЛЬКО в тестовой среде!
"""

import boto3
import random
import psycopg2
import os
import logging
import redis
from datetime import datetime

# ===== Конфигурация =====
TEST_DB_URL = os.getenv("DB_TEST_URL", "postgresql://test_user:test_pass@localhost:5432/test_db")
TEST_S3_BUCKET = os.getenv("TEST_S3_BUCKET", "magnolia-photos-test")
TEST_REDIS_HOST = os.getenv("TEST_REDIS_HOST", "localhost")
REDIS_PORT = 6379

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ===== PostgreSQL Chaos =====
def chaos_delete_orders_table():
    """Имитация удаления таблицы заказов"""
    try:
        conn = psycopg2.connect(TEST_DB_URL)
        cur = conn.cursor()
        
        # Проверяем, существует ли таблица
        cur.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'orders');")
        exists = cur.fetchone()[0]
        
        if exists:
            # Создаем бэкап таблицы перед удалением (для восстановления)
            cur.execute("CREATE TABLE orders_backup AS SELECT * FROM orders;")
            conn.commit()
            logger.info("✅ Создан бэкап таблицы orders_backup")
            
            # Удаляем таблицу
            cur.execute("DROP TABLE orders CASCADE;")
            conn.commit()
            logger.info("🔥 [CHAOS] Таблица orders удалена!")
        else:
            logger.warning("Таблица orders не существует, пропускаем")
        
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Ошибка при удалении таблицы: {e}")

# ===== S3 Chaos =====
def chaos_encrypt_s3_files(bucket, fraction=0.1):
    """Имитация шифрования файлов в S3"""
    try:
        s3 = boto3.client('s3')
        
        # Получаем список объектов
        response = s3.list_objects_v2(Bucket=bucket)
        if 'Contents' not in response:
            logger.warning(f"В бакете {bucket} нет объектов")
            return
        
        objects = response['Contents']
        logger.info(f"Найдено {len(objects)} объектов в бакете")
        
        # Выбираем случайные файлы
        to_encrypt = random.sample(objects, min(int(len(objects) * fraction), 50))
        
        for obj in to_encrypt:
            key = obj['Key']
            # Пропускаем уже зашифрованные
            if key.endswith('.encrypted'):
                continue
            
            # Имитация шифрования: переименовываем файл
            new_key = key + '.encrypted'
            s3.copy_object(
                Bucket=bucket,
                CopySource={'Bucket': bucket, 'Key': key},
                Key=new_key
            )
            s3.delete_object(Bucket=bucket, Key=key)
            logger.info(f"🔥 [CHAOS] Файл зашифрован: {key} -> {new_key}")
        
        logger.info(f"Зашифровано {len(to_encrypt)} файлов")
    except Exception as e:
        logger.error(f"Ошибка при шифровании S3: {e}")

# ===== Redis Chaos =====
def chaos_clear_redis_cache():
    """Имитация очистки кэша Redis"""
    try:
        r = redis.Redis(host=TEST_REDIS_HOST, port=REDIS_PORT, db=0)
        
        # Сохраняем количество ключей до очистки
        before_count = r.dbsize()
        logger.info(f"Количество ключей до очистки: {before_count}")
        
        # Очищаем все ключи
        r.flushdb()
        
        after_count = r.dbsize()
        logger.info(f"🔥 [CHAOS] Redis кэш очищен! Ключей осталось: {after_count}")
        
        r.close()
    except Exception as e:
        logger.error(f"Ошибка при очистке Redis: {e}")

# ===== Network Chaos =====
def chaos_network_latency(duration=30):
    """Имитация задержки сети (требует sudo)"""
    try:
        import subprocess
        
        logger.info(f"🔥 [CHAOS] Добавляем задержку сети на {duration} секунд...")
        
        # Добавляем задержку 500ms на интерфейс eth0
        subprocess.run(f"sudo tc qdisc add dev eth0 root netem delay 500ms", shell=True, check=True)
        
        # Ждем указанное время
        import time
        time.sleep(duration)
        
        # Удаляем задержку
        subprocess.run(f"sudo tc qdisc del dev eth0 root", shell=True, check=True)
        
        logger.info("Сетевая задержка удалена")
    except Exception as e:
        logger.error(f"Ошибка при имитации задержки сети: {e}")

# ===== Main =====
def main():
    """Основная функция запуска хаос-теста"""
    logger.info("=" * 50)
    logger.info("Запуск Chaos Engine для DR Drill")
    logger.info("=" * 50)
    
    # Проверка: запущено ли в тестовой среде
    env = os.getenv("ENVIRONMENT", "development")
    if env not in ["development", "test", "staging"]:
        logger.error(f"🚫 Остановка! ENVIRONMENT={env}. Запуск только в test/development!")
        return
    
    # 1. Хаос в PostgreSQL
    logger.info("\n[1/3] Запуск хаоса в PostgreSQL...")
    chaos_delete_orders_table()
    
    # 2. Хаос в S3
    logger.info("\n[2/3] Запуск хаоса в S3...")
    chaos_encrypt_s3_files(TEST_S3_BUCKET, fraction=0.05)
    
    # 3. Хаос в Redis
    logger.info("\n[3/3] Запуск хаоса в Redis...")
    chaos_clear_redis_cache()
    
    logger.info("\n" + "=" * 50)
    logger.info("✅ Chaos Engine завершил работу!")
    logger.info("🔥 Теперь запустите восстановление по Runbook!")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()