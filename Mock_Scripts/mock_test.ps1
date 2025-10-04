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
    "reset" {
        Write-Host ">> Resetowanie licznika faz REM..." -ForegroundColor Yellow
        .\run_mock.ps1 /embedded/reset_rem_counter POST
    }
    default {
        Write-Host "ERROR: Nieznana komenda: $testName" -ForegroundColor Red
        Write-Host "Dostepne: data, rem, status, reset" -ForegroundColor Yellow
        Write-Host "Uzyj '.\mock_test.ps1 help' aby zobaczyc pomoc" -ForegroundColor Cyan
        exit 1
    }
}