# LAN SNMP Monitoring

# 

# System monitorowania parametrów urządzeń sieciowych (CPU, RAM, interfejsy) w czasie rzeczywistym z wykorzystaniem protokołu SNMPv3. Aplikacja zrealizowana w architekturze klient-serwer.

# 

# Opis systemu

# 

# Projekt składa się z trzech głównych modułów:

# 

# Backend (Python/Flask): Odpowiada za cykliczne odpytywanie urządzeń poprzez SNMP, obsługę bazy danych oraz udostępnianie API REST.

# 

# Frontend (React): Interfejs użytkownika prezentujący dane na wykresach oraz tabelach w czasie rzeczywistym.

# 

# Infrastruktura (Docker): Konteneryzacja bazy danych (InfluxDB) oraz symulatora urządzeń sieciowych.

# 

# Funkcjonalności

# 

# Monitorowanie wykorzystania zasobów (CPU, RAM) oraz ruchu sieciowego.

# 

# Obsługa protokołu SNMP w wersji 3 (bezpieczeństwo USM: uwierzytelnianie MD5, szyfrowanie DES).

# 

# Wykrywanie stanów alarmowych (np. obciążenie CPU > 80%, awaria łącza).

# 

# Archiwizacja danych pomiarowych w bazie szeregów czasowych.

# 

# Generowanie raportów PDF z historią pomiarów.

# 

# Wymagania systemowe

# 

# Docker Desktop

# 

# Python 3.10 lub nowszy

# 

# Node.js 16 lub nowszy

# 

# Git

# 

# Instalacja

# 

# 1\. Pobranie repozytorium

# 

# git clone \[https://github.com/Quiloch/LAN-SNMP-Monitoring.git](https://github.com/Quiloch/LAN-SNMP-Monitoring.git)

# cd LAN-SNMP-Monitoring

# 

# 

# 2\. Konfiguracja Backendu

# 

# Należy zainstalować wymagane biblioteki Python w katalogu backend:

# 

# cd backend

# pip install -r requirements.txt

# 

# 

# W tym samym katalogu (backend) należy utworzyć plik .env zawierający konfigurację środowiska:

# 

# SNMP\_HOST=127.0.0.1

# SNMP\_PORT=16100

# SNMP\_USERNAME=simulator

# SNMP\_AUTH\_PASSWORD=snmpauth123

# SNMP\_PRIV\_PASSWORD=snmppriv123

# SNMP\_CONTEXT\_NAME=router

# INFLUX\_HOST=localhost

# INFLUX\_PORT=8086

# INFLUX\_DB=snmp\_data

# 

# 

# 3\. Konfiguracja Frontendu

# 

# Należy pobrać zależności projektu w katalogu frontend:

# 

# cd ../frontend

# npm install

# 

# 

# Uruchomienie

# 

# System można uruchomić na dwa sposoby.

# 

# Metoda automatyczna (Windows)

# 

# W głównym katalogu projektu znajduje się skrypt start\_monitoring.bat. Jego uruchomienie spowoduje:

# 

# Start kontenerów Docker (baza danych, symulator).

# 

# Uruchomienie generatora obciążenia.

# 

# Uruchomienie serwera Backend i aplikacji Frontend w osobnych oknach.

# 

# Metoda ręczna

# 

# Należy uruchomić poszczególne komponenty w osobnych terminalach:

# 

# Infrastruktura: docker-compose up -d

# 

# Generator danych: python generate\_load.py

# 

# Backend: cd backend \&\& python app.py (Serwer nasłuchuje na porcie 5001)

# 

# Frontend: cd frontend \&\& npm start (Aplikacja dostępna pod http://localhost:3000)

# 

# Rozwiązywanie problemów

# 

# Błąd uprawnień PowerShell (running scripts is disabled):

# Należy zmienić politykę wykonywania skryptów dla bieżącego użytkownika:

# Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# 

# Błąd ModuleNotFoundError (Python):

# Upewnij się, że polecenie pip install zostało wykonane wewnątrz katalogu backend. W przypadku problemów z pip, użyj python -m pip install ....

# 

# Brak danych na wykresach:

# Weryfikacja działania skryptu generate\_load.py oraz kontenerów Docker (docker ps).

# 

# Błąd połączenia (Network Error):

# Sprawdź, czy port 5001 nie jest blokowany przez zaporę systemu Windows.

