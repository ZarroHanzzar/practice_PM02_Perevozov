-- ============================================
-- 1. СОЗДАНИЕ БАЗЫ ДАННЫХ
-- ============================================
CREATE DATABASE IF NOT EXISTS pizzeria_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE pizzeria_db;

-- ============================================
-- 2. ТАБЛИЦА ПОЛЬЗОВАТЕЛЕЙ
-- ============================================
CREATE TABLE IF NOT EXISTS `Пользователи` (
    `id_пользователя` INT PRIMARY KEY AUTO_INCREMENT,
    `логин` VARCHAR(50) UNIQUE NOT NULL,
    `пароль_hash` VARCHAR(255) NOT NULL,
    `роль` ENUM('admin', 'worker') DEFAULT 'worker',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 3. ТАБЛИЦА ЗАКАЗОВ
-- ============================================
CREATE TABLE IF NOT EXISTS `Заказы` (
    `id_заказа` INT PRIMARY KEY AUTO_INCREMENT,
    `номер_заказа` VARCHAR(20) UNIQUE,
    `имя_клиента` VARCHAR(100) NOT NULL,
    `телефон` VARCHAR(20) NOT NULL,
    `адрес` TEXT,
    `тип_пиццы` VARCHAR(100) NOT NULL,
    `размер` ENUM('Маленькая', 'Средняя', 'Большая') DEFAULT 'Средняя',
    `количество` INT DEFAULT 1,
    `цена_за_штуку` DECIMAL(10, 2),
    `общая_сумма` DECIMAL(10, 2),
    `статус` ENUM('новый', 'подтвержден', 'готовится', 'доставляется', 'завершен', 'отменен') DEFAULT 'новый',
    `способ_оплаты` ENUM('Наличные', 'Карта', 'Онлайн') DEFAULT 'Наличные',
    `комментарий` TEXT,
    `создал` INT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `обновлен` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`создал`) REFERENCES `Пользователи`(`id_пользователя`) ON DELETE SET NULL,
    INDEX idx_status (`статус`),
    INDEX idx_created_at (`created_at`),
    INDEX idx_client_phone (`телефон`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 4. ТАБЛИЦА МЕНЮ ПИЦЦ
-- ============================================
CREATE TABLE IF NOT EXISTS `Меню` (
    `id_пиццы` INT PRIMARY KEY AUTO_INCREMENT,
    `название` VARCHAR(100) NOT NULL,
    `описание` TEXT,
    `цена_маленькая` DECIMAL(10, 2),
    `цена_средняя` DECIMAL(10, 2),
    `цена_большая` DECIMAL(10, 2),
    `ингредиенты` TEXT,
    `доступна` BOOLEAN DEFAULT TRUE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 5. ТАБЛИЦА ИСТОРИИ ИЗМЕНЕНИЙ ЗАКАЗОВ
-- ============================================
CREATE TABLE IF NOT EXISTS `История_заказов` (
    `id_истории` INT PRIMARY KEY AUTO_INCREMENT,
    `id_заказа` INT NOT NULL,
    `статус_был` VARCHAR(50),
    `статус_стал` VARCHAR(50),
    `кто_изменил` INT,
    `комментарий` TEXT,
    `changed_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`id_заказа`) REFERENCES `Заказы`(`id_заказа`) ON DELETE CASCADE,
    FOREIGN KEY (`кто_изменил`) REFERENCES `Пользователи`(`id_пользователя`) ON DELETE SET NULL,
    INDEX idx_changed_at (`changed_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 6. ТАБЛИЦА ЕЖЕДНЕВНЫХ ОТЧЕТОВ
-- ============================================
CREATE TABLE IF NOT EXISTS `Ежедневные_отчеты` (
    `id_отчета` INT PRIMARY KEY AUTO_INCREMENT,
    `дата` DATE NOT NULL UNIQUE,
    `всего_заказов` INT DEFAULT 0,
    `завершено_заказов` INT DEFAULT 0,
    `отменено_заказов` INT DEFAULT 0,
    `общая_выручка` DECIMAL(10, 2) DEFAULT 0,
    `средний_чек` DECIMAL(10, 2) DEFAULT 0,
    `популярные_пиццы` TEXT,
    `создан` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_date (`дата`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 7. ВСТАВКА ДАННЫХ В МЕНЮ (ПРИМЕРЫ)
-- ============================================
INSERT IGNORE INTO `Меню` (`название`, `описание`, `цена_маленькая`, `цена_средняя`, `цена_большая`, `ингредиенты`) VALUES
('Маргарита', 'Томатный соус, моцарелла, базилик', 350.00, 450.00, 550.00, 'томатный соус, сыр моцарелла, базилик'),
('Пепперони', 'Томатный соус, пепперони, моцарелла', 400.00, 500.00, 600.00, 'томатный соус, пепперони, сыр моцарелла'),
('Гавайская', 'Томатный соус, курица, ананас, моцарелла', 380.00, 480.00, 580.00, 'томатный соус, курица, ананас, сыр моцарелла'),
('Четыре сыра', 'Сливочный соус, 4 вида сыра', 420.00, 520.00, 620.00, 'сливочный соус, пармезан, моцарелла, горгондзола, фета'),
('Мясная', 'Томатный соус, бекон, ветчина, пепперони, моцарелла', 450.00, 550.00, 650.00, 'томатный соус, бекон, ветчина, пепперони, сыр моцарелла');

-- ============================================
-- 8. ВСТАВКА ТЕСТОВОГО АДМИНА (пароль: admin123)
-- ============================================
-- Для реального использования замените хеш на сгенерированный bcrypt
INSERT IGNORE INTO `Пользователи` (`логин`, `пароль_hash`, `роль`) VALUES
('admin', '$2b$12$YK5xTwZwBkR6KJqJfqDyy.PWYwP8QW7QYjQRvQ7YwP8QW7QYjQRvQ', 'admin');

-- ============================================
-- 9. УДАЛЕНИЕ СТАРЫХ ПРОЦЕДУР (ЕСЛИ ЕСТЬ)
-- ============================================
DROP PROCEDURE IF EXISTS GetSalesReport;
DROP TRIGGER IF EXISTS before_insert_orders;
DROP TRIGGER IF EXISTS before_update_order_amount;

-- ============================================
-- 10. СОЗДАНИЕ ХРАНИМЫХ ПРОЦЕДУР ДЛЯ ОТЧЕТОВ
-- ============================================

DELIMITER //

CREATE PROCEDURE GetSalesReport(IN start_date DATE, IN end_date DATE)
BEGIN
    SELECT 
        DATE(o.`created_at`) as дата,
        COUNT(*) as количество_заказов,
        SUM(o.`общая_сумма`) as выручка,
        AVG(o.`общая_сумма`) as средний_чек,
        COUNT(CASE WHEN o.`статус` = 'завершен' THEN 1 END) as завершено,
        COUNT(CASE WHEN o.`статус` = 'отменен' THEN 1 END) as отменено
    FROM `Заказы` o
    WHERE DATE(o.`created_at`) BETWEEN start_date AND end_date
    GROUP BY DATE(o.`created_at`)
    ORDER BY дата DESC;
END//

-- ============================================
-- 11. ТРИГГЕР ДЛЯ АВТОМАТИЧЕСКОГО СОЗДАНИЯ НОМЕРА ЗАКАЗА
-- ============================================

CREATE TRIGGER before_insert_orders
BEFORE INSERT ON `Заказы`
FOR EACH ROW
BEGIN
    DECLARE next_number INT;
    
    IF NEW.`номер_заказа` IS NULL THEN
        SELECT COALESCE(MAX(CAST(SUBSTRING_INDEX(`номер_заказа`, '-', -1) AS UNSIGNED)), 0) + 1 
        INTO next_number
        FROM `Заказы` 
        WHERE DATE(`created_at`) = CURDATE();
        
        SET NEW.`номер_заказа` = CONCAT('PZ-', DATE_FORMAT(NOW(), '%Y%m%d'), '-', LPAD(next_number, 3, '0'));
    END IF;
END//

-- ============================================
-- 12. ТРИГГЕР ДЛЯ АВТОМАТИЧЕСКОГО РАСЧЕТА СУММЫ ЗАКАЗА
-- ============================================

CREATE TRIGGER before_insert_order_amount
BEFORE INSERT ON `Заказы`
FOR EACH ROW
BEGIN
    DECLARE price DECIMAL(10, 2);
    
    -- Получаем цену из меню в зависимости от размера
    SELECT 
        CASE NEW.`размер`
            WHEN 'Маленькая' THEN `цена_маленькая`
            WHEN 'Средняя' THEN `цена_средняя`
            WHEN 'Большая' THEN `цена_большая`
        END INTO price
    FROM `Меню`
    WHERE `название` = NEW.`тип_пиццы` AND `доступна` = TRUE
    LIMIT 1;
    
    IF price IS NOT NULL THEN
        SET NEW.`цена_за_штуку` = price;
        SET NEW.`общая_сумма` = price * NEW.`количество`;
    END IF;
END//

DELIMITER ;

-- ============================================
-- 13. ПРЕДСТАВЛЕНИЕ ДЛЯ АКТИВНЫХ ЗАКАЗОВ
-- ============================================
CREATE OR REPLACE VIEW `Активные_заказы` AS
SELECT 
    o.`id_заказа`,
    o.`номер_заказа`,
    o.`имя_клиента`,
    o.`телефон`,
    o.`тип_пиццы`,
    o.`размер`,
    o.`количество`,
    o.`общая_сумма`,
    o.`статус`,
    o.`created_at`,
    u.`логин` as создал
FROM `Заказы` o
LEFT JOIN `Пользователи` u ON o.`создал` = u.`id_пользователя`
WHERE o.`статус` NOT IN ('завершен', 'отменен')
ORDER BY o.`created_at` DESC;

-- ============================================
-- 14. ПРЕДСТАВЛЕНИЕ ДЛЯ СТАТИСТИКИ ПО СОТРУДНИКАМ
-- ============================================
CREATE OR REPLACE VIEW `Статистика_сотрудников` AS
SELECT 
    u.`id_пользователя`,
    u.`логин`,
    COUNT(o.`id_заказа`) as всего_заказов,
    SUM(CASE WHEN o.`статус` = 'завершен' THEN 1 ELSE 0 END) as завершенных,
    SUM(CASE WHEN o.`статус` = 'отменен' THEN 1 ELSE 0 END) as отмененных,
    SUM(o.`общая_сумма`) as общая_выручка,
    AVG(o.`общая_сумма`) as средний_чек
FROM `Пользователи` u
LEFT JOIN `Заказы` o ON u.`id_пользователя` = o.`создал`
WHERE u.`роль` = 'worker'
GROUP BY u.`id_пользователя`;

-- ============================================
-- 15. ПРОВЕРКА СОЗДАНИЯ ТАБЛИЦ
-- ============================================
SHOW TABLES;

-- ============================================
-- 16. ТЕСТОВЫЙ ЗАКАЗ ДЛЯ ПРОВЕРКИ
-- ============================================
INSERT INTO `Заказы` (`имя_клиента`, `телефон`, `тип_пиццы`, `размер`, `количество`) VALUES
('Тестовый Клиент', '+79991234567', 'Маргарита', 'Средняя', 2);

SELECT 'База данных успешно создана!' as Статус;