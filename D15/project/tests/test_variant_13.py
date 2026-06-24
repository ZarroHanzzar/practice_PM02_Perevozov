# tests/test_variant_13.py
import pytest
import time
from app.services.report import generate_report


class TestReportPerformance:
    """Тесты производительности для generate_report()."""
    
    def test_report_generation_performance_basic(self, sample_data):
        """
        Базовый тест производительности.
        Проверяет, что generate_report() обрабатывает 10_000 записей менее чем за 2 секунды.
        """
        # Arrange - данные уже подготовлены фикстурой sample_data
        
        # Act
        start = time.perf_counter()
        result = generate_report(sample_data)
        elapsed = time.perf_counter() - start
        
        # Assert
        assert elapsed < 2.0, f"Report generation took {elapsed:.2f}s, expected < 2.0s"
        assert result["total_records"] == 10000
        
    def test_report_generation_with_benchmark(self, benchmark, sample_data):
        """
        Тест с использованием pytest-benchmark для точного измерения производительности.
        """
        # Act - используем benchmark для измерения времени выполнения
        result = benchmark(generate_report, sample_data)
        
        # Assert
        assert result["total_records"] == 10000
        assert result["average"] == 49995.0  # (0 + 99990) / 2
        
    def test_report_generation_scaling(self, sample_data_small):
        """
        Тест масштабируемости: сравнение времени для разных объемов данных.
        """
        # Маленький набор данных (100 записей)
        start_small = time.perf_counter()
        result_small = generate_report(sample_data_small)
        elapsed_small = time.perf_counter() - start_small
        
        # Большой набор данных (10_000 записей)
        large_data = [{"id": i, "value": i * 10} for i in range(10000)]
        start_large = time.perf_counter()
        result_large = generate_report(large_data)
        elapsed_large = time.perf_counter() - start_large
        
        # Проверка корректности
        assert result_small["total_records"] == 100
        assert result_large["total_records"] == 10000
        
        # Проверка масштабируемости (не более чем в 50 раз при 100x увеличении данных)
        ratio = elapsed_large / elapsed_small
        assert ratio < 50, f"Scaling ratio too high: {ratio:.2f}"
        
    def test_report_generation_correctness(self, sample_data):
        """
        Проверка корректности результатов.
        """
        start = time.perf_counter()
        result = generate_report(sample_data)
        elapsed = time.perf_counter() - start
        
        # Проверка вычислений
        assert result["total_records"] == 10000
        assert result["sum"] == 499950000  # sum of 0, 10, 20, ..., 99990
        assert result["average"] == 49995.0
        assert result["min"] == 0
        assert result["max"] == 99990
        assert result["median"] == 49995.0
        
        # Проверка группировки
        assert result["grouped"]["low"] > 0
        assert result["grouped"]["medium"] > 0
        
        # Проверка времени
        assert elapsed < 2.0
        
    def test_report_generation_edge_cases(self):
        """Тест краевых случаев."""
        # Пустой список
        result = generate_report([])
        assert result["total_records"] == 0
        assert result["sum"] == 0
        
        # Один элемент
        data = [{"id": 1, "value": 100}]
        result = generate_report(data)
        assert result["total_records"] == 1
        assert result["average"] == 100.0
        assert result["min"] == 100
        assert result["max"] == 100
        
    def test_report_generation_with_negative_values(self):
        """Тест с отрицательными значениями."""
        data = [{"id": i, "value": i * 10 - 50} for i in range(100)]
        start = time.perf_counter()
        result = generate_report(data)
        elapsed = time.perf_counter() - start
        
        assert result["total_records"] == 100
        assert result["min"] == -50
        assert result["max"] == 940
        assert elapsed < 0.5