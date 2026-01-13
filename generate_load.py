import time
import random
import os
import subprocess

DATA_FILE = os.path.join("snmpsim", "data", "router.snmprec")

def generate_data():
    print(f"Inicjalizacja symulatora obciążenia sieci...")
    
    # Inicjalizacja liczników ruchu
    traffic_in_1 = 1000000
    traffic_out_1 = 500000
    traffic_in_2 = 2000000
    traffic_out_2 = 100000

    while True:
        # Generowanie losowych wartości dla CPU i RAM
        cpu_load = random.randint(0, 100) 
        ram_total = 1024000
        ram_free = int(ram_total * random.uniform(0.1, 0.9))
        
        # Symulacja przyrostu ruchu sieciowego
        traffic_in_1 += random.randint(1000, 50000)
        traffic_out_1 += random.randint(1000, 50000)
        traffic_in_2 += random.randint(500, 10000)
        traffic_out_2 += random.randint(500, 10000)
        
        # Symulacja statusu interfejsów (losowa awaria)
        if2_status = 2 if random.random() > 0.90 else 1

        content = f"""1.3.6.1.2.1.1.1.0|4|Router Cisco 2900 (Live)
1.3.6.1.2.1.1.5.0|4|Lab-Router-01
1.3.6.1.4.1.9.9.109.1.1.1.1.6|2|{cpu_load}
1.3.6.1.4.1.9.9.48.1.1.1.6|2|{ram_total}
1.3.6.1.4.1.9.9.48.1.1.1.5|2|{ram_free}
# --- Interfejs 1 ---
1.3.6.1.2.1.2.2.1.2.1|4|GigabitEthernet0/0
1.3.6.1.2.1.2.2.1.8.1|2|1
1.3.6.1.2.1.2.2.1.10.1|65|{traffic_in_1}
1.3.6.1.2.1.2.2.1.16.1|65|{traffic_out_1}
# --- Interfejs 2 ---
1.3.6.1.2.1.2.2.1.2.2|4|GigabitEthernet0/1
1.3.6.1.2.1.2.2.1.8.2|2|{if2_status}
1.3.6.1.2.1.2.2.1.10.2|65|{traffic_in_2}
1.3.6.1.2.1.2.2.1.16.2|65|{traffic_out_2}
"""
        try:
            with open(DATA_FILE, "w") as f:
                f.write(content)
            # Wymuszenie przeładowania danych w kontenerze symulatora
            subprocess.run("docker restart snmp-simulator", shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Zaktualizowano parametry: CPU={cpu_load}%, InterfaceStatus={if2_status}")
        except Exception as e:
            print(f"Błąd aktualizacji symulatora: {e}")
        time.sleep(1)

if __name__ == "__main__":
    try:
        generate_data()
    except KeyboardInterrupt:
        print("\nZatrzymano symulator.")