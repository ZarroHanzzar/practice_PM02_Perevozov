class EntityNotFoundException(Exception):
    """Исключение, выбрасываемое при попытке найти несуществующую сущность."""
    pass


class DeliveryCalculationException(Exception):
    """Исключение, выбрасываемое при ошибке расчёта доставки."""
    pass