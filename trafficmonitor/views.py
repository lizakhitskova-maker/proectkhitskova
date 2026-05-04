from django. shortcuts import render
from django. http import HttpResponse
import random
from datetime import datetime

def index(request):
    # Параметры из URL (можно менять пороги)
  threshold_packets = int(request.GET.get('threshold_packets', 800))
  threshold_bandwidth = int(request.GET.get('threshold_bandwidth', 90)) 

  traffic_data = []
  anomalies  =  []

  for i in range(15):
    packets = random. randint(100, 1500)
    bandwidth = random. randint(20, 120)
    source_ip = f"192.168.1.{random.randint(1, 50)}"
    protocol =  random.choice(["TCP", "UDP", "ICMP"])

    is_anomaly = False
    anomaly_type = None
    
    if packets > threshold_packets:
      is_anomaly = True
      anomaly_type = "Пакетный флуд (DDos)"
    elif  bandwidth > threshold_bandwidth:
       is_anomaly = True
       anomaly_type = "Перегрузка канала"
      
    traffic_data. append({
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
  stats = {
    'total_records': len(traffic_data),
    'anomaly_count': len(anomalies),
    'anomaly_percent': round(len(anomalies) / len(traffic_data) * 100, 1),
    'threshold_packets': threshold_packets,
    'threshold_bandwidth': threshold_bandwidth,
    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')    
  }  

  context = {
    'traffic_data': traffic_data,
    'anomalies': anomalies,
    'stats': stats,
    'title': 'Защита грид-системы от нетипичной сетевой нагрузки'
  }

  return render(request, 'trafficmonitor/index.html', context)