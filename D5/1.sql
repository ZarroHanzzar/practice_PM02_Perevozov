-- =====================================================
-- 1–5. Создание базы данных и таблиц
-- =====================================================

-- Создаём базу данных (если не существует)
CREATE DATABASE IF NOT EXISTS DeliveryService;
USE DeliveryService;

-- 1. Таблица ресторанов
CREATE TABLE Restaurants (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL
);

-- 2. Таблица блюд
CREATE TABLE Dishes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    restaurant_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    cooking_time_minutes INT NOT NULL, -- время приготовления в минутах
    FOREIGN KEY (restaurant_id) REFERENCES Restaurants(id) ON DELETE CASCADE
);

-- 3. Таблица ингредиентов
CREATE TABLE Ingredients (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- 4. Таблица связей блюд и ингредиентов
CREATE TABLE DishIngredients (
    dish_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    quantity VARCHAR(50) NOT NULL, -- например, "100 г", "2 шт"
    PRIMARY KEY (dish_id, ingredient_id),
    FOREIGN KEY (dish_id) REFERENCES Dishes(id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES Ingredients(id) ON DELETE CASCADE
);

-- 5. Таблица курьеров
CREATE TABLE Couriers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(150) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    status ENUM('available', 'busy', 'offline') DEFAULT 'available'
);

-- 6. Таблица заказов на доставку
CREATE TABLE DeliveryOrders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_date DATE NOT NULL,
    order_time TIME NOT NULL,
    client_name VARCHAR(100) NOT NULL,
    delivery_address VARCHAR(255) NOT NULL,
    restaurant_id INT NOT NULL,
    courier_id INT,
    status ENUM('new', 'cooking', 'delivering', 'delivered', 'cancelled') DEFAULT 'new',
    total_amount DECIMAL(10,2) DEFAULT 0,
    delivery_time_minutes INT, -- фактическое время доставки (в минутах от заказа до доставки)
    FOREIGN KEY (restaurant_id) REFERENCES Restaurants(id),
    FOREIGN KEY (courier_id) REFERENCES Couriers(id)
);

-- 7. Таблица позиций заказа
CREATE TABLE OrderItems (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    dish_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    price_at_time DECIMAL(10,2) NOT NULL, -- цена блюда на момент заказа
    FOREIGN KEY (order_id) REFERENCES DeliveryOrders(id) ON DELETE CASCADE,
    FOREIGN KEY (dish_id) REFERENCES Dishes(id)
);

-- =====================================================
-- 6. Вставить 3 ресторана
-- =====================================================
INSERT INTO Restaurants (name, address, phone) VALUES
('Япошка', 'ул. Ленина, 15', '+7(999)123-45-67'),
('Итальянский дворик', 'пр. Мира, 28', '+7(999)234-56-78'),
('Пицца Хаус', 'ул. Гагарина, 7', '+7(999)345-67-89');

-- =====================================================
-- 7. Вставить 6 блюд с привязкой к ресторанам
-- =====================================================
INSERT INTO Dishes (restaurant_id, name, price, cooking_time_minutes) VALUES
(1, 'Филадельфия ролл', 550.00, 15),
(1, 'Суши с лососем', 180.00, 8),
(1, 'Гункан с угрём', 250.00, 10),
(2, 'Пицца Маргарита', 420.00, 20),
(2, 'Паста Карбонара', 380.00, 15),
(3, 'Пепперони', 490.00, 18);

-- =====================================================
-- 8. Вставить 4 ингредиента (рис, нори, огурец, лосось, сыр) — 5 штук
-- =====================================================
INSERT INTO Ingredients (name) VALUES
('рис'), ('нори'), ('огурец'), ('лосось'), ('сыр');

-- =====================================================
-- 9. Связать блюда с ингредиентами (количество)
-- =====================================================
INSERT INTO DishIngredients (dish_id, ingredient_id, quantity) VALUES
-- Филадельфия ролл
(1, 1, '200 г'), (1, 2, '2 листа'), (1, 3, '50 г'), (1, 4, '100 г'),
-- Суши с лососем
(2, 1, '50 г'), (2, 2, '0.5 листа'), (2, 4, '30 г'),
-- Гункан с угрём (лосось не нужен)
(3, 1, '70 г'), (3, 2, '1 лист'),
-- Пицца Маргарита
(4, 5, '150 г'),
-- Паста Карбонара
(5, 5, '100 г'),
-- Пепперони
(6, 5, '120 г');

-- =====================================================
-- 10. Вставить 2 курьеров
-- =====================================================
INSERT INTO Couriers (full_name, phone, status) VALUES
('Петров Иван Сергеевич', '+7(999)456-78-90', 'available'),
('Сидорова Анна Владимировна', '+7(999)567-89-01', 'busy');

-- =====================================================
-- 11. Создать 4 заказа на доставку
-- =====================================================
INSERT INTO DeliveryOrders (order_date, order_time, client_name, delivery_address, restaurant_id, courier_id, status, total_amount, delivery_time_minutes) VALUES
('2025-06-01', '12:30:00', 'Алексей Смирнов', 'ул. Пушкина, 10', 1, 1, 'delivered', 730.00, 35),
('2025-06-01', '18:15:00', 'Мария Козлова', 'ул. Лермонтова, 5', 2, 2, 'delivered', 800.00, 28),
('2025-06-02', '13:00:00', 'Дмитрий Иванов', 'б-р Энтузиастов, 12', 1, 1, 'delivering', 180.00, NULL),
('2025-06-02', '19:45:00', 'Елена Петрова', 'пер. Садовый, 3', 3, 2, 'cancelled', 490.00, NULL);

-- =====================================================
-- 12. Добавить позиции заказов
-- =====================================================
-- Заказ №1 (сумма 730 = 550 + 180)
INSERT INTO OrderItems (order_id, dish_id, quantity, price_at_time) VALUES
(1, 1, 1, 550.00),
(1, 2, 1, 180.00);

-- Заказ №2 (сумма 800 = 420 + 380)
INSERT INTO OrderItems (order_id, dish_id, quantity, price_at_time) VALUES
(2, 4, 1, 420.00),
(2, 5, 1, 380.00);

-- Заказ №3
INSERT INTO OrderItems (order_id, dish_id, quantity, price_at_time) VALUES
(3, 2, 1, 180.00);

-- Заказ №4 (отменён)
INSERT INTO OrderItems (order_id, dish_id, quantity, price_at_time) VALUES
(4, 6, 1, 490.00);

-- =====================================================
-- 13. Вывести все блюда ресторана «Япошка» с ценами
-- =====================================================
SELECT d.name AS dish_name, d.price
FROM Dishes d
JOIN Restaurants r ON d.restaurant_id = r.id
WHERE r.name = 'Япошка';

-- =====================================================
-- 14. Найти заказы, доставленные курьером «Петров»
-- =====================================================
SELECT do.*
FROM DeliveryOrders do
JOIN Couriers c ON do.courier_id = c.id
WHERE c.full_name LIKE 'Петров%';

-- =====================================================
-- 15. Отсортировать блюда по возрастанию времени приготовления
-- =====================================================
SELECT name, cooking_time_minutes
FROM Dishes
ORDER BY cooking_time_minutes ASC;

-- =====================================================
-- 16. Рассчитать общую сумму заказа №1
-- =====================================================
SELECT order_id, SUM(quantity * price_at_time) AS total_calculated
FROM OrderItems
WHERE order_id = 1
GROUP BY order_id;

-- =====================================================
-- 17. Найти среднее время доставки (доставленные заказы)
-- =====================================================
SELECT AVG(delivery_time_minutes) AS avg_delivery_time
FROM DeliveryOrders
WHERE status = 'delivered' AND delivery_time_minutes IS NOT NULL;

-- =====================================================
-- 18. Вывести рестораны и количество заказов из них
-- =====================================================
SELECT r.name AS restaurant_name, COUNT(do.id) AS orders_count
FROM Restaurants r
LEFT JOIN DeliveryOrders do ON r.id = do.restaurant_id
GROUP BY r.id, r.name;

-- =====================================================
-- 19. Сгруппировать заказы по курьерам и подсчитать общую выручку
-- =====================================================
SELECT c.full_name AS courier_name, SUM(do.total_amount) AS total_revenue
FROM Couriers c
LEFT JOIN DeliveryOrders do ON c.id = do.courier_id AND do.status = 'delivered'
GROUP BY c.id, c.full_name;

-- =====================================================
-- 20. Найти блюда, которые никогда не заказывались (NOT EXISTS)
-- =====================================================
SELECT d.name AS dish_name
FROM Dishes d
WHERE NOT EXISTS (
    SELECT 1 FROM OrderItems oi WHERE oi.dish_id = d.id
);

-- =====================================================
-- 21. Повысить цену всех блюд в ресторане №1 на 5%
-- =====================================================
UPDATE Dishes
SET price = price * 1.05
WHERE restaurant_id = 1;

-- =====================================================
-- 22. Удалить заказ, который был отменён (заказ №4)
-- =====================================================
DELETE FROM DeliveryOrders WHERE id = 4 AND status = 'cancelled';

-- =====================================================
-- 23. Добавить столбец rating (DECIMAL) в Restaurants
-- =====================================================
ALTER TABLE Restaurants ADD COLUMN rating DECIMAL(3,2) DEFAULT NULL;

-- Обновим рейтинг для примера
UPDATE Restaurants SET rating = 4.5 WHERE id = 1;
UPDATE Restaurants SET rating = 4.8 WHERE id = 2;
UPDATE Restaurants SET rating = 4.2 WHERE id = 3;

-- =====================================================
-- 24. Создать представление OrderDetails
-- =====================================================
CREATE VIEW OrderDetails AS
SELECT 
    do.id AS order_id,
    do.client_name,
    do.order_date,
    do.order_time,
    c.full_name AS courier_name,
    GROUP_CONCAT(CONCAT(d.name, ' (', oi.quantity, ' шт.)') SEPARATOR ', ') AS dishes_list,
    SUM(oi.quantity * oi.price_at_time) AS total_sum
FROM DeliveryOrders do
LEFT JOIN Couriers c ON do.courier_id = c.id
LEFT JOIN OrderItems oi ON do.id = oi.order_id
LEFT JOIN Dishes d ON oi.dish_id = d.id
WHERE do.status != 'cancelled'
GROUP BY do.id, do.client_name, do.order_date, do.order_time, c.full_name;

-- =====================================================
-- 25. Сложный запрос: для каждого ресторана самое популярное блюдо,
--     общая выручка, среднее время доставки
-- =====================================================
WITH PopularDishes AS (
    SELECT 
        r.id AS restaurant_id,
        r.name AS restaurant_name,
        d.id AS dish_id,
        d.name AS dish_name,
        COUNT(oi.id) AS order_count,
        ROW_NUMBER() OVER (PARTITION BY r.id ORDER BY COUNT(oi.id) DESC) AS rn
    FROM Restaurants r
    LEFT JOIN Dishes d ON r.id = d.restaurant_id
    LEFT JOIN OrderItems oi ON d.id = oi.dish_id
    LEFT JOIN DeliveryOrders do ON oi.order_id = do.id AND do.status = 'delivered'
    GROUP BY r.id, r.name, d.id, d.name
),
RestaurantStats AS (
    SELECT 
        r.id AS restaurant_id,
        COALESCE(SUM(oi.quantity * oi.price_at_time), 0) AS total_revenue,
        AVG(CASE WHEN do.status = 'delivered' THEN do.delivery_time_minutes END) AS avg_delivery_time
    FROM Restaurants r
    LEFT JOIN Dishes d ON r.id = d.restaurant_id
    LEFT JOIN OrderItems oi ON d.id = oi.dish_id
    LEFT JOIN DeliveryOrders do ON oi.order_id = do.id
    GROUP BY r.id
)
SELECT 
    pd.restaurant_name,
    pd.dish_name AS most_popular_dish,
    pd.order_count AS times_ordered,
    rs.total_revenue,
    ROUND(rs.avg_delivery_time, 2) AS avg_delivery_time_minutes
FROM PopularDishes pd
JOIN RestaurantStats rs ON pd.restaurant_id = rs.restaurant_id
WHERE pd.rn = 1 OR pd.dish_id IS NULL
ORDER BY pd.restaurant_name;

-- =====================================================
-- Дополнительная проверка: просмотр всех данных
-- =====================================================
SELECT '=== Restaurants ===' AS '';
SELECT * FROM Restaurants;

SELECT '=== Dishes ===' AS '';
SELECT * FROM Dishes;

SELECT '=== Couriers ===' AS '';
SELECT * FROM Couriers;

SELECT '=== DeliveryOrders (после удаления cancelled) ===' AS '';
SELECT * FROM DeliveryOrders;

SELECT '=== OrderItems ===' AS '';
SELECT * FROM OrderItems;

SELECT '=== OrderDetails View ===' AS '';
SELECT * FROM OrderDetails;