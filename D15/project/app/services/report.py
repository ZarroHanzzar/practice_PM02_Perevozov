# app/services/report.py
from typing import List, Dict, Any
from collections import defaultdict
import statistics


def generate_report(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Генерирует сложный отчет на основе переданных данных.
    
    Args:
        data: Список словарей с полями id и value
        
    Returns:
        Dict с различными статистическими показателями
    """
    if not data:
        return {
            "total_records": 0,
            "sum": 0,
            "average": 0,
            "median": 0,
            "min": 0,
            "max": 0,
            "grouped": {},
            "percentiles": {}
        }
    
    # Извлечение значений
    values = [item["value"] for item in data]
    
    # Базовые статистики
    total_records = len(data)
    sum_values = sum(values)
    average = sum_values / total_records
    median = statistics.median(values)
    min_value = min(values)
    max_value = max(values)
    
    # Группировка по диапазонам
    grouped = defaultdict(int)
    for value in values:
        if value < 1000:
            grouped["low"] += 1
        elif value < 10000:
            grouped["medium"] += 1
        elif value < 50000:
            grouped["high"] += 1
        else:
            grouped["very_high"] += 1
    
    # Процентили
    percentiles = {
        "p25": statistics.quantiles(values, n=4)[0] if len(values) >= 4 else None,
        "p50": statistics.quantiles(values, n=4)[1] if len(values) >= 4 else None,
        "p75": statistics.quantiles(values, n=4)[2] if len(values) >= 4 else None,
    }
    
    return {
        "total_records": total_records,
        "sum": sum_values,
        "average": round(average, 2),
        "median": round(median, 2),
        "min": min_value,
        "max": max_value,
        "grouped": dict(grouped),
        "percentiles": percentiles,
    }