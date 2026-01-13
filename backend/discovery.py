import threading
from datetime import datetime

class DeviceDiscovery:
    def __init__(self):
        self.devices = {}
        self.lock = threading.Lock()
        
    def add_device(self, ip, data):
        with self.lock:
            self.devices[ip] = {
                'last_seen': datetime.now(),
                'data': data
            }
    
    def remove_inactive_devices(self, timeout_minutes=5):
        with self.lock:
            current_time = datetime.now()
            inactive = [
                ip for ip, device in self.devices.items()
                if (current_time - device['last_seen']).total_seconds() > timeout_minutes * 60
            ]
            for ip in inactive:
                del self.devices[ip]