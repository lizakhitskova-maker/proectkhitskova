from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
import random
from datetime import datetime
import io
import base64
from collections import Counter
import os

# Попытка импорта matplotlib с обработкой ошибки
try:
    import matplotlib
    matplotlib.use('Agg')  # Используем бэкенд без GUI
    import matplotlib.pyplot as plt
    # Настройка русских шрифтов для matplotlib
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['axes.unicode_minus'] = False
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Предупреждение: matplotlib не установлен. Графики не будут отображаться.")


def generate_packet_plot(traffic_data, threshold_packets):
    """Генерация графика пакетов/сек"""
    if not MATPLOTLIB_AVAILABLE:
        return None

    plt.figure(figsize=(10, 5))

    indices = list(range(len(traffic_data)))
    packets = [item['packets'] for item in traffic_data]
    anomalies = [item['is_anomaly'] for item in traffic_data]

    # Цветовая маркировка: красный - аномалия, синий - норма
    colors = ['red' if a else 'blue' for a in anomalies]

    plt.bar(indices, packets, color=colors, alpha=0.7)
    plt.axhline(y=threshold_packets, color='orange', linestyle='--', 
                label=f'Порог: {threshold_packets} пакетов/сек', linewidth=2)
    plt.xlabel('Номер записи')
    plt.ylabel('Пакеты/сек')
    plt.title('График пакетов в секунду')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    # Сохранение в буфер
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return image_base64


def generate_bandwidth_plot(traffic_data, threshold_bandwidth):
    """Генерация графика пропускной способности"""
    if not MATPLOTLIB_AVAILABLE:
        return None

    plt.figure(figsize=(10, 5))

    indices = list(range(len(traffic_data)))
    bandwidth = [item['bandwidth'] for item in traffic_data]
    anomalies = [item['is_anomaly'] for item in traffic_data]

    colors = ['red' if a else 'green' for a in anomalies]

    plt.plot(indices, bandwidth, marker='o', color='purple', alpha=0.7, 
             linestyle='-', linewidth=2, markersize=6)

    # Добавляем цветные точки для аномалий
    anomaly_indices = [i for i, a in enumerate(anomalies) if a]
    anomaly_values = [bandwidth[i] for i in anomaly_indices]
    plt.scatter(anomaly_indices, anomaly_values, color='red', s=100, 
                zorder=5, label='Аномалии')

    plt.axhline(y=threshold_bandwidth, color='orange', linestyle='--', 
                label=f'Порог: {threshold_bandwidth} Мбит/с', linewidth=2)
    plt.xlabel('Номер записи')
    plt.ylabel('Мбит/с')
    plt.title('График пропускной способности')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return image_base64


def generate_protocol_pie_chart(traffic_data):
    """Генерация круговой диаграммы распределения протоколов"""
    if not MATPLOTLIB_AVAILABLE:
        return None

    plt.figure(figsize=(8, 8))

    protocols = [item['protocol'] for item in traffic_data]
    protocol_counts = Counter(protocols)

    colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
    explode = [0.05] * len(protocol_counts)

    plt.pie(protocol_counts.values(), labels=protocol_counts.keys(), 
            autopct='%1.1f%%', colors=colors[:len(protocol_counts)],
            explode=explode[:len(protocol_counts)], shadow=True,
            textprops={'fontsize': 12})
    plt.title('Распределение сетевых протоколов', fontsize=14, fontweight='bold')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return image_base64


def generate_anomaly_pie_chart(traffic_data):
    """Генерация диаграммы соотношения нормального трафика и аномалий"""
    if not MATPLOTLIB_AVAILABLE:
        return None

    plt.figure(figsize=(8, 8))

    anomaly_count = sum(1 for item in traffic_data if item['is_anomaly'])
    normal_count = len(traffic_data) - anomaly_count

    labels = ['Нормальный трафик', 'Аномалии']
    sizes = [normal_count, anomaly_count]
    colors = ['#27ae60', '#e74c3c']
    explode = (0, 0.05) if anomaly_count > 0 else (0, 0)

    plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors,
            explode=explode, shadow=True, startangle=90,
            textprops={'fontsize': 12})
    plt.title('Соотношение нормального трафика и аномалий', 
              fontsize=14, fontweight='bold')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return image_base64


def save_plots_to_png(traffic_data, threshold_packets, threshold_bandwidth):
    """Сохранение всех графиков в PNG файлы (перезапись старых)"""
    if not MATPLOTLIB_AVAILABLE:
        return None, None, None, None

    # Создаем директорию для графиков, если её нет
    plots_dir = 'trafficmonitor/static/plots'
    os.makedirs(plots_dir, exist_ok=True)

    # Используем фиксированные имена файлов (без временной метки)
    packets_path = f'{plots_dir}/packets_plot.png'
    bandwidth_path = f'{plots_dir}/bandwidth_plot.png'
    protocols_path = f'{plots_dir}/protocols_pie.png'
    anomaly_path = f'{plots_dir}/anomaly_ratio_pie.png'

    # График пакетов
    plt.figure(figsize=(10, 5))
    indices = list(range(len(traffic_data)))
    packets = [item['packets'] for item in traffic_data]
    anomalies = [item['is_anomaly'] for item in traffic_data]
    colors = ['red' if a else 'blue' for a in anomalies]
    plt.bar(indices, packets, color=colors, alpha=0.7)
    plt.axhline(y=threshold_packets, color='orange', linestyle='--', 
                label=f'Порог: {threshold_packets} пакетов/сек')
    plt.xlabel('Номер записи')
    plt.ylabel('Пакеты/сек')
    plt.title('График пакетов в секунду')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(packets_path, dpi=150)
    plt.close()

    # График пропускной способности
    plt.figure(figsize=(10, 5))
    bandwidth = [item['bandwidth'] for item in traffic_data]
    plt.plot(indices, bandwidth, marker='o', color='purple', alpha=0.7)
    anomaly_indices = [i for i, a in enumerate(anomalies) if a]
    anomaly_values = [bandwidth[i] for i in anomaly_indices]
    plt.scatter(anomaly_indices, anomaly_values, color='red', s=100, label='Аномалии')
    plt.axhline(y=threshold_bandwidth, color='orange', linestyle='--', 
                label=f'Порог: {threshold_bandwidth} Мбит/с')
    plt.xlabel('Номер записи')
    plt.ylabel('Мбит/с')
    plt.title('График пропускной способности')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(bandwidth_path, dpi=150)
    plt.close()

    # Круговая диаграмма протоколов
    plt.figure(figsize=(8, 8))
    protocols = [item['protocol'] for item in traffic_data]
    protocol_counts = Counter(protocols)
    plt.pie(protocol_counts.values(), labels=protocol_counts.keys(), 
            autopct='%1.1f%%', colors=['#3498db', '#2ecc71', '#e74c3c'])
    plt.title('Распределение сетевых протоколов')
    plt.tight_layout()
    plt.savefig(protocols_path, dpi=150)
    plt.close()

    # Диаграмма соотношения нормы и аномалий
    plt.figure(figsize=(8, 8))
    anomaly_count = sum(1 for item in traffic_data if item['is_anomaly'])
    normal_count = len(traffic_data) - anomaly_count
    plt.pie([normal_count, anomaly_count], labels=['Нормальный трафик', 'Аномалии'],
            autopct='%1.1f%%', colors=['#27ae60', '#e74c3c'], explode=(0, 0.05))
    plt.title('Соотношение нормального трафика и аномалий')
    plt.tight_layout()
    plt.savefig(anomaly_path, dpi=150)
    plt.close()

    # Возвращаем пути к файлам (теперь они всегда одинаковые)
    return '/static/plots/packets_plot.png', \
           '/static/plots/bandwidth_plot.png', \
           '/static/plots/protocols_pie.png', \
           '/static/plots/anomaly_ratio_pie.png'
    
@never_cache
def index(request):
    # Параметры из URL (можно менять пороги)
    threshold_packets = int(request.GET.get('threshold_packets', 800))
    threshold_bandwidth = int(request.GET.get('threshold_bandwidth', 90))

    traffic_data = []
    anomalies = []

    for i in range(15):
        packets = random.randint(100, 1500)
        bandwidth = random.randint(20, 120)
        source_ip = f"192.168.1.{random.randint(1, 50)}"
        protocol = random.choice(["TCP", "UDP", "ICMP"])
        is_anomaly = False
        anomaly_type = None

        if packets > threshold_packets:
            is_anomaly = True
            anomaly_type = "Пакетный флуд (DDoS)"
        elif bandwidth > threshold_bandwidth:
            is_anomaly = True
            anomaly_type = "Перегрузка канала"

        traffic_data.append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'packets': packets,
            'bandwidth': bandwidth,
            'source_ip': source_ip,
            'protocol': protocol,
            'is_anomaly': is_anomaly,
            'anomaly_type': anomaly_type
        })

        if is_anomaly:
            anomalies.append(traffic_data[-1])

    # Генерация графиков в формате base64 для отображения на странице
    packet_plot_base64 = generate_packet_plot(traffic_data, threshold_packets)
    bandwidth_plot_base64 = generate_bandwidth_plot(traffic_data, threshold_bandwidth)
    protocol_chart_base64 = generate_protocol_pie_chart(traffic_data)
    anomaly_chart_base64 = generate_anomaly_pie_chart(traffic_data)

    # Сохранение графиков в PNG файлы
    saved_files = save_plots_to_png(traffic_data, threshold_packets, threshold_bandwidth)

    stats = {
        'total_records': len(traffic_data),
        'anomaly_count': len(anomalies),
        'anomaly_percent': round(len(anomalies) / len(traffic_data) * 100, 1),
        'threshold_packets': threshold_packets,
        'threshold_bandwidth': threshold_bandwidth,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'matplotlib_available': MATPLOTLIB_AVAILABLE
    }

    context = {
        'traffic_data': traffic_data,
        'anomalies': anomalies,
        'stats': stats,
        'title': 'Защита грид-системы от нетипичной сетевой нагрузки',
        'packet_plot': packet_plot_base64,
        'bandwidth_plot': bandwidth_plot_base64,
        'protocol_chart': protocol_chart_base64,
        'anomaly_chart': anomaly_chart_base64,
        'saved_packets_plot': saved_files[0],
        'saved_bandwidth_plot': saved_files[1],
        'saved_protocol_chart': saved_files[2],
        'saved_anomaly_chart': saved_files[3],
        'matplotlib_available': MATPLOTLIB_AVAILABLE
    }

    return render(request, 'trafficmonitor/index.html', context)