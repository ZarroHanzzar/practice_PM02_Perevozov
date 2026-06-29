"""
API Gateway — главный модуль системы
Версия: 2.0.0
"""

import sys
import os
import argparse
from datetime import date

# Добавляем текущую папку в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Теперь можно импортировать без точек
from database import Database
from hotel_service import HotelService
from booking_service import BookingService


class BookingAPI:
    """API Gateway для системы бронирований"""
    
    def __init__(self):
        self.db = Database()
        self.hotel_service = HotelService(self.db)
        self.booking_service = BookingService(self.db, self.hotel_service)
        self._init_demo_data()

    def _init_demo_data(self):
        """Инициализация демо-данных"""
        hotel1 = self.hotel_service.create_hotel(
            "Гранд Отель Москва",
            "ул. Тверская, д. 1, Москва",
            "+7 (495) 111-11-11",
            "info@grandhotel.ru"
        )
        if hotel1:
            self.hotel_service.add_room("HOTEL-0001", "101", 5000, 2, 1, "standard")
            self.hotel_service.add_room("HOTEL-0001", "102", 5000, 2, 1, "standard")
            self.hotel_service.add_room("HOTEL-0001", "201", 7000, 4, 2, "suite")
            self.hotel_service.add_room("HOTEL-0001", "202", 8000, 4, 2, "deluxe")
        
        hotel2 = self.hotel_service.create_hotel(
            "Отель Санкт-Петербург",
            "Невский пр., д. 10, Санкт-Петербург",
            "+7 (812) 222-22-22",
            "info@spbhotel.ru"
        )
        if hotel2:
            self.hotel_service.add_room("HOTEL-0002", "301", 4000, 2, 3, "standard")
            self.hotel_service.add_room("HOTEL-0002", "302", 4500, 2, 3, "standard")
            self.hotel_service.add_room("HOTEL-0002", "401", 6000, 3, 4, "suite")
        
        print(f"🏨 Загружено {len(self.db.get_all_hotels())} отелей")
        print(f"📋 Всего номеров: {sum(len(h.rooms) for h in self.db.get_all_hotels())}")

    def show_hotels(self):
        """Показать все отели"""
        print("\n" + "="*60)
        print("🏨 СПИСОК ОТЕЛЕЙ")
        print("="*60)
        for hotel in self.hotel_service.get_all_hotels():
            print(f"\n📌 {hotel.name} ({hotel.id})")
            print(f"   📍 {hotel.address}")
            print(f"   📞 {hotel.phone}")
            print(f"   ✉️  {hotel.email}")
            print(f"   ⭐ Рейтинг: {hotel.rating}")
            print(f"   🏠 Номера: {len(hotel.rooms)}")
            for room in hotel.rooms:
                status = "✅ Доступен" if room.is_available else "❌ Занят"
                print(f"      • {room.id} | {room.room_type} | {room.capacity} чел. | {room.price_per_night} руб. | {status}")

    def show_available_rooms(self, hotel_id: str, check_in_str: str, check_out_str: str):
        """Показать доступные номера"""
        check_in = date.fromisoformat(check_in_str)
        check_out = date.fromisoformat(check_out_str)
        
        rooms = self.hotel_service.get_available_rooms(hotel_id, check_in, check_out)
        
        hotel = self.hotel_service.get_hotel(hotel_id)
        if not hotel:
            print(f"❌ Отель {hotel_id} не найден")
            return
        
        print(f"\n{'='*60}")
        print(f"🏨 ДОСТУПНЫЕ НОМЕРА В {hotel.name.upper()}")
        print(f"📅 С {check_in_str} по {check_out_str}")
        print("="*60)
        
        if not rooms:
            print("❌ Нет доступных номеров на указанные даты")
            return
        
        for room in rooms:
            print(f"\n🛏  Номер {room.id}")
            print(f"   Тип: {room.room_type}")
            print(f"   Вместимость: {room.capacity} чел.")
            print(f"   Цена: {room.price_per_night} руб./ночь")
            print(f"   Этаж: {room.floor or 'не указан'}")

    def create_booking_interactive(self):
        """Интерактивное создание бронирования"""
        print("\n" + "="*60)
        print("📝 СОЗДАНИЕ БРОНИРОВАНИЯ")
        print("="*60)
        
        self.show_hotels()
        
        hotel_id = input("\n🏨 Введите ID отеля: ").strip()
        room_id = input("🛏  Введите ID номера: ").strip()
        guest_name = input("👤 Имя гостя: ").strip()
        guest_email = input("✉️  Email гостя: ").strip()
        guest_phone = input("📞 Телефон гостя: ").strip()
        check_in_str = input("📅 Дата заезда (ГГГГ-ММ-ДД): ").strip()
        check_out_str = input("📅 Дата выезда (ГГГГ-ММ-ДД): ").strip()
        
        try:
            check_in = date.fromisoformat(check_in_str)
            check_out = date.fromisoformat(check_out_str)
        except ValueError:
            print("❌ Неверный формат даты")
            return
        
        booking = self.booking_service.create_booking(
            hotel_id, room_id, guest_name, guest_email, guest_phone,
            check_in, check_out
        )
        
        if booking:
            print(f"\n✅ Бронирование успешно создано!")
            print(f"   ID бронирования: {booking.id}")
            print(f"   Сумма: {booking.total_price} руб.")

    def run_cli(self):
        """Запуск CLI-интерфейса"""
        parser = argparse.ArgumentParser(
            description="Система управления бронированиями",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Примеры:
  python -m booking_system.api_gateway --list-hotels
  python -m booking_system.api_gateway --available HOTEL-0001 2026-07-01 2026-07-05
  python -m booking_system.api_gateway --create-booking
  python -m booking_system.api_gateway --cancel BK-000001
  python -m booking_system.api_gateway --revenue HOTEL-0001 2026-06-01 2026-06-30
  python -m booking_system.api_gateway --save data.json
            """
        )
        
        parser.add_argument("--list-hotels", action="store_true", help="Показать все отели")
        parser.add_argument("--available", nargs=3, metavar=("HOTEL_ID", "CHECK_IN", "CHECK_OUT"),
                           help="Показать доступные номера")
        parser.add_argument("--create-booking", action="store_true", help="Создать бронирование (интерактивно)")
        parser.add_argument("--cancel", metavar="BOOKING_ID", help="Отменить бронирование")
        parser.add_argument("--check-in", metavar="BOOKING_ID", help="Заселить гостя")
        parser.add_argument("--check-out", metavar="BOOKING_ID", help="Выселить гостя")
        parser.add_argument("--revenue", nargs=3, metavar=("HOTEL_ID", "START", "END"),
                           help="Рассчитать выручку")
        parser.add_argument("--save", metavar="FILE", help="Сохранить данные в JSON")
        parser.add_argument("--load", metavar="FILE", help="Загрузить данные из JSON")
        parser.add_argument("--guest-history", metavar="EMAIL", help="История бронирований гостя")
        
        args = parser.parse_args()
        
        if args.list_hotels:
            self.show_hotels()
        
        elif args.available:
            hotel_id, check_in, check_out = args.available
            self.show_available_rooms(hotel_id, check_in, check_out)
        
        elif args.create_booking:
            self.create_booking_interactive()
        
        elif args.cancel:
            self.booking_service.cancel_booking(args.cancel)
        
        elif args.check_in:
            self.booking_service.check_in(args.check_in)
        
        elif args.check_out:
            self.booking_service.check_out(args.check_out)
        
        elif args.revenue:
            hotel_id, start, end = args.revenue
            start_date = date.fromisoformat(start)
            end_date = date.fromisoformat(end)
            revenue = self.booking_service.calculate_revenue(hotel_id, start_date, end_date)
            hotel = self.hotel_service.get_hotel(hotel_id)
            print(f"💰 Выручка {hotel.name if hotel else hotel_id}: {revenue} руб.")
        
        elif args.save:
            if self.db.save_to_file(args.save):
                print(f"✅ Данные сохранены в {args.save}")
        
        elif args.load:
            if self.db.load_from_file(args.load):
                print(f"✅ Данные загружены из {args.load}")
        
        elif args.guest_history:
            bookings = self.booking_service.get_guest_history(args.guest_history)
            print(f"\n📋 ИСТОРИЯ БРОНИРОВАНИЙ ДЛЯ {args.guest_history}")
            print("="*60)
            if not bookings:
                print("❌ Бронирований не найдено")
                return
            for b in bookings:
                hotel = self.hotel_service.get_hotel(b.hotel_id)
                hotel_name = hotel.name if hotel else b.hotel_id
                print(f"\n🆔 {b.id} | {b.status.value.upper()}")
                print(f"   Отель: {hotel_name}")
                print(f"   Номер: {b.room_id}")
                print(f"   Даты: {b.check_in} → {b.check_out} ({b.get_nights()} ночей)")
                print(f"   Сумма: {b.total_price} руб.")
        
        else:
            parser.print_help()


def main():
    """Главная функция"""
    app = BookingAPI()
    app.run_cli()


if __name__ == "__main__":
    main()