import os
from dotenv import load_dotenv

load_dotenv()

SNMP_CONFIG = {
    # Konfiguracja SNMP
    'host': os.getenv('SNMP_HOST', '127.0.0.1'),
    'port': int(os.getenv('SNMP_PORT', 16100)),
    'username': os.getenv('SNMP_USERNAME', 'simulator'),
    'auth_password': os.getenv('SNMP_AUTH_PASSWORD', 'snmpauth123'),
    'priv_password': os.getenv('SNMP_PRIV_PASSWORD', 'snmppriv123'),
    'context_name': os.getenv('SNMP_CONTEXT_NAME', 'router'),
    
    # Aliasy kluczy dla zgodności z biblioteką pysnmp
    'auth_key': os.getenv('SNMP_AUTH_PASSWORD', 'snmpauth123'),
    'priv_key': os.getenv('SNMP_PRIV_PASSWORD', 'snmppriv123'),
    
    # Konfiguracja InfluxDB
    'influx_host': os.getenv('INFLUX_HOST', 'localhost'),
    'influx_port': int(os.getenv('INFLUX_PORT', 8086)),
    'influx_db': os.getenv('INFLUX_DB', 'snmp_data')
}


# Definicje OID dla urządzeń Cisco
OIDS = {
    "sysName": "1.3.6.1.2.1.1.5.0",       # Nazwa hosta
    "sysDescr": "1.3.6.1.2.1.1.1.0",      # Opis
    "sysContact": "1.3.6.1.2.1.1.4.0",    # Kontakt 
    "sysLocation": "1.3.6.1.2.1.1.6.0",   # Lokalizacja 
    "sysUpTime": "1.3.6.1.2.1.1.3.0",     # Czas działania 
    

    "cpuUsage": "1.3.6.1.4.1.9.9.109.1.1.1.1.6",  # Wykorzystanie CPU
    "ramTotal": "1.3.6.1.4.1.9.9.48.1.1.1.6",     # Całkowita pamięć RAM
    "ramFree": "1.3.6.1.4.1.9.9.48.1.1.1.5",      # Wolna pamięć RAM
    "ramUsage": "1.3.6.1.4.1.9.9.48.1.1.1.5",     # Wykorzystanie RAM ((Total - Free)/Total * 100)
    
    # Interfejs 1 (GigabitEthernet0/0)
    "if1_Name": "1.3.6.1.2.1.2.2.1.2.1",
    "if1_Status": "1.3.6.1.2.1.2.2.1.8.1",
    "if1_In": "1.3.6.1.2.1.2.2.1.10.1",
    "if1_Out": "1.3.6.1.2.1.2.2.1.16.1",
    "if1_ErrIn": "1.3.6.1.2.1.2.2.1.14.1",   # Błędy wejścia 
    "if1_ErrOut": "1.3.6.1.2.1.2.2.1.20.1",  # Błędy wyjścia 

    # Interfejs 2 (GigabitEthernet0/1) 
    "if2_Name": "1.3.6.1.2.1.2.2.1.2.2",
    "if2_Status": "1.3.6.1.2.1.2.2.1.8.2",
    "if2_In": "1.3.6.1.2.1.2.2.1.10.2",
    "if2_Out": "1.3.6.1.2.1.2.2.1.16.2",
    "if2_ErrIn": "1.3.6.1.2.1.2.2.1.14.2",   # Błędy wejścia 
    "if2_ErrOut": "1.3.6.1.2.1.2.2.1.20.2"   # Błędy wyjścia 
}