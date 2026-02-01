import time
import random
import os
import subprocess

DATA_FILE = os.path.join("snmpsim", "data", "router.snmprec")

def generate_data():
    print(f"Generator startuje")
    
    traffic_in_1 = 1000000
    traffic_out_1 = 500000
    traffic_in_2 = 2000000
    traffic_out_2 = 100000
    
    # Symulacja uptime
    uptime_ticks = 532231

    while True:
        cpu_load = random.randint(20, 100) 
        ram_total = 1024000
        ram_free = int(ram_total * random.uniform(0.1, 0.9))
        
        traffic_in_1 += random.randint(1000, 50000)
        traffic_out_1 += random.randint(1000, 50000)
        traffic_in_2 += random.randint(500, 10000)
        traffic_out_2 += random.randint(500, 10000)
        
        if2_status = 2 if random.random() > 0.95 else 1
        
        # Inkrementacja uptime
        uptime_ticks += 1500

        # Budowanie pliku .snmprec

        content = f"""1.3.6.1.2.1.1.1.0|4|Cisco IOS Software, C2900 Software
1.3.6.1.2.1.1.3.0|67|{uptime_ticks}         
1.3.6.1.2.1.1.4.0|4|admin@network.local     
1.3.6.1.2.1.1.5.0|4|RTR-Main-01              
1.3.6.1.2.1.1.6.0|4|Serwerownia B, Szafa 2  
1.3.6.1.4.1.9.9.109.1.1.1.1.6|2|{cpu_load}  
1.3.6.1.4.1.9.9.48.1.1.1.6|2|{ram_total}    
1.3.6.1.4.1.9.9.48.1.1.1.5|2|{ram_free}     

# Interfejs 1
1.3.6.1.2.1.2.2.1.2.1|4|GigabitEthernet0/0  
1.3.6.1.2.1.2.2.1.8.1|2|1
1.3.6.1.2.1.2.2.1.10.1|65|{traffic_in_1}    
1.3.6.1.2.1.2.2.1.14.1|65|0
1.3.6.1.2.1.2.2.1.16.1|65|{traffic_out_1}   
1.3.6.1.2.1.2.2.1.20.1|65|0

# Interfejs 2
1.3.6.1.2.1.2.2.1.2.2|4|GigabitEthernet0/1
1.3.6.1.2.1.2.2.1.8.2|2|{if2_status}        
1.3.6.1.2.1.2.2.1.10.2|65|{traffic_in_2}    
1.3.6.1.2.1.2.2.1.14.2|65|5
1.3.6.1.2.1.2.2.1.16.2|65|{traffic_out_2}   
1.3.6.1.2.1.2.2.1.20.2|65|0
"""
        try:
            with open(DATA_FILE, "w") as f:
                f.write(content)
            # restart zeby dane mogly sie zaktualizowac
            subprocess.run("docker restart snmp-simulator", shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Zaktualizowano: Uptime={uptime_ticks}, Lokalizacja=Serwerownia B")
        except Exception as e:
            print(f"Błąd: {e}")

        time.sleep(15)

if __name__ == "__main__":
    try:
        generate_data()
    except KeyboardInterrupt:
        print("\n Zatrzymano.")