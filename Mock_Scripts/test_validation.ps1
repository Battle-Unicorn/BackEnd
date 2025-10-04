# Test walidacji bledow w endpoincie load_scenarios
Write-Host "=== Test Walidacji Bledow ===" -ForegroundColor Green

$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

Write-Host "`n1. Test pustego body..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8080/mobile/load_scenarios" -Method POST -Body "" -ContentType "application/json" -WebSession $session
    Write-Host "ERROR: Powinien zwrocic blad!" -ForegroundColor Red
} catch {
    Write-Host "OK: Prawidlowo zwrocil blad" -ForegroundColor Green
}

Write-Host "`n2. Test nieprawidlowego JSON..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8080/mobile/load_scenarios" -Method POST -Body "invalid json" -ContentType "application/json" -WebSession $session
    Write-Host "ERROR: Powinien zwrocic blad!" -ForegroundColor Red
} catch {
    Write-Host "OK: Prawidlowo zwrocil blad" -ForegroundColor Green
}

Write-Host "`n3. Test JSON bez dream_keywords..." -ForegroundColor Yellow
try {
    $invalidJson = '{"mobile_id": "TEST_001"}'
    $response = Invoke-RestMethod -Uri "http://localhost:8080/mobile/load_scenarios" -Method POST -Body $invalidJson -ContentType "application/json" -WebSession $session
    Write-Host "ERROR: Powinien zwrocic blad!" -ForegroundColor Red
} catch {
    Write-Host "OK: Prawidlowo zwrocil blad" -ForegroundColor Green
}

Write-Host "`n4. Test prawidlowego JSON..." -ForegroundColor Yellow
try {
    $validJson = Get-Content -Path "mobile_scenarios.json" -Raw
    $response = Invoke-RestMethod -Uri "http://localhost:8080/mobile/load_scenarios" -Method POST -Body $validJson -ContentType "application/json" -WebSession $session
    Write-Host "OK: Prawidlowo zaladowal: $($response.scenarios_count) scenariuszy" -ForegroundColor Green
    Write-Host "  Mobile ID: $($response.mobile_id)" -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: Nie powinien zwrocic bledu!" -ForegroundColor Red
}

Write-Host "`nSUCCESS: Wszystkie testy walidacji zakonczone!" -ForegroundColor Green