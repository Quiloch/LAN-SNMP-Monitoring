LAN SNMP Monitoring

Kompletny system do monitorowania urządzeń sieciowych w czasie rzeczywistym z wykorzystaniem bezpiecznego protokołu SNMPv3.

Projekt składa się z backendu w Pythonie (Flask), nowoczesnego frontendu w React oraz infrastruktury (baza danych, symulator sieci) opartej na kontenerach Docker.

Funkcjonalności

Monitoring SNMPv3: Bezpieczne pobieranie danych (authPriv: MD5 + DES) z urządzeń sieciowych.

Wizualizacja Live: Interaktywny dashboard (wykresy CPU, RAM, tabela interfejsów) oparty na React + Recharts.

System Alertów: Automatyczne powiadomienia wizualne o stanach krytycznych (np. CPU > 80%, awaria interfejsu).

Historia Danych: Przechowywanie metryk w bazie szeregów czasowych InfluxDB.

Raportowanie: Generowanie profesjonalnych raportów PDF ze stanem urządzenia na żądanie.

Symulacja: Wbudowany symulator routera Cisco oraz generator obciążenia do celów testowych i demonstracyjnych.

Architektura i Technologie

Projekt działa w architekturze hybrydowej:

Infrastruktura (Docker): Baza danych i Symulator urządzenia działają w izolowanych kontenerach.

Aplikacja (Host): Backend i Frontend uruchamiane są lokalnie dla łatwego developmentu.

Backend: Python 3.10+, Flask, PySNMP, Pandas, FPDF

Frontend: React 18, Recharts, Axios

Baza Danych: InfluxDB (Docker)

Symulator: snmpsim (Docker)

Wymagania

Przed uruchomieniem upewnij się, że masz zainstalowane:

Docker Desktop (musi być uruchomiony)

Python 3.10+

Node.js 16+ (do frontendu)

Szybki Start (Windows)

Dla systemu Windows przygotowano skrypt automatyzujący uruchomienie wszystkich komponentów.

Upewnij się, że Docker Desktop działa.

Uruchom plik start_monitoring.bat (dwukrotne kliknięcie).

Skrypt otworzy 3 okna terminala i automatycznie uruchomi przeglądarkę z aplikacją.

Instalacja Ręczna (Krok po kroku)

Jeśli wolisz uruchamiać komponenty ręcznie lub korzystasz z innego systemu (Linux/macOS), wykonaj poniższe kroki.

1. Klonowanie repozytorium

git clone [https://github.com/Quiloch/LAN-SNMP-Monitoring.git](https://github.com/Quiloch/LAN-SNMP-Monitoring.git)

cd LAN-SNMP-Monitoring

2. Uruchomienie Infrastruktury (Docker)

Uruchom bazę danych i symulator routera:

docker-compose up -d


3. Konfiguracja i Uruchomienie Backendu

Otwórz nowy terminal w folderze projektu:

cd backend
# Instalacja zależności
pip install -r requirements.txt


Upewnij się, że plik .env w folderze backend istnieje i zawiera konfigurację:

SNMP_HOST=127.0.0.1
SNMP_PORT=16100
SNMP_USERNAME=simulator
SNMP_AUTH_PASSWORD=snmpauth123
SNMP_PRIV_PASSWORD=snmppriv123
SNMP_CONTEXT_NAME=router
INFLUX_HOST=localhost
INFLUX_PORT=8086
INFLUX_DB=snmp_data


Uruchom serwer:

python app.py


Backend wystartuje na porcie 5001.

4. Uruchomienie Frontendu

Otwórz kolejny terminal:

cd frontend
# Instalacja zależności (tylko pierwszy raz)
npm install
# Uruchomienie serwera deweloperskiego
npm start


Aplikacja otworzy się pod adresem http://localhost:3000.

5. Symulacja Danych (Opcjonalne)

Aby wykresy pokazywały zmienne dane (symulacja ruchu sieciowego i obciążenia), uruchom generator w osobnym oknie (główny folder):

python generate_load.py


Struktura Katalogów

/backend - Kod serwera API (Flask), logika SNMP, generator raportów PDF.

/frontend - Kod aplikacji klienckiej (React), style CSS, komponenty wykresów.

/snmpsim - Konfiguracja i dane symulatora routera (pliki .snmprec).

docker-compose.yml - Definicja kontenerów infrastruktury.

generate_load.py - Skrypt Python generujący losowe obciążenie dla symulatora (dla celów demonstracyjnych).

start_monitoring.bat - Launcher dla systemu Windows.

Rozwiązywanie problemów

Wykresy są puste / Błąd połączenia:

Sprawdź, czy python app.py działa i nie zgłasza błędów w konsoli.

Upewnij się, że Docker działa (docker ps powinno pokazać kontenery snmp-simulator i influxdb).

Sprawdź, czy firewall/antywirus nie blokuje portu 5001 lub 16100.

Błąd "Module not found" w Pythonie:
Upewnij się, że zainstalowałeś zależności: pip install -r requirements.txt.

Błąd "Module not found" w React:
Wejdź do folderu frontend i wykonaj npm install.
