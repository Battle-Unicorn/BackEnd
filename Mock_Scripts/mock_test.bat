@echo off
echo Mock API Tester for Flask Backend
echo.
echo Dostepne komendy:
echo   test_data     - Testuj endpoint /embedded/data
echo   test_status   - Testuj endpoint /embedded/rem_status  
echo   test_reset    - Testuj endpoint /embedded/reset_rem_counter
echo.

if "%1"=="test_data" (
    echo Testowanie wysylania danych z urzadzenia...
    python run_mock.py /embedded/data POST data_embedded.json
    goto end
)

if "%1"=="test_status" (
    echo Sprawdzanie statusu REM...
    python run_mock.py /embedded/rem_status GET
    goto end
)

if "%1"=="test_reset" (
    echo Resetowanie licznika faz REM...
    python run_mock.py /embedded/reset_rem_counter POST
    goto end
)

if "%1"=="" (
    echo Podaj komende: test_data, test_status, lub test_reset
    echo Przyklad: mock_test.bat test_data
    goto end
)

echo Nieznana komenda: %1
echo Dostepne: test_data, test_status, test_reset

:end
pause