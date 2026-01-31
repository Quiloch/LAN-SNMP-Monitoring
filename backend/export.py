from influxdb import InfluxDBClient
from config import SNMP_CONFIG

def export_to_influxdb(data):
    """Wysyła dane numeryczne do bazy InfluxDB"""
    if not data:
        return

    try:
        client = InfluxDBClient(
            host=SNMP_CONFIG['influx_host'],
            port=SNMP_CONFIG['influx_port']
        )
        client.switch_database(SNMP_CONFIG['influx_db'])
        
        points = []
        
        for oid_key, value in data.items():
            # Pomijamy wartości błędne i puste
            if "Error" in str(value) or value == "":
                continue

            try:
                #sprawdzenie czy wartosc to liczba
                clean_value = str(value).replace('.', '', 1)
                
                if clean_value.isdigit():
                    point = {
                        "measurement": "snmp_metrics",
                        "tags": { "oid": oid_key },
                        "fields": { "value": float(value) }
                    }
                    points.append(point)
            except ValueError:
                continue
        
        if points:
            client.write_points(points)
            
    except Exception as e:
        print(f"InfluxDB Error: {e}")