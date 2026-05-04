import pytest
from datetime import datetime

# === Тестируемые функции (имитация логики из views.py) ===

def detect_anomaly(packets, bandwidth, threshold_packets, threshold_bandwidth):
    """
    Детектирование аномалии.
    Возвращает (is_anomaly, anomaly_type)
    """
    if packets > threshold_packets:
        return (True, "Пакетный флуд (DDoS)")
    elif bandwidth > threshold_bandwidth:
        return (True, "Перегрузка канала")
    else:
        return (False, None)

def generate_stats(traffic_data, threshold_packets, threshold_bandwidth):
    """
    Формирование статистики по данным трафика.
    """
    anomalies = [item for item in traffic_data if item.get('is_anomaly', False)]
    total = len(traffic_data)
    anomaly_count = len(anomalies)
    anomaly_percent = round(anomaly_count / total * 100, 1) if total > 0 else 0
    return {
        'total_records': total,
        'anomaly_count': anomaly_count,
        'anomaly_percent': anomaly_percent,
        'threshold_packets': threshold_packets,
        'threshold_bandwidth': threshold_bandwidth,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def validate_and_get_threshold(value, default, min_val=None, max_val=None):
    """
    Валидация пороговых значений.
    Если value не число или вне диапазона – возвращает default.
    """
    try:
        val = int(value)
        if min_val is not None and val < min_val:
            return default
        if max_val is not None and val > max_val:
            return default
        return val
    except (ValueError, TypeError):
        return default

# === Модульные тесты ===

class TestAnomalyDetection:
    """Тесты для модуля детектирования аномалий"""

    def test_packet_flood_detected(self):
        is_anomaly, atype = detect_anomaly(1000, 50, 800, 90)
        assert is_anomaly is True
        assert atype == "Пакетный флуд (DDoS)"

    def test_bandwidth_overflow_detected(self):
        is_anomaly, atype = detect_anomaly(700, 100, 800, 90)
        assert is_anomaly is True
        assert atype == "Перегрузка канала"

    def test_no_anomaly(self):
        is_anomaly, atype = detect_anomaly(500, 50, 800, 90)
        assert is_anomaly is False
        assert atype is None

    def test_boundary_packets_equal(self):
        is_anomaly, _ = detect_anomaly(800, 50, 800, 90)
        assert is_anomaly is False   # строгое сравнение, равенство не аномалия

    def test_boundary_bandwidth_equal(self):
        is_anomaly, _ = detect_anomaly(700, 90, 800, 90)
        assert is_anomaly is False

class TestStatistics:
    """Тесты для модуля статистического анализа"""

    def test_stats_normal(self):
        data = [
            {'is_anomaly': True},
            {'is_anomaly': False},
            {'is_anomaly': True},
            {'is_anomaly': False},
            {'is_anomaly': False}
        ]
        stats = generate_stats(data, 800, 90)
        assert stats['total_records'] == 5
        assert stats['anomaly_count'] == 2
        assert stats['anomaly_percent'] == 40.0

    def test_stats_empty(self):
        stats = generate_stats([], 800, 90)
        assert stats['total_records'] == 0
        assert stats['anomaly_count'] == 0
        assert stats['anomaly_percent'] == 0

    def test_stats_all_anomalies(self):
        data = [{'is_anomaly': True} for _ in range(10)]
        stats = generate_stats(data, 800, 90)
        assert stats['anomaly_count'] == 10
        assert stats['anomaly_percent'] == 100.0

class TestThresholdValidation:
    """Тесты для валидации пороговых значений"""

    def test_valid_int(self):
        val = validate_and_get_threshold("600", 800, 100, 2000)
        assert val == 600

    def test_invalid_string(self):
        val = validate_and_get_threshold("abc", 800, 100, 2000)
        assert val == 800   # значение по умолчанию

    def test_value_below_min(self):
        val = validate_and_get_threshold("50", 800, 100, 2000)
        assert val == 800

    def test_value_above_max(self):
        val = validate_and_get_threshold("3000", 800, 100, 2000)
        assert val == 800

    def test_negative_value(self):
        val = validate_and_get_threshold("-100", 800, None, None)
        assert val == -100   # если диапазон не задан, отрицательное допустимо
        # с диапазоном:
        val2 = validate_and_get_threshold("-100", 800, 100, 2000)
        assert val2 == 800