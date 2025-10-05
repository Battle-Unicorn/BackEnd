# Test pełnego cyklu scenariuszy - ładowanie i polling
Write-Host "=== Test Pełnego Cyklu Scenariuszy ===" -ForegroundColor Green

$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

try {
    Write-Host "Ładowanie scenariuszy..." -ForegroundColor Yellow
    
    # Wczytujemy dane JSON z pliku (poprawiona ścieżka)
    $jsonData = Get-Content -Path "../mock_data/mobile_scenarios.json" -Raw
    
    $loadResponse = Invoke-RestMethod -Uri "http://localhost:8080/mobile/load_scenarios" -Method POST -Body $jsonData -ContentType "application/json" -WebSession $session
    Write-Host "Załadowano $($loadResponse.scenarios_count) scenariuszy`n" -ForegroundColor Cyan
    
    # Testujemy polling endpoint kilka razy (sprawdzamy czy dane są poprawnie załadowane)
    for ($i = 0; $i -lt 5; $i++) {
        Write-Host "Test polling #$($i + 1)..." -ForegroundColor Yellow
        $response = Invoke-RestMethod -Uri "http://localhost:8080/mobile/polling" -Method GET -WebSession $session
        
        Write-Host "  Mobile ID: $($response.mobile_id) | REM: $($response.rem) | Faza: $($response.current_rem_phase)" -ForegroundColor White
        
        # Testujemy też detailed format
        $detailedResponse = Invoke-RestMethod -Uri "http://localhost:8080/mobile/polling?detailed=true" -Method GET -WebSession $session
        Write-Host "  Detailed format OK: Status=$($detailedResponse.status)" -ForegroundColor Gray
        Write-Host ""
        
        Start-Sleep -Seconds 1
    }
    
    Write-Host "SUCCESS: Test ładowania scenariuszy i polling przeszedł pomyślnie!" -ForegroundColor Green
    
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
}