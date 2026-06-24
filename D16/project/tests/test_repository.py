import pytest
from datetime import datetime, timedelta

from app.repositories import OrderRepository
from app.exceptions import EntityNotFoundException, DeliveryCalculationException
from app.models import Order, OrderItem


class TestOrderRepository:
    """Интеграционные тесты для OrderRepository."""

    def test_create_order_with_items(self, db_session):
        """Тест: создание заказа с позициями."""
        repo = OrderRepository(db_session)

        order_data = {
            "customer_name": "Иван Петров",
            "delivery_address": "Москва, ул. Тверская, д. 10",
            "status": "PENDING",
            "total_amount": 0.0,
            "items": [
                {"product_name": "Товар 1", "quantity": 2, "price": 100.50},
                {"product_name": "Товар 2", "quantity": 1, "price": 200.00},
            ]
        }

        order = repo.create(order_data)

        assert order.id is not None
        assert order.customer_name == "Иван Петров"
        assert order.status == "PENDING"
        assert len(order.items) == 2
        assert order.items[0].product_name == "Товар 1"
        assert order.items[0].quantity == 2
        assert order.items[0].price == 100.50

        saved_order = db_session.get(Order, order.id)
        assert saved_order is not None
        assert len(saved_order.items) == 2

    def test_find_by_id_existing(self, db_session):
        """Тест: поиск существующего заказа по ID."""
        repo = OrderRepository(db_session)

        order_data = {
            "customer_name": "Тестовый клиент",
            "delivery_address": "Тестовый адрес",
            "items": []
        }
        created = repo.create(order_data)

        found = repo.find_by_id(created.id)

        assert found is not None
        assert found.id == created.id
        assert found.customer_name == "Тестовый клиент"

    def test_find_by_id_not_existing(self, db_session):
        """Тест: поиск несуществующего заказа возвращает None."""
        repo = OrderRepository(db_session)
        found = repo.find_by_id(999)
        assert found is None

    @pytest.mark.parametrize("status", ["PENDING", "PAID", "SHIPPED", "CANCELLED"])
    def test_find_all_by_status_parametrized(self, db_session, status):
        """Тест: поиск заказов по статусу (параметризованный)."""
        repo = OrderRepository(db_session)

        for s in ["PENDING", "PAID", "SHIPPED", "CANCELLED"]:
            order_data = {
                "customer_name": f"Клиент {s}",
                "delivery_address": f"Адрес {s}",
                "status": s,
                "items": []
            }
            repo.create(order_data)

        orders = repo.find_all_by_status(status)

        assert len(orders) == 1
        assert all(o.status == status for o in orders)

    def test_update_status_existing(self, db_session):
        """Тест: обновление статуса существующего заказа."""
        repo = OrderRepository(db_session)

        order_data = {
            "customer_name": "Тестовый клиент",
            "delivery_address": "Тестовый адрес",
            "status": "PENDING",
            "items": []
        }
        order = repo.create(order_data)

        updated = repo.update_status(order.id, "PAID")

        assert updated.status == "PAID"
        saved = db_session.get(Order, order.id)
        assert saved.status == "PAID"

    def test_update_status_not_existing(self, db_session):
        """Тест: обновление статуса несуществующего заказа вызывает исключение."""
        repo = OrderRepository(db_session)

        with pytest.raises(EntityNotFoundException) as exc_info:
            repo.update_status(999, "PAID")

        assert "Order with id 999 not found" in str(exc_info.value)

    def test_delete_order_cascade(self, db_session):
        """Тест: удаление заказа каскадно удаляет позиции."""
        repo = OrderRepository(db_session)

        order_data = {
            "customer_name": "Тестовый клиент",
            "delivery_address": "Тестовый адрес",
            "items": [
                {"product_name": "Товар 1", "quantity": 2, "price": 100.0},
                {"product_name": "Товар 2", "quantity": 1, "price": 200.0},
            ]
        }
        order = repo.create(order_data)
        order_id = order.id

        repo.delete(order_id)

        assert db_session.get(Order, order_id) is None
        items = db_session.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        assert len(items) == 0

    def test_find_by_date_range(self, db_session):
        """Тест: поиск заказов по диапазону дат."""
        repo = OrderRepository(db_session)

        # Используем datetime без временной зоны для совместимости с SQLite
        now = datetime.utcnow()
        dates = [
            now - timedelta(days=5),
            now - timedelta(days=3),
            now - timedelta(days=1),
            now + timedelta(days=1),
            now + timedelta(days=3),
        ]

        for i, dt in enumerate(dates):
            order = Order(
                customer_name=f"Клиент {i}",
                delivery_address=f"Адрес {i}",
                status="PENDING",
                created_at=dt
            )
            db_session.add(order)
        db_session.commit()

        start_date = now - timedelta(days=2)
        end_date = now + timedelta(days=2)
        orders = repo.find_by_date_range(start_date, end_date)

        # Должны попасть заказы: индекс 2 (-1 день) и индекс 3 (+1 день)
        assert len(orders) == 2
        for order in orders:
            assert start_date <= order.created_at <= end_date

    def test_get_total_amount_for_order(self, db_session):
        """Тест: расчёт общей суммы заказа через SQL-агрегацию."""
        repo = OrderRepository(db_session)

        order_data = {
            "customer_name": "Тестовый клиент",
            "delivery_address": "Тестовый адрес",
            "items": [
                {"product_name": "Товар 1", "quantity": 3, "price": 100.0},
                {"product_name": "Товар 2", "quantity": 2, "price": 50.0},
                {"product_name": "Товар 3", "quantity": 1, "price": 200.0},
            ]
        }
        order = repo.create(order_data)
        expected_total = 3 * 100.0 + 2 * 50.0 + 1 * 200.0

        total = repo.get_total_amount_for_order(order.id)

        assert total == expected_total

    def test_transaction_rollback_on_invalid_data(self, db_session):
        """Тест: транзакция откатывается при некорректных данных."""
        repo = OrderRepository(db_session)

        invalid_order_data = {
            "customer_name": "Тестовый клиент",
            "delivery_address": "Тестовый адрес",
            "items": [
                {"product_name": "Товар 1", "quantity": -5, "price": 100.0},
            ]
        }

        with pytest.raises(Exception):
            repo.create(invalid_order_data)

        db_session.rollback()

        orders = db_session.query(Order).all()
        items = db_session.query(OrderItem).all()
        assert len(orders) == 0
        assert len(items) == 0

    def test_calculate_delivery_cost_success(self, db_session, httpx_mock):
        """Тест: успешный расчёт стоимости доставки."""
        repo = OrderRepository(db_session)

        order_data = {
            "customer_name": "Тестовый клиент",
            "delivery_address": "Москва, ул. Тверская, д. 10",
            "items": [
                {"product_name": "Товар 1", "quantity": 2, "price": 100.0},
                {"product_name": "Товар 2", "quantity": 3, "price": 50.0},
            ]
        }
        order = repo.create(order_data)

        expected_payload = {
            "address": "Москва, ул. Тверская, д. 10",
            "weight": 2.5
        }

        httpx_mock.add_response(
            method="POST",
            url="https://api.delivery.com/calculate",
            json={"cost": 150.0},
            status_code=200,
            match_json=expected_payload
        )

        cost = repo.calculate_delivery_cost(order.id)

        assert cost == 150.0

    def test_calculate_delivery_cost_api_error(self, db_session, httpx_mock):
        """Тест: ошибка внешнего API вызывает DeliveryCalculationException."""
        repo = OrderRepository(db_session)

        order_data = {
            "customer_name": "Тестовый клиент",
            "delivery_address": "Москва, ул. Тверская, д. 10",
            "items": [
                {"product_name": "Товар 1", "quantity": 1, "price": 100.0},
            ]
        }
        order = repo.create(order_data)

        httpx_mock.add_response(
            method="POST",
            url="https://api.delivery.com/calculate",
            status_code=500
        )

        with pytest.raises(DeliveryCalculationException) as exc_info:
            repo.calculate_delivery_cost(order.id)

        assert "Delivery API returned error: 500" in str(exc_info.value)

    def test_calculate_delivery_cost_order_not_found(self, db_session):
        """Тест: расчёт доставки для несуществующего заказа."""
        repo = OrderRepository(db_session)

        with pytest.raises(EntityNotFoundException) as exc_info:
            repo.calculate_delivery_cost(999)

        assert "Order with id 999 not found" in str(exc_info.value)