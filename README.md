# LAN SNMP Monitoring 📡

Kompletny system do monitorowania urządzeń sieciowych w czasie rzeczywistym z wykorzystaniem bezpiecznego protokołu SNMPv3.

Aplikacja została stworzona jako projekt inżynierski. Składa się z backendu w Pythonie (Flask), nowoczesnego frontendu w React oraz infrastruktury symulacyjnej opartej na kontenerach Docker.

🚀 Funkcjonalności

Monitoring SNMPv3: Bezpieczne pobieranie danych (użytkownik, hasło, szyfrowanie MD5 + DES) z urządzeń sieciowych.

Wizualizacja Live: Interaktywny dashboard (wykresy CPU, RAM, tabela interfejsów) oparty na React + Recharts.

System Alertów: Automatyczne powiadomienia wizualne o stanach krytycznych (np. CPU > 80%, awaria interfejsu).

Historia Danych: Przechowywanie i analiza metryk historycznych dzięki bazie szeregów czasowych InfluxDB.

Raportowanie: Generowanie profesjonalnych raportów PDF ze stanem urządzenia na żądanie (z wykresem historii).

Symulacja: Wbudowany symulator routera Cisco oraz generator obciążenia do celów testowych i demonstracyjnych.

# 🛠️ Architektura i Technologie

Projekt działa w architekturze hybrydowej, co ułatwia rozwój i testowanie:

Infrastruktura (Docker): Baza danych i Symulator urządzenia działają w izolowanych kontenerach, zapewniając stabilne środowisko.

Aplikacja (Host): Backend i Frontend uruchamiane są lokalnie na systemie hosta (Windows/Linux).

Stos technologiczny:
-Backend: Python 3.10+, Flask, PySNMP, FPDF
-Frontend: React 18, Recharts, Axios
-Baza Danych: InfluxDB (Docker)
-Symulator: snmpsim (Docker)

# 📋 Wymagania Wstępne

Przed uruchomieniem upewnij się, że masz zainstalowane:

-Docker Desktop (musi być uruchomiony w tle)
-Python 3.10+ (z dodanym do zmiennej środowiskowej PATH)
-Node.js 16+ (niezbędny do obsługi frontendu i komendy npm)
-Git (do pobrania projektu)

🛠️ Instalacja i Pierwsze Uruchomienie

Wykonaj te kroki tylko raz po pobraniu projektu na dysk.

1. Klonowanie repozytorium

git clone https://github.com/Quiloch/LAN-SNMP-Monitoring.git
cd LAN-SNMP-Monitoring


2. Konfiguracja Backendu (Python)
Otwórz terminal w folderze projektu:

cd backend

Instalacja wymaganych bibliotek:

Jeśli komenda 'pip' nie działa, spróbuj "python -m pip install -r requirements.txt"
pip install -r requirements.txt


Ważne: Utwórz w folderze backend nowy plik o nazwie .env i wklej do niego poniższą konfigurację (jest ona ignorowana przez Git dla bezpieczeństwa):

SNMP_HOST=127.0.0.1

SNMP_PORT=16100

SNMP_USERNAME=simulator

SNMP_AUTH_PASSWORD=snmpauth123

SNMP_PRIV_PASSWORD=snmppriv123

SNMP_CONTEXT_NAME=router

INFLUX_HOST=localhost

INFLUX_PORT=8086

INFLUX_DB=snmp_data





3. Konfiguracja Frontendu (React)

Wróć do głównego katalogu i wejdź do folderu frontend:

cd ../frontend


Pobranie bibliotek (node_modules):

npm install


# ⚡ Codzienne Uruchamianie (Szybki Start)

Gdy masz już zainstalowane biblioteki, uruchomienie systemu jest bardzo proste.

Metoda Automatyczna (Windows):

Upewnij się, że Docker Desktop jest włączony.
W głównym folderze znajdź plik start_monitoring.bat.
Kliknij go dwukrotnie.
Skrypt automatycznie:

-Podniesie kontenery Dockera (Baza + Symulator)
-Otworzy okno z generatorem danych (symulacja ruchu)
-Otworzy okno z serwerem Backend
-Otworzy okno z Frontendem i uruchomi przeglądarkę

# Metoda Ręczna (Terminal):

Jeśli wolisz terminal, uruchom komponenty w osobnych oknach:

-Infrastruktura: docker-compose up -d

-Generator: python generate_load.py

-Backend: cd backend -> python app.py

-Frontend: cd frontend -> npm start

Aplikacja dostępna jest pod adresem: http://localhost:3000 (lub http://localhost:3001, jeśli port 3000 jest zajęty)

# 📂 Struktura Katalogów

/backend - Kod serwera API (Flask), logika SNMP, generator raportów PDF.

/frontend - Kod aplikacji klienckiej (React), style CSS, komponenty wykresów.

/snmpsim - Konfiguracja i dane symulatora routera (pliki .snmprec).

docker-compose.yml - Definicja kontenerów infrastruktury.

generate_load.py - Skrypt Python generujący losowe obciążenie dla symulatora (dla celów demonstracyjnych).

start_monitoring.bat - Launcher dla systemu Windows.

# ❓ Rozwiązywanie problemów

Jeśli napotkasz błędy podczas instalacji lub uruchamiania, sprawdź poniższe rozwiązania.

Błędy Instalacji

🔴 Błąd "npm ... cannot be loaded because running scripts is disabled on this system"

Przyczyna: Zabezpieczenia PowerShell w Windows blokują skrypty.

Rozwiązanie: Otwórz PowerShell jako Administrator i wpisz:

Set-ExecutionPolicy RemoteSigned -Scope CurrentUser


🔴 Błąd "pip : The term 'pip' is not recognized"

Przyczyna: Python nie został dodany do zmiennych środowiskowych (PATH).

Rozwiązanie: Użyj pełnej komendy Pythona:

python -m pip install -r requirements.txt


🔴 Błąd "ModuleNotFoundError: No module named 'asyncore'" (Python 3.12+)

Przyczyna: Moduł asyncore został usunięty z nowych wersji Pythona, a biblioteka SNMP go wymaga.

Rozwiązanie: Upewnij się, że w pliku backend/requirements.txt znajduje się pyasyncore i uruchom pip install -r requirements.txt. Kod aplikacji automatycznie załaduje łatkę.

Błędy Uruchamiania

🔴 Błąd w przeglądarce: "Network Error" / "Błąd połączenia z Backendem"

Przyczyna: Frontend (React) nie widzi Backendu (Flask).

Rozwiązanie:
Sprawdź, czy okno terminala z python app.py jest otwarte i nie ma błędów.
Sprawdź, czy Zapora Windows (Firewall) nie blokuje portu 5001.
Spróbuj wejść bezpośrednio na http://127.0.0.1:5001/snmp – jeśli działa, problem leży w przeglądarce (CORS/AdBlock).

🔴 Wykresy są puste lub stoją w miejscu

Przyczyna: Symulator nie generuje nowych danych lub baza nie zapisuje.

Rozwiązanie:
Upewnij się, że uruchomiłeś skrypt python generate_load.py.
Sprawdź, czy kontenery Docker działają (docker ps).

🔴 Raport PDF nie pobiera się

Przyczyna: Błąd generowania pliku po stronie serwera.

Rozwiązanie: Sprawdź logi w oknie backendu. Upewnij się, że masz
