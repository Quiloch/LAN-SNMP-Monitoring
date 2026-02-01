# Dla python 3.12+
import os
import sys
try:
    import asynchat
    import asyncore
except ImportError:
    try:
        import pyasyncore as asyncore
        sys.modules['asyncore'] = asyncore
        import asynchat
        sys.modules['asynchat'] = asynchat
    except ImportError:
        pass 
    
base_dir = os.path.dirname(os.path.abspath(__file__))
vendor_dir = os.path.join(base_dir, 'vendor')
if os.path.exists(vendor_dir):
    sys.path.insert(0, vendor_dir)

from flask import Flask, jsonify, render_template, send_file
from flask_cors import CORS
from datetime import datetime
import json
import base64
import time
import threading
import logging
from influxdb import InfluxDBClient
from io import BytesIO
from snmp_scan import SNMPManager
from config import SNMP_CONFIG
from export import export_to_influxdb
from report import create_report

# Logowanie
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SNMP-Monitor")

app = Flask(__name__)
CORS(app) 

snmp_manager = SNMPManager()

# Połączenie z InfluxDB
influx_client = InfluxDBClient(
    host=SNMP_CONFIG['influx_host'],
    port=SNMP_CONFIG['influx_port']
)

try:
    influx_client.create_database(SNMP_CONFIG['influx_db'])
    logger.info("Połączono z bazą danych InfluxDB")
except Exception as e:
    logger.warning(f"Ostrzeżenie InfluxDB: {e}")

def background_monitoring():
    time.sleep(5)
    logger.info("Uruchamianie monitoringu w tle...")
    
    while True:
        try:
            data = snmp_manager.get_snmp_data()
            error_found = any("Error" in str(val) or "Exception" in str(val) for val in data.values())
            
            if not error_found and data:
                export_to_influxdb(data)
                logger.debug(f"Zapisano dane: CPU={data.get('cpuUsage')}%")
        except Exception as e:
            logger.error(f"Błąd monitoringu: {e}")
        
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
        logger.error(f"Błąd historii DB: {str(e)}")
        return []


@app.route('/')
def home():
    return jsonify(snmp_manager.get_snmp_data())

@app.route('/snmp')
def get_snmp_data_endpoint():
    return jsonify(snmp_manager.get_snmp_data())

@app.route('/api/history')
def get_history_api():
    try:
        history = get_history_data(hours=24)
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/devices')
def get_devices():
    return jsonify(snmp_manager.get_devices())

@app.route('/api/status')
def get_status():
    return jsonify({"status": "running", "timestamp": datetime.now().isoformat()})

@app.route('/export/report/pdf')
def export_pdf_report():
    try:
        data = snmp_manager.get_snmp_data()
        history = get_history_data(hours=1)
        
        filename = f"raport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_bytes = create_report(data, history)
        
        buffer = BytesIO(pdf_bytes)
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')
    except Exception as e:
        logger.error(f"Błąd PDF: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)