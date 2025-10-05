# Test scenariuszy z zachowaniem sesji
Write-Host "=== Test Scenariuszy z Sesja ===" -ForegroundColor Green

# Tworzymy sesję WebRequest do zachowania cookies
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

try {
    Write-Host "1. Ładowanie scenariuszy..." -ForegroundColor Yellow
    
    # Wczytujemy dane JSON z pliku
    $jsonData = Get-Content -Path "mobile_scenarios.json" -Raw
    
    $response1 = Invoke-RestMethod -Uri "http://localhost:8080/mobile/load_scenarios" -Method POST -Body $jsonData -ContentType "application/json" -WebSession $session
    Write-Host "Status: $($response1.status)" -ForegroundColor Green
    Write-Host "Scenariuszy załadowano: $($response1.scenarios_count)" -ForegroundColor Cyan
    
    Write-Host "`n2. Pobieranie pierwszego scenariusza..." -ForegroundColor Yellow
    $response2 = Invoke-RestMethod -Uri "http://localhost:8080/mobile/next_scenario" -Method GET -WebSession $session
    Write-Host "Status: $($response2.status)" -ForegroundColor Green
    Write-Host "Scenariusz #$($response2.scenario_index):" -ForegroundColor Cyan
    Write-Host "  Słowa kluczowe: $($response2.scenario.key_words)" -ForegroundColor White
    Write-Host "  Miejsce: $($response2.scenario.place)" -ForegroundColor White
    
    Write-Host "`n3. Pobieranie drugiego scenariusza..." -ForegroundColor Yellow
    $response3 = Invoke-RestMethod -Uri "http://localhost:8080/mobile/next_scenario" -Method GET -WebSession $session
    Write-Host "Status: $($response3.status)" -ForegroundColor Green
    Write-Host "Scenariusz #$($response3.scenario_index):" -ForegroundColor Cyan
    Write-Host "  Słowa kluczowe: $($response3.scenario.key_words)" -ForegroundColor White
    Write-Host "  Miejsce: $($response3.scenario.place)" -ForegroundColor White
    
    Write-Host "`n4. Pobieranie trzeciego scenariusza..." -ForegroundColor Yellow
    $response4 = Invoke-RestMethod -Uri "http://localhost:8080/mobile/next_scenario" -Method GET -WebSession $session
    Write-Host "Status: $($response4.status)" -ForegroundColor Green
    Write-Host "Scenariusz #$($response4.scenario_index):" -ForegroundColor Cyan
    Write-Host "  Słowa kluczowe: $($response4.scenario.key_words)" -ForegroundColor White
    Write-Host "  Miejsce: $($response4.scenario.place)" -ForegroundColor White
    
    Write-Host "`nSUCCESS: Wszystkie testy przeszły pomyślnie!" -ForegroundColor Green
    
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        Write-Host "Status Code: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}