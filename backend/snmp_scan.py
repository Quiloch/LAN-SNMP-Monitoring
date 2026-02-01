import logging
from pysnmp.hlapi import (
    getCmd,
    SnmpEngine,
    UsmUserData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    usmHMACMD5AuthProtocol,
    usmDESPrivProtocol
)
from config import SNMP_CONFIG, OIDS

logger = logging.getLogger("SNMP-Scan")

class SNMPManager:
    def __init__(self):
        self.config = SNMP_CONFIG

    def execute_snmp_query(self, oid):
        """Wykonywanie zapytania SNMP GET"""
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
                UdpTransportTarget(
                    (self.config['host'], self.config['port']), 
                    timeout=1.0, 
                    retries=1
                ),
                ContextData(contextName=self.config['context_name']),
                ObjectType(ObjectIdentity(oid))
            )

            error_indication, error_status, error_index, var_binds = next(iterator)

            if error_indication:
                return f"Error: {error_indication}"
            elif error_status:
                return f"Error: {error_status.prettyPrint()}"
            else:
                for var_bind in var_binds:
                    return str(var_bind[1])
                    
        except Exception as e:
            return f"Exception: {str(e)}"

    def get_snmp_data(self):
        results = {}
        for key, oid in OIDS.items():
            results[key] = self.execute_snmp_query(oid)
        return results
    
    def test_connection(self):
        if 'sysDescr' in OIDS:
            res = self.execute_snmp_query(OIDS['sysDescr'])
            if "Error" in res or "Exception" in res:
                return "failed"
            return "connected"
        return "unknown"

    def get_devices(self):
        """Zwraca statyczną konfigurację"""
        # Ukrywamy hasła w odpowiedzi API
        safe_config = {k: v for k, v in self.config.items() if 'password' not in k and 'key' not in k}
        return {
            self.config['host']: {
                "status": self.test_connection(),
                "config": safe_config
            }
        }