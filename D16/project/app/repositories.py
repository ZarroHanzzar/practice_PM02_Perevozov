from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from app.exceptions import EntityNotFoundException, DeliveryCalculationException
from app.models import Order, OrderItem


class OrderRepository:
    """Репозиторий для работы с заказами."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, order_data: Dict[str, Any]) -> Order:
        """
        Создаёт заказ и связанные позиции из словаря order_data.
        Ожидает структуру: {
            'customer_name': str,
            'delivery_address': str,
            'status': str (опционально),
            'total_amount': float (опционально),
            'items': [
                {'product_name': str, 'quantity': int, 'price': float},
                ...
            ]
        }
        """
        # Извлекаем данные о позициях
        items_data = order_data.pop("items", [])

        # Создаём заказ
        order = Order(**order_data)
        self.session.add(order)

        # Создаём позиции
        for item_data in items_data:
            item = OrderItem(**item_data)
            order.items.append(item)

        # Сохраняем
        self.session.commit()
        self.session.refresh(order)

        return order

    def find_by_id(self, order_id: int) -> Optional[Order]:
        """Возвращает заказ по ID или None, если не найден."""
        return self.session.get(Order, order_id)

    def find_all_by_status(self, status: str) -> List[Order]:
        """Возвращает список заказов с указанным статусом."""
        return self.session.query(Order).filter(Order.status == status).all()

    def update_status(self, order_id: int, new_status: str) -> Order:
        """Обновляет статус заказа. Если заказ не найден -- выбрасывает EntityNotFoundException."""
        order = self.find_by_id(order_id)
        if order is None:
            raise EntityNotFoundException(f"Order with id {order_id} not found")

        order.status = new_status
        self.session.commit()
        self.session.refresh(order)
        return order

    def delete(self, order_id: int) -> None:
        """Жёстко удаляет заказ и все его позиции из БД."""
        order = self.find_by_id(order_id)
        if order:
            self.session.delete(order)
            self.session.commit()

    def find_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Order]:
        """Возвращает заказы, созданные в указанном временном интервале (включая границы)."""
        return (
            self.session.query(Order)
            .filter(and_(Order.created_at >= start_date, Order.created_at <= end_date))
            .all()
        )

    def get_total_amount_for_order(self, order_id: int) -> float:
        """Вычисляет сумму всех позиций заказа (используя SQL-агрегацию)."""
        result = (
            self.session.query(func.sum(OrderItem.quantity * OrderItem.price))
            .filter(OrderItem.order_id == order_id)
            .scalar()
        )
        return float(result) if result else 0.0

    def calculate_delivery_cost(self, order_id: int) -> float:
        """
        Обращается к внешнему сервису доставки для расчёта стоимости доставки.
        Использует синхронный httpx.Client.
        """
        import httpx

        order = self.find_by_id(order_id)
        if order is None:
            raise EntityNotFoundException(f"Order with id {order_id} not found")

        # Вычисляем вес: количество * 0.5 кг
        weight = sum(item.quantity * 0.5 for item in order.items)

        payload = {
            "address": order.delivery_address,
            "weight": weight
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    "https://api.delivery.com/calculate",
                    json=payload
                )

            if response.status_code >= 400:
                raise DeliveryCalculationException(
                    f"Delivery API returned error: {response.status_code}"
                )

            data = response.json()
            return float(data.get("cost", 0.0))

        except httpx.RequestError as e:
            raise DeliveryCalculationException(f"Delivery API request failed: {str(e)}")