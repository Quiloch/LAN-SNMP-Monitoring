from flask import Flask, jsonify, render_template, send_file, request
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import base64
import time
import threading
import logging
from influxdb import InfluxDBClient
from snmp_scan import SNMPManager
from config import SNMP_CONFIG
from export import export_to_csv, export_to_influxdb
from discovery import DeviceDiscovery
import os
from report import generate_pdf_report
from io import BytesIO  # <--- WAŻNY IMPORT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SNMP-Monitor")

app = Flask(__name__)
CORS(app) 

snmp_manager = SNMPManager()
device_discovery = DeviceDiscovery()

influx_client = InfluxDBClient(
    host=SNMP_CONFIG['influx_host'],
    port=SNMP_CONFIG['influx_port']
)

try:
    influx_client.create_database(SNMP_CONFIG['influx_db'])
    logger.info("Nawiązano połączenie z InfluxDB")
except Exception as e:
    logger.warning(f"Błąd inicjalizacji bazy danych: {e}")

def background_monitoring():
    time.sleep(5)
    logger.info("Uruchomiono proces monitorowania w tle")
    while True:
        try:
            data = snmp_manager.get_snmp_data()
            error_found = any("Error" in str(val) or "Exception" in str(val) for val in data.values())
            
            if not error_found and data:
                export_to_influxdb(data)
                logger.debug(f"Zarchiwizowano dane: CPU={data.get('cpuUsage')}%")
            else:
                logger.warning("Błąd odczytu SNMP lub brak danych")
        except Exception as e:
            logger.error(f"Wyjątek w wątku monitorującym: {e}")
        time.sleep(10)

if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    monitor_thread = threading.Thread(target=background_monitoring, daemon=True)
    monitor_thread.start()

def get_history_data(hours=1):
    try:
        influx_client.switch_database(SNMP_CONFIG['influx_db'])
        cpu_query = f"SELECT value FROM snmp_metrics WHERE oid = 'cpuUsage' AND time > now() - {hours}h"
        ram_query = f"SELECT value FROM snmp_metrics WHERE oid = 'ramUsage' AND time > now() - {hours}h"
        
        cpu_res = list(influx_client.query(cpu_query).get_points())
        ram_res = list(influx_client.query(ram_query).get_points())

        history = []
        for i, cpu_point in enumerate(cpu_res):
            ram_val = 0
            if i < len(ram_res):
                ram_val = ram_res[i]['value']
            
            item = {
                'timestamp': cpu_point['time'],
                'data': { 'cpuUsage': cpu_point['value'], 'ramUsage': ram_val }
            }
            history.append(item)
        return history
    except Exception as e:
        logger.error(f"Błąd pobierania historii: {str(e)}")
        return []

@app.route('/')
def home():
    return snmp_manager.get_snmp_data()

@app.route('/snmp')
def get_snmp_data_endpoint():
    data = snmp_manager.get_snmp_data()
    return jsonify(data)

@app.route('/dashboard')
def dashboard():
    try:
        data = snmp_manager.get_snmp_data()
        history = get_history_data(hours=1)
        json_data = json.dumps(history)
        encoded_history = base64.b64encode(json_data.encode()).decode()
        return render_template('dashboard.html', data=data, history=encoded_history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history')
def get_history_api():
    try:
        history = get_history_data(hours=24)
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/devices')
def get_devices():
    return jsonify(device_discovery.devices)

@app.route('/api/status')
def get_status():
    return jsonify({"status": "running", "timestamp": datetime.now().isoformat()})

@app.route('/export/report/pdf')
def export_pdf_report():
    try:
        data = snmp_manager.get_snmp_data()
        filename = f"raport_sieciowy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # 1. Generujemy PDF do zmiennej (bajtów)
        pdf_bytes = generate_pdf_report(data)
        
        # 2. Tworzymy wirtualny plik w pamięci
        buffer = BytesIO(pdf_bytes)
        buffer.seek(0)
        
        # 3. Wysyłamy do przeglądarki
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        logger.error(f"Błąd generowania PDF: {e}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)