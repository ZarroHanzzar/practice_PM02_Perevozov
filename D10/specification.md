# Спецификация валидации заказов

## Общее описание
Система валидации заказов проверяет корректность входящих заказов и вычисляет риск-скор.

## Входные данные (JSON Schema)
```json
{
  "type": "object",
  "required": ["order_id", "user_id", "items", "total_amount", "order_time", "user_created_at"],
  "properties": {
    "order_id": {
      "type": "string",
      "minLength": 1,
      "description": "Уникальный идентификатор заказа"
    },
    "user_id": {
      "type": "string",
      "minLength": 1,
      "description": "Идентификатор пользователя"
    },
    "items": {
      "type": "array",
      "minItems": 1,
      "maxItems": 100,
      "items": {
        "type": "object",
        "required": ["product_id", "quantity", "price"],
        "properties": {
          "product_id": {"type": "string", "minLength": 1},
          "quantity": {"type": "integer", "minimum": 1, "maximum": 999},
          "price": {"type": "number", "minimum": 0.01, "maximum": 1000000}
        }
      }
    },
    "total_amount": {
      "type": "number",
      "minimum": 0.01,
      "maximum": 10000000,
      "description": "Общая сумма заказа"
    },
    "order_time": {
      "type": "string",
      "format": "date-time",
      "description": "Время создания заказа (UTC)"
    },
    "user_created_at": {
      "type": "string",
      "format": "date-time",
      "description": "Дата регистрации пользователя"
    }
  }
}