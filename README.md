# LAN SNMP Monitoring

System monitorowania parametrów urządzeń sieciowych (CPU, RAM, interfejsy) w czasie rzeczywistym z wykorzystaniem protokołu SNMPv3. Aplikacja zrealizowana w architekturze klient-serwer.

## Opis systemu

Projekt składa się z trzech głównych modułów:
1. **Backend (Python/Flask):** Odpowiada za cykliczne odpytywanie urządzeń poprzez SNMP, obsługę bazy danych oraz udostępnianie API REST.
2. **Frontend (React):** Interfejs użytkownika prezentujący dane na wykresach oraz tabelach w czasie rzeczywistym.
3. **Infrastruktura (Docker):** Konteneryzacja bazy danych (InfluxDB) oraz symulatora urządzeń sieciowych.

## Funkcjonalności

* Monitorowanie wykorzystania zasobów (CPU, RAM) oraz ruchu sieciowego.
* Obsługa protokołu SNMP w wersji 3 (bezpieczeństwo USM: uwierzytelnianie MD5, szyfrowanie DES).
* Wykrywanie stanów alarmowych (np. obciążenie CPU > 80%, awaria łącza).
* Archiwizacja danych pomiarowych w bazie szeregów czasowych.
* Generowanie raportów PDF z historią pomiarów.

## Wymagania systemowe

* Docker Desktop
* Python 3.10 lub nowszy
* Node.js 16 lub nowszy
* Git

## Instalacja

### 1. Pobranie repozytorium

```
git clone https://github.com/Quiloch/LAN-SNMP-Monitoring.git
cd LAN-SNMP-Monitoring
```
2. Konfiguracja Backendu
Należy zainstalować wymagane biblioteki Python w katalogu backend:


```
cd backend
pip install -r requirements.txt
```
W tym samym katalogu (backend) należy utworzyć plik .env zawierający konfigurację środowiska:
```
SNMP_HOST=127.0.0.1
SNMP_PORT=16100
SNMP_USERNAME=simulator
SNMP_AUTH_PASSWORD=snmpauth123
SNMP_PRIV_PASSWORD=snmppriv123
SNMP_CONTEXT_NAME=router
INFLUX_HOST=localhost
INFLUX_PORT=8086
INFLUX_DB=snmp_data
```
3. Konfiguracja Frontendu
Należy pobrać zależności projektu w katalogu frontend:


```
cd ../frontend
npm install
```

# Uruchomienie
System można uruchomić na dwa sposoby.

## Metoda automatyczna (Windows)
W głównym katalogu projektu znajduje się skrypt start_monitoring.bat. Jego uruchomienie spowoduje:

Start kontenerów Docker (baza danych, symulator).

Uruchomienie generatora obciążenia.

Uruchomienie serwera Backend i aplikacji Frontend w osobnych oknach. W oknie Frontendu może pojawić się pytanie o uruchomienie na porcie 3001, jeśli port 3000 jest zajęty.

## Metoda ręczna
Należy uruchomić poszczególne komponenty w osobnych terminalach:

Infrastruktura: ```docker-compose up -d```

Generator danych: ```python generate_load.py```

Backend: ```cd backend && python app.py``` (Serwer nasłuchuje na porcie 5001)

Frontend: ```cd frontend && npm start``` (Aplikacja dostępna pod http://localhost:3000)

# Rozwiązywanie problemów
Błąd uprawnień PowerShell (running scripts is disabled): Należy zmienić politykę wykonywania skryptów dla bieżącego użytkownika: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

Błąd ModuleNotFoundError (Python): Upewnij się, że polecenie pip install zostało wykonane wewnątrz katalogu backend. W przypadku problemów z pip, użyj python -m pip install ....

Brak danych na wykresach: Weryfikacja działania skryptu generate_load.py oraz kontenerów Docker (docker ps).

Błąd połączenia (Network Error): Sprawdź, czy port 5001 nie jest blokowany przez zaporę systemu Windows.
