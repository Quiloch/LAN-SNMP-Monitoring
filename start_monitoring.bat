@echo off
TITLE LAN-SNMP-Monitoring Launcher
COLOR 0A

echo ========================================================
echo      URUCHAMIANIE SYSTEMU LAN-SNMP-MONITORING
echo ========================================================
echo.

:: 1. Infrastruktura Docker
echo [1/4] Startowanie Docker (Symulator + Baza)...
docker-compose up -d
IF %ERRORLEVEL% NEQ 0 (
    COLOR 0C
    echo [BLAD] Docker nie odpowiedzial.
    pause
    exit
)
echo [OK] Infrastruktura dziala.
echo.

:: 2. Generator Danych
echo [2/4] Uruchamianie Generatora...
start "Generator Danych" cmd /k "python generate_load.py"
echo [OK] Generator uruchomiony.
echo.

:: 3. Backend Flask
echo [3/4] Uruchamianie Backendu...
cd backend
start "Backend Flask" cmd /k "python app.py"
cd ..
echo [OK] Backend uruchomiony.
echo.

:: 4. Frontend React
echo [4/4] Uruchamianie Frontendu...
cd frontend
echo     (Otworzy sie przegladarka)
start "Frontend React" cmd /k "npm start"
cd ..

echo.
echo ========================================================
echo  SYSTEM URUCHOMIONY
echo ========================================================
echo.

:WAIT_LOOP
echo Aby zakonczyc prace, wpisz 'Q' i nacisnij ENTER.
set "UserChoice="
set /p "UserChoice=Twoj wybor: "
if /i "%UserChoice%"=="Q" goto SHUTDOWN
goto WAIT_LOOP

:SHUTDOWN
echo.
echo ========================================================
echo      ZAMYKANIE SYSTEMU
echo ========================================================

:: 1. Instrukcja dla użytkownika
echo.
echo [INFO] Prosze recznie zamknac nastepujace okna:
echo        1. Okno przegladarki z Dashboardem.
echo        2. Okno terminala z 'python app.py' (Backend).
echo        3. Okno terminala z 'python generate_load.py' (Generator).
echo        4. Okno terminala z 'npm start' (Frontend).
echo.

:: 2. Zatrzymywanie Dockera
echo [2/2] Zatrzymywanie kontenerow (Baza + Symulator)...
docker-compose stop

echo.
echo [KONIEC]
timeout /t 5 >nul
exit