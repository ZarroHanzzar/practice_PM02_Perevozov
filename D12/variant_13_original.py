"""
Вариант 13: ORM (SQLAlchemy) - ИСХОДНЫЙ КОД С ОШИБКАМИ
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import tracemalloc
import time
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

Base = declarative_base()

class Hotel(Base):
    __tablename__ = 'hotels'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    city = Column(String(50))
    rating = Column(Float)
    # ОШИБКА 4: N+1 проблема - lazy loading по умолчанию
    rooms = relationship("Room", back_populates="hotel")

class Room(Base):
    __tablename__ = 'rooms'
    
    id = Column(Integer, primary_key=True)
    hotel_id = Column(Integer, ForeignKey('hotels.id'))
    room_number = Column(String(10))
    price_per_night = Column(Float)
    # ОШИБКА 6: неправильный тип данных
    is_available = Column(Integer)  # Должно быть Boolean
    
    hotel = relationship("Hotel", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room")

class Booking(Base):
    __tablename__ = 'bookings'
    
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('rooms.id'))
    guest_name = Column(String(100))
    nights = Column(Integer)
    total_price = Column(Float)
    
    room = relationship("Room", back_populates="bookings")

class HotelService:
    def __init__(self):
        self.session = Session()
        # ОШИБКА 3: неограниченный кеш
        self._cache = {}
        self._calls = 0
    
    def __del__(self):
        # ОШИБКА 5: сессия не закрывается
        pass
    
    def find_hotels_by_city(self, city):
        # ОШИБКА 2: неправильная фильтрация
        return self.session.query(Hotel).filter(Hotel.city == city + '%').all()
    
    def calculate_booking_price(self, room_id, nights):
        room = self.session.query(Room).get(room_id)
        # ОШИБКА 1: несуществующий атрибут
        return room.base_price * nights
    
    def get_hotel_with_rooms(self, hotel_id):
        # ОШИБКА 4: N+1 проблема
        hotel = self.session.query(Hotel).get(hotel_id)
        for room in hotel.rooms:  # Дополнительный запрос
            bookings = room.bookings  # Еще один запрос для каждой комнаты
        return hotel
    
    def process_bookings(self, hotel_id):
        # ОШИБКА 3: кеширование без ограничения
        cache_key = f"hotel_{hotel_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        hotel = self.get_hotel_with_rooms(hotel_id)
        
        total_revenue = 0
        for room in hotel.rooms:
            for booking in room.bookings:  # N+1 проблема
                total_revenue += booking.total_price
        
        result = {'hotel_name': hotel.name, 'total_revenue': total_revenue}
        self._cache[cache_key] = result  # Утечка памяти
        return result

# Создание БД
engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def main():
    tracemalloc.start()
    session = Session()
    
    # Создание тестовых данных
    hotel = Hotel(name="Grand Plaza", city="Moscow", rating=4.8)
    session.add(hotel)
    session.commit()
    
    room = Room(hotel_id=hotel.id, room_number="001", 
                price_per_night=150.0, is_available=1)
    session.add(room)
    session.commit()
    
    booking = Booking(room_id=room.id, guest_name="John", 
                      nights=3, total_price=450.0)
    session.add(booking)
    session.commit()
    
    service = HotelService()
    
    # Вызов с ошибками
    try:
        service.find_hotels_by_city("Moscow")
        service.calculate_booking_price(1, 3)
        service.process_bookings(1)
    except Exception as e:
        print(f"Ошибка: {e}")
    
    snapshot = tracemalloc.take_snapshot()
    print("\nТоп-5 строк по памяти:")
    for stat in snapshot.statistics('lineno')[:5]:
        print(stat)

if __name__ == "__main__":
    main()