# Mock tester dla Flask API - wersja PowerShell
# Uzycie: .\mock_test.ps1 <test_name>

param(
    [string]$testName = ""
)

Write-Host "=== Flask API Mock Tester (PowerShell) ===" -ForegroundColor Magenta
Write-Host ""

if ($testName -eq "" -or $testName -eq "help") {
    Write-Host "Dostepne testy:" -ForegroundColor Yellow
    Write-Host "  data     - Testuj endpoint /embedded/data (normalne dane z urzadzenia)" -ForegroundColor White
    Write-Host "  rem      - Testuj endpoint /embedded/data (dane z potencjalnym REM)" -ForegroundColor White
    Write-Host "  status   - Testuj endpoint /embedded/rem_status (sprawdzenie statusu REM)" -ForegroundColor White
    Write-Host "  mobile_polling   - Testuj endpoint /mobile/polling (dane dla aplikacji mobilnej)" -ForegroundColor White
    Write-Host "  load_scenarios   - Testuj endpoint /mobile/load_scenarios (ladowanie scenariuszy)" -ForegroundColor White
    Write-Host "  next_scenario    - Testuj endpoint /mobile/next_scenario (kolejny scenariusz)" -ForegroundColor White
    Write-Host "  test_scenarios   - Pelny test scenariuszy z sesja (ładowanie + 3 scenariusze)" -ForegroundColor White
    Write-Host "  test_cycle       - Test cykliczności scenariuszy (10 scenariuszy)" -ForegroundColor White
    Write-Host "  test_validation  - Test walidacji błędów endpointa load_scenarios" -ForegroundColor White
    Write-Host "  reset    - Testuj endpoint /embedded/reset_rem_counter (reset licznika)" -ForegroundColor White
    Write-Host ""
    Write-Host "Dostepne pliki danych:" -ForegroundColor Yellow
    Write-Host "  data_embedded.json  - Normalne dane (sleep=false, atonia=false)" -ForegroundColor Gray
    Write-Host "  data_rem_test.json  - Dane testowe REM (wyzsze HR)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Przyklad uzycia:" -ForegroundColor Green
    Write-Host "  .\mock_test.ps1 data" -ForegroundColor Cyan
    Write-Host "  .\mock_test.ps1 rem" -ForegroundColor Cyan
    Write-Host "  .\mock_test.ps1 status" -ForegroundColor Cyan
    Write-Host "  .\mock_test.ps1 mobile_polling" -ForegroundColor Cyan
    Write-Host "  .\mock_test.ps1 load_scenarios" -ForegroundColor Cyan
    Write-Host "  .\mock_test.ps1 next_scenario" -ForegroundColor Cyan
    Write-Host "  .\mock_test.ps1 test_scenarios" -ForegroundColor Cyan
    Write-Host "  .\mock_test.ps1 test_cycle" -ForegroundColor Cyan
    Write-Host "  .\mock_test.ps1 test_validation" -ForegroundColor Cyan
    Write-Host "  .\mock_test.ps1 reset" -ForegroundColor Cyan
    exit 0
}

switch ($testName.ToLower()) {
    "data" {
        Write-Host ">> Testowanie wysylania normalnych danych z urzadzenia..." -ForegroundColor Yellow
        .\run_mock.ps1 /embedded/data POST data_embedded.json
    }
    "rem" {
        Write-Host ">> Testowanie wysylania danych REM z urzadzenia..." -ForegroundColor Yellow
        .\run_mock.ps1 /embedded/data POST data_rem_test.json
    }
    "status" {
        Write-Host ">> Sprawdzanie statusu REM..." -ForegroundColor Yellow
        .\run_mock.ps1 /embedded/rem_status GET
    }
    "mobile_polling" {
        Write-Host ">> Testowanie endpointa aplikacji mobilnej..." -ForegroundColor Yellow
        .\run_mock.ps1 /mobile/polling GET
    }
    "load_scenarios" {
        Write-Host ">> Testowanie ladowania scenariuszy snow..." -ForegroundColor Yellow
        .\run_mock.ps1 /mobile/load_scenarios POST mobile_scenarios.json
    }
    "next_scenario" {
        Write-Host ">> Testowanie pobierania kolejnego scenariusza..." -ForegroundColor Yellow
        Write-Host "UWAGA: Pojedyncze żądania nie zachowują sesji!" -ForegroundColor Red
        Write-Host "Użyj 'test_scenarios' dla pełnego testu z sesją." -ForegroundColor Yellow
        .\run_mock.ps1 /mobile/next_scenario GET
    }
    "test_scenarios" {
        Write-Host ">> Pełny test scenariuszy z zachowaniem sesji..." -ForegroundColor Yellow
        .\test_scenarios.ps1
    }
    "test_cycle" {
        Write-Host ">> Test cykliczności scenariuszy..." -ForegroundColor Yellow
        .\test_cycle.ps1
    }
    "test_validation" {
        Write-Host ">> Test walidacji błędów..." -ForegroundColor Yellow
        .\test_validation.ps1
    }
    "reset" {
        Write-Host ">> Resetowanie licznika faz REM..." -ForegroundColor Yellow
        .\run_mock.ps1 /embedded/reset_rem_counter POST
    }
    default {
        Write-Host "ERROR: Nieznana komenda: $testName" -ForegroundColor Red
        Write-Host "Dostepne: data, rem, status, mobile_polling, load_scenarios, next_scenario, test_scenarios, test_cycle, test_validation, reset" -ForegroundColor Yellow
        Write-Host "Uzyj '.\mock_test.ps1 help' aby zobaczyc pomoc" -ForegroundColor Cyan
        exit 1
    }
}