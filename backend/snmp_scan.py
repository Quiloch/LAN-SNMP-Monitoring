from pysnmp.hlapi import *
from config import SNMP_CONFIG, OIDS

class SNMPManager:
    def __init__(self):
        self.config = SNMP_CONFIG

    def execute_snmp_query(self, oid):
        """Wykonywanie pojedynczego zapytania SNMP GET"""
        try:
            iterator = getCmd(
                SnmpEngine(),
                UsmUserData(
                    self.config['username'],
                    self.config['auth_key'],
                    self.config['priv_key'],
                    authProtocol=usmHMACMD5AuthProtocol,
                    privProtocol=usmDESPrivProtocol
                ),
                UdpTransportTarget((self.config['host'], self.config['port']), timeout=1.0, retries=1),
                ContextData(contextName=self.config['context_name']),
                ObjectType(ObjectIdentity(oid))
            )

            error_indication, error_status, error_index, var_binds = next(iterator)

            if error_indication:
                return f"Error: {error_indication}"
            elif error_status:
                return f"Error: {error_status.prettyPrint()}"
            else:
                # zwrócenie wartości OID
                for var_bind in var_binds:
                    return str(var_bind[1])
        except Exception as e:
            return f"Exception: {str(e)}"

    def get_snmp_data(self):
        """Pobiera dane dla wszystkich zdefiniowanych OID-ów"""
        results = {}
        # iteorwanie po wszystkich OID-ach z konfiguracji
        for key, oid in OIDS.items():
            value = self.execute_snmp_query(oid)
            results[key] = value
        return results

    def test_connection(self):
        """Szybki test połączenia pobierając opis systemu"""
        res = self.execute_snmp_query(OIDS['sysDescr'])
        if "Error" in res or "Exception" in res:
            return "failed"
        return "connected"
    
    def get_devices(self):
        """Zwraca listę urządzeń (mock lub z discovery)"""
        # zwrócenie statycznej listy urządzeń jako przykład symulacji
        return {
            self.config['host']: {
                "status": self.test_connection(),
                "config": self.config
            }
        }