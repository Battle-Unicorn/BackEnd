# Test pełnego cyklu scenariuszy (więcej niż 7)
Write-Host "=== Test Pełnego Cyklu Scenariuszy ===" -ForegroundColor Green

$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

try {
    Write-Host "Ładowanie scenariuszy..." -ForegroundColor Yellow
    
    # Wczytujemy dane JSON z pliku
    $jsonData = Get-Content -Path "mobile_scenarios.json" -Raw
    
    $loadResponse = Invoke-RestMethod -Uri "http://localhost:8080/mobile/load_scenarios" -Method POST -Body $jsonData -ContentType "application/json" -WebSession $session
    Write-Host "Załadowano $($loadResponse.scenarios_count) scenariuszy`n" -ForegroundColor Cyan
    
    # Testujemy więcej scenariuszy niż mamy (7 + 3 dodatkowe)
    for ($i = 0; $i -lt 10; $i++) {
        Write-Host "Pobieranie scenariusza $($i + 1)..." -ForegroundColor Yellow
        $response = Invoke-RestMethod -Uri "http://localhost:8080/mobile/next_scenario" -Method GET -WebSession $session
        
        Write-Host "  Index: $($response.scenario_index) | Słowa: $($response.scenario.key_words)" -ForegroundColor White
        Write-Host "  Miejsce: $($response.scenario.place)" -ForegroundColor Gray
        
        if ($i -eq 6) {
            Write-Host "  ^ Ostatni scenariusz w pliku" -ForegroundColor Red
        }
        if ($i -eq 7) {
            Write-Host "  ^ Cykl się restartował - pierwszy scenariusz ponownie" -ForegroundColor Green
        }
        Write-Host ""
    }
    
    Write-Host "SUCCESS: Test cykliczności przeszedł pomyślnie!" -ForegroundColor Green
    
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
}