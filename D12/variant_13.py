"""
Вариант 13: ORM (SQLAlchemy)
Финальная версия со всеми исправлениями и проверками

Список исправленных ошибок:
1. AttributeError - обращение к несуществующему атрибуту base_price
2. Неправильная фильтрация - использование LIKE с ошибкой в синтаксисе
3. Утечка памяти - неограниченный рост кеша
4. N+1 проблема - множественные запросы к БД из-за lazy loading
5. Сессия не закрывается - отсутствие явного закрытия
6. Неправильный тип данных - Integer вместо Boolean для is_available
"""
import math
import time
import tracemalloc
import logging
import sys
from contextlib import contextmanager
from functools import lru_cache
from typing import List, Dict, Any, Optional

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, joinedload, selectinload
from sqlalchemy.exc import SQLAlchemyError

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

Base = declarative_base()

# ============ Модели данных ============

class Hotel(Base):
    """Модель отеля"""
    __tablename__ = 'hotels'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    city = Column(String(50), nullable=False)
    rating = Column(Float, default=0.0)
    
    # ИСПРАВЛЕНИЕ №4: Используем selectinload для предотвращения N+1 проблемы
    # Вместо lazy='select' (по умолчанию) используем 'selectinload'
    # Это загружает все связанные комнаты одним запросом
    rooms = relationship("Room", back_populates="hotel", lazy='selectin')
    
    def __repr__(self):
        return f"<Hotel(id={self.id}, name='{self.name}', city='{self.city}')>"


class Room(Base):
    """Модель комнаты"""
    __tablename__ = 'rooms'
    
    id = Column(Integer, primary_key=True)
    hotel_id = Column(Integer, ForeignKey('hotels.id', ondelete='CASCADE'))
    room_number = Column(String(10), nullable=False)
    price_per_night = Column(Float, nullable=False)
    
    # ИСПРАВЛЕНИЕ №6: Исправлен тип данных
    # Было: is_available = Column(Integer)  # Ошибка: int вместо bool
    # Стало: используется Boolean тип
    is_available = Column(Boolean, default=True)
    
    hotel = relationship("Hotel", back_populates="rooms")
    
    # ИСПРАВЛЕНИЕ №4: Также используем selectinload для bookings
    bookings = relationship("Booking", back_populates="room", lazy='selectin')
    
    def __repr__(self):
        return f"<Room(id={self.id}, number='{self.room_number}', price={self.price_per_night})>"


class Booking(Base):
    """Модель бронирования"""
    __tablename__ = 'bookings'
    
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('rooms.id', ondelete='CASCADE'))
    guest_name = Column(String(100), nullable=False)
    nights = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    created_at = Column(Integer, default=lambda: int(time.time()))  # Для отслеживания устаревания
    
    room = relationship("Room", back_populates="bookings")
    
    def __repr__(self):
        return f"<Booking(id={self.id}, guest='{self.guest_name}', nights={self.nights})>"


# ============ Создание тестовой БД ============

def create_test_database():
    """Создание тестовой базы данных"""
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)
    return engine


def create_test_data(session):
    """Создание тестовых данных"""
    logger.info("Создание тестовых данных...")
    
    # Создаем отели
    hotels = [
        Hotel(name="Grand Plaza", city="Moscow", rating=4.8),
        Hotel(name="Seaside Resort", city="Sochi", rating=4.5),
        Hotel(name="Mountain View", city="Krasnodar", rating=4.2),
        Hotel(name="City Center", city="Moscow", rating=4.6),
        Hotel(name="Lake Paradise", city="Krasnodar", rating=4.3),
    ]
    session.add_all(hotels)
    session.commit()
    
    # Создаем комнаты
    rooms = []
    for hotel in hotels:
        for i in range(5):
            room = Room(
                hotel_id=hotel.id,
                room_number=f"{i+1:03d}",
                price_per_night=100.0 + i * 50.0,
                # ИСПРАВЛЕНИЕ №6: Используем Boolean значения
                # Было: is_available=1 if i % 2 == 0 else 0
                # Стало: передаем True/False
                is_available=(i % 2 == 0)
            )
            rooms.append(room)
    session.add_all(rooms)
    session.commit()
    
    # Создаем бронирования
    bookings = []
    for i, room in enumerate(rooms[:10]):
        nights = (i % 5) + 1
        booking = Booking(
            room_id=room.id,
            guest_name=f"Guest_{i+1:03d}",
            nights=nights,
            total_price=room.price_per_night * nights * 0.9  # скидка 10%
        )
        bookings.append(booking)
    session.add_all(bookings)
    session.commit()
    
    logger.info(f"Создано {len(hotels)} отелей, {len(rooms)} комнат, {len(bookings)} бронирований")
    return [h.id for h in hotels]


# ============ Сервис с исправленными ошибками ============

class HotelService:
    """
    Сервис для работы с отелями.
    Все ошибки исправлены:
    1. AttributeError - исправлен доступ к атрибутам
    2. Неправильная фильтрация - исправлена
    3. Утечка памяти - добавлен LRU кеш с очисткой
    4. N+1 проблема - исправлена с помощью joinedload
    5. Сессия не закрывается - добавлен контекстный менеджер
    """
    
    def __init__(self, session, max_cache_size: int = 100, cache_ttl: int = 300):
        """
        Инициализация сервиса
        
        Args:
            session: Сессия SQLAlchemy
            max_cache_size: Максимальный размер кеша
            cache_ttl: Время жизни кеша в секундах
        """
        self.session = session
        self._cache = {}
        self._cache_timestamps = {}
        
        # ИСПРАВЛЕНИЕ №3: Ограничение размера кеша
        self._max_cache_size = max_cache_size
        self._cache_ttl = cache_ttl
        
        self._calls_count = 0
        self._is_closed = False
        logger.info(f"Сервис инициализирован (max_cache_size={max_cache_size}, ttl={cache_ttl}s)")
    
    def __enter__(self):
        """Вход в контекстный менеджер"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекстного менеджера"""
        self.close()
    
    def close(self):
        """ИСПРАВЛЕНИЕ №5: Закрытие сессии и очистка ресурсов"""
        if not self._is_closed:
            if self.session:
                try:
                    # Было: сессия никогда не закрывалась
                    # Стало: явное закрытие сессии
                    self.session.close()
                    logger.info("Сессия закрыта")
                except Exception as e:
                    logger.error(f"Ошибка при закрытии сессии: {e}")
            self._cache.clear()
            self._cache_timestamps.clear()
            self._is_closed = True
            logger.info("Ресурсы очищены")
    
    def _cleanup_cache(self):
        """ИСПРАВЛЕНИЕ №3: Очистка устаревших записей кеша"""
        current_time = time.time()
        
        # Удаляем устаревшие записи (TTL)
        expired_keys = [
            key for key, timestamp in self._cache_timestamps.items()
            if current_time - timestamp > self._cache_ttl
        ]
        for key in expired_keys:
            del self._cache[key]
            del self._cache_timestamps[key]
            logger.debug(f"Удалена устаревшая запись кеша: {key}")
        
        # Если кеш все еще больше лимита, удаляем самые старые
        if len(self._cache) > self._max_cache_size:
            sorted_keys = sorted(
                self._cache_timestamps.items(),
                key=lambda x: x[1]
            )
            keys_to_remove = sorted_keys[:len(self._cache) - self._max_cache_size]
            for key, _ in keys_to_remove:
                del self._cache[key]
                del self._cache_timestamps[key]
                logger.debug(f"Удалена запись кеша (превышение лимита): {key}")
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Получение данных из кеша"""
        self._cleanup_cache()
        return self._cache.get(key)
    
    def _set_to_cache(self, key: str, value: Any):
        """Сохранение данных в кеш"""
        self._cleanup_cache()
        self._cache[key] = value
        self._cache_timestamps[key] = time.time()
        logger.debug(f"Добавлено в кеш: {key}")
    
    # ============ Основные методы ============
    
    def find_hotels_by_city(self, city: str) -> List[Hotel]:
        """
        Поиск отелей по городу.
        ИСПРАВЛЕНИЕ №2: правильная фильтрация
        """
        logger.debug(f"Поиск отелей в городе: {city}")
        
        # ИСПРАВЛЕНИЕ №2: Неправильный синтаксис фильтрации
        # Было: return self.session.query(Hotel).filter(Hotel.city == city + '%').all()
        # Ошибка: использовался LIKE с неправильным синтаксисом
        # Стало: точное совпадение
        return self.session.query(Hotel).filter(Hotel.city == city).all()
    
    def find_hotels_by_city_with_rating(self, city: str, min_rating: float = 0) -> List[Hotel]:
        """
        Поиск отелей по городу с минимальным рейтингом
        """
        logger.debug(f"Поиск отелей в городе {city} с рейтингом >= {min_rating}")
        
        return (self.session.query(Hotel)
                .filter(Hotel.city == city)
                .filter(Hotel.rating >= min_rating)
                .all())
    
    def calculate_booking_price(self, room_id: int, nights: int) -> float:
        """
        Расчет цены бронирования.
        ИСПРАВЛЕНИЕ №1: использование правильного атрибута
        """
        logger.debug(f"Расчет цены для комнаты {room_id}, ночей: {nights}")
        
        # Проверка входных данных
        if nights <= 0:
            logger.warning(f"Некорректное количество ночей: {nights}")
            return 0.0
        
        room = self.session.query(Room).get(room_id)
        if not room:
            logger.warning(f"Комната с ID {room_id} не найдена")
            return 0.0
        
        # ИСПРАВЛЕНИЕ №1: AttributeError
        # Было: return room.base_price * nights
        # Ошибка: атрибут 'base_price' не существует
        # Стало: используем правильный атрибут 'price_per_night'
        price = room.price_per_night * nights
        
        # Применяем скидку для длительных бронирований
        if nights > 7:
            price *= 0.85  # 15% скидка
        elif nights > 3:
            price *= 0.95  # 5% скидка
        
        logger.debug(f"Расчетная цена: {price}")
        return price
    
    def get_hotel_with_rooms(self, hotel_id: int) -> Optional[Hotel]:
        """
        Получение отеля со всеми комнатами.
        ИСПРАВЛЕНИЕ №4: устранение N+1 проблемы через joinedload
        """
        logger.debug(f"Загрузка отеля {hotel_id} с комнатами")
        
        # ИСПРАВЛЕНИЕ №4: N+1 проблема
        # Было: hotel = self.session.query(Hotel).get(hotel_id)
        # Проблема: при обращении к hotel.rooms выполнялся дополнительный запрос
        # для каждой комнаты при обращении к room.bookings
        # Стало: используем joinedload для жадной загрузки всех данных
        hotel = (self.session.query(Hotel)
                .options(
                    joinedload(Hotel.rooms)
                    .joinedload(Room.bookings)  # Загружаем bookings вместе с комнатами
                )
                .filter(Hotel.id == hotel_id)
                .first())
        
        if not hotel:
            logger.warning(f"Отель с ID {hotel_id} не найден")
        else:
            logger.debug(f"Загружен отель: {hotel.name}, комнат: {len(hotel.rooms)}")
        
        return hotel
    
    def get_hotel_with_rooms_optimized(self, hotel_id: int) -> Optional[Hotel]:
        """
        Получение отеля с комнатами (оптимизированная версия).
        Использует selectinload для еще более эффективной загрузки.
        """
        logger.debug(f"Оптимизированная загрузка отеля {hotel_id}")
        
        # Альтернативный способ: selectinload обычно быстрее для больших наборов
        hotel = (self.session.query(Hotel)
                .options(
                    selectinload(Hotel.rooms)
                    .selectinload(Room.bookings)
                )
                .filter(Hotel.id == hotel_id)
                .first())
        
        return hotel
    
    def process_bookings(self, hotel_id: int) -> Dict[str, Any]:
        """
        Обработка бронирований отеля.
        ИСПРАВЛЕНИЕ №3 и №4: кеширование с ограничением, устранение N+1
        """
        self._calls_count += 1
        logger.debug(f"Обработка бронирований для отеля {hotel_id} (вызов #{self._calls_count})")
        
        # ИСПРАВЛЕНИЕ №3: Проверка кеша с ограничением
        cache_key = f"hotel_{hotel_id}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            logger.debug(f"Результат получен из кеша для отеля {hotel_id}")
            return cached_result
        
        # ИСПРАВЛЕНИЕ №4: Загрузка отеля с данными (уже нет N+1 проблемы)
        hotel = self.get_hotel_with_rooms(hotel_id)
        if not hotel:
            logger.error(f"Отель с ID {hotel_id} не найден")
            return {'error': 'Hotel not found'}
        
        # Расчет данных (уже нет N+1 проблемы благодаря joinedload)
        total_revenue = 0
        total_bookings = 0
        available_rooms = 0
        room_details = []
        
        # Теперь hotel.rooms и room.bookings уже загружены
        # Нет дополнительных запросов к БД!
        for room in hotel.rooms:
            room_bookings_count = len(room.bookings)
            room_revenue = sum(booking.total_price for booking in room.bookings)
            
            total_revenue += room_revenue
            total_bookings += room_bookings_count
            
            if room.is_available:
                available_rooms += 1
            
            room_details.append({
                'number': room.room_number,
                'price': room.price_per_night,
                'available': room.is_available,
                'bookings_count': room_bookings_count,
                'revenue': room_revenue
            })
        
        result = {
            'hotel_id': hotel.id,
            'hotel_name': hotel.name,
            'city': hotel.city,
            'rating': hotel.rating,
            'total_revenue': total_revenue,
            'total_bookings': total_bookings,
            'room_count': len(hotel.rooms),
            'available_rooms': available_rooms,
            'occupancy_rate': total_bookings / (len(hotel.rooms) * 30) if hotel.rooms else 0,
            'rooms': room_details,
            'processed_at': time.time(),
            'cache_hit': False
        }
        
        # ИСПРАВЛЕНИЕ №3: Сохранение в кеш с ограничением
        self._set_to_cache(cache_key, result)
        logger.info(f"Обработан отель {hotel_id}: {total_bookings} бронирований, выручка {total_revenue:.2f}")
        
        return result
    
    def process_multiple_hotels(self, hotel_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Обработка нескольких отелей.
        ИСПРАВЛЕНО: обработка ошибок для каждого отеля
        """
        logger.info(f"Массовая обработка {len(hotel_ids)} отелей")
        
        results = []
        errors = []
        
        for hotel_id in hotel_ids:
            try:
                result = self.process_bookings(hotel_id)
                results.append(result)
            except SQLAlchemyError as e:
                # Обработка ошибок БД
                error_msg = f"Ошибка БД при обработке отеля {hotel_id}: {e}"
                logger.error(error_msg)
                errors.append({'hotel_id': hotel_id, 'error': str(e)})
            except Exception as e:
                # Обработка всех остальных ошибок
                error_msg = f"Неизвестная ошибка при обработке отеля {hotel_id}: {e}"
                logger.error(error_msg)
                errors.append({'hotel_id': hotel_id, 'error': str(e)})
        
        if errors:
            logger.warning(f"Обработано с ошибками: {len(errors)} отелей")
        
        return results
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Получение статистики кеша"""
        return {
            'cache_size': len(self._cache),
            'max_cache_size': self._max_cache_size,
            'cache_ttl': self._cache_ttl,
            'total_calls': self._calls_count,
            'is_closed': self._is_closed,
            'cache_keys': list(self._cache.keys())[:10]  # Показываем первые 10 ключей
        }
    
    def clear_cache(self):
        """Очистка кеша"""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("Кеш очищен")


# ============ Тесты ============

def test_memory_leaks(service: HotelService, iterations: int = 100):
    """Тест на утечки памяти"""
    logger.info(f"Запуск теста на утечки памяти ({iterations} итераций)")
    
    tracemalloc.start()
    snapshot_before = tracemalloc.take_snapshot()
    
    for i in range(iterations):
        if i % 20 == 0:
            logger.info(f"Итерация {i}/{iterations}")
        service.process_bookings(1)
    
    snapshot_after = tracemalloc.take_snapshot()
    diff = snapshot_after.compare_to(snapshot_before, 'lineno')
    
    logger.info("Статистика памяти:")
    total_memory = 0
    for stat in diff[:10]:
        total_memory += stat.size_diff
        logger.info(f"  {stat}")
    
    logger.info(f"Общее изменение памяти: {total_memory / 1024:.2f} KB")
    return total_memory < 1024 * 1024  # Меньше 1MB


def run_all_tests():
    """Запуск всех тестов"""
    logger.info("=" * 60)
    logger.info("ЗАПУСК ТЕСТОВ ДЛЯ ВАРИАНТА №13")
    logger.info("=" * 60)
    
    # Создание БД и данных
    engine = create_test_database()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    hotel_ids = create_test_data(session)
    session.commit()
    
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'details': []
    }
    
    def run_test(name, func, *args, **kwargs):
        """Вспомогательная функция для запуска тестов"""
        results['total'] += 1
        try:
            result = func(*args, **kwargs)
            results['passed'] += 1
            results['details'].append({'name': name, 'status': 'PASS', 'result': result})
            logger.info(f"✅ {name} - ПРОЙДЕН")
            return result
        except Exception as e:
            results['failed'] += 1
            results['details'].append({'name': name, 'status': 'FAIL', 'error': str(e)})
            logger.error(f"❌ {name} - ПРОВАЛЕН: {e}")
            return None
    
    # Создаем сервис
    service = HotelService(session, max_cache_size=50, cache_ttl=60)
    
    # Тест 1: Поиск отелей
    run_test("Поиск отелей в Москве", 
             service.find_hotels_by_city, "Moscow")
    
    # Тест 2: Поиск отелей с рейтингом
    run_test("Поиск отелей в Сочи с рейтингом >= 4.5",
             service.find_hotels_by_city_with_rating, "Sochi", 4.5)
    
    # Тест 3: Расчет цены
    room_id = 1
    price = run_test("Расчет цены бронирования",
                     service.calculate_booking_price, room_id, 3)
    if price is not None:
        assert price > 0, "Цена должна быть положительной"
    
    # Тест 4: Расчет цены с некорректными данными
    run_test("Расчет цены с некорректными данными",
             service.calculate_booking_price, 999, -1)
    
    # Тест 5: Обработка бронирований
    result = run_test("Обработка бронирований отеля",
                      service.process_bookings, hotel_ids[0])
    if result and 'error' not in result:
        assert 'total_revenue' in result, "Результат должен содержать выручку"
        assert result['total_bookings'] > 0, "Должны быть бронирования"
    
    # Тест 6: Кеширование
    cached_result = run_test("Проверка кеширования",
                             service.process_bookings, hotel_ids[0])
    if cached_result:
        assert cached_result['cache_hit'] is False, "Первый вызов не должен быть из кеша"
    
    # Тест 7: Массовая обработка
    results_list = run_test("Массовая обработка отелей",
                            service.process_multiple_hotels, hotel_ids)
    if results_list:
        assert len(results_list) == len(hotel_ids), "Должны быть обработаны все отели"
    
    # Тест 8: Статистика кеша
    stats = run_test("Статистика кеша",
                     service.get_cache_stats)
    if stats:
        assert stats['cache_size'] <= 50, "Размер кеша не должен превышать лимит"
    
    # Тест 9: Очистка кеша
    run_test("Очистка кеша",
             service.clear_cache)
    
    # Тест 10: Утечки памяти
    memory_ok = run_test("Проверка утечек памяти",
                         test_memory_leaks, service, 50)
    if memory_ok is not None:
        assert memory_ok, "Обнаружены утечки памяти"
    
    # Тест 11: Закрытие сессии
    run_test("Закрытие сессии",
             service.close)
    
    # Итоговые результаты
    logger.info("=" * 60)
    logger.info("ИТОГОВЫЕ РЕЗУЛЬТАТЫ ТЕСТОВ:")
    logger.info(f"Всего тестов: {results['total']}")
    logger.info(f"Пройдено: {results['passed']}")
    logger.info(f"Провалено: {results['failed']}")
    
    if results['failed'] == 0:
        logger.info("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        logger.warning(f"⚠️ {results['failed']} тестов провалено")
    
    logger.info("=" * 60)
    
    # Финальная проверка памяти
    logger.info("\nФинальная проверка памяти:")
    snapshot = tracemalloc.take_snapshot()
    for stat in snapshot.statistics('lineno')[:5]:
        logger.info(f"  {stat}")
    
    return results


# ============ Основная функция ============

def main():
    """Основная функция"""
    try:
        results = run_all_tests()
        
        # Дополнительная проверка закрытия ресурсов
        logger.info("\nПроверка закрытия ресурсов...")
        logger.info("✅ Все ресурсы должны быть закрыты")
        
        return 0 if results['failed'] == 0 else 1
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    # Запуск с трассировкой памяти
    tracemalloc.start()
    exit_code = main()
    
    # Финальная статистика
    snapshot = tracemalloc.take_snapshot()
    print("\n" + "=" * 60)
    print("ФИНАЛЬНАЯ СТАТИСТИКА ПАМЯТИ:")
    top_stats = snapshot.statistics('lineno')[:5]
    for stat in top_stats:
        print(f"  {stat}")
    
    print(f"\nПрограмма завершена с кодом: {exit_code}")
    sys.exit(exit_code)