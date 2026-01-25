import csv
from datetime import datetime
from influxdb import InfluxDBClient
from config import SNMP_CONFIG

def export_to_csv(data, filename):
    """Zapisuje słownik danych do pliku CSV"""
    if not data:
        return

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        headers = ["timestamp"] + list(data.keys())
        writer.writerow(headers)
        values = [datetime.now().isoformat()] + list(data.values())
        writer.writerow(values)

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
            # błedy i puste wartości pomijamy
            if "Error" in str(value) or value == "":
                continue

            try:
                # sprawdzenie czy wartosc jest liczbą, sprawdzenie typu int lub float
                clean_value = str(value).replace('.', '', 1)
                
                if clean_value.isdigit():
                    # liczba całkowita lub zmiennoprzecinkowa
                    point = {
                        "measurement": "snmp_metrics",
                        "tags": {
                            "oid": oid_key
                        },
                        "fields": {
                            "value": float(value)
                        }
                    }
                    points.append(point)
                else:
                    # żeby uniknąć mieszania typów w InfluxDB pomijamy string
                    pass
                    
            except ValueError:
                continue
        
        if points:
            client.write_points(points)
            
    except Exception as e:
        print(f"InfluxDB Export Error: {e}")