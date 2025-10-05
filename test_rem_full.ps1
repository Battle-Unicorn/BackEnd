# Test REM z większą ilością danych (symulujemy 15+ minut)
Write-Host "REM FULL: Testing REM with sufficient data..." -ForegroundColor Green

$baseUrl = "http://localhost:8080"

# Wyślij dane sensorowe 5 razy żeby nazbierać więcej danych
Write-Host "`n1. Sending multiple sensor data packets..." -ForegroundColor Yellow

for ($i = 1; $i -le 5; $i++) {
    Write-Host "  Sending packet $i/5..." -ForegroundColor Cyan
    $sensorData = Get-Content "Mock_Scripts/data_sensor_data.json" -Raw
    $result = Invoke-RestMethod -Uri "$baseUrl/embedded/sensor_data" -Method POST -Body $sensorData -ContentType "application/json"
    Write-Host "    HR stored: $($result.total_samples_stored.hr)" -ForegroundColor Gray
    Start-Sleep -Seconds 1
}

Write-Host "`n2. Sending flags with REM conditions..." -ForegroundColor Yellow
$flagsData = Get-Content "Mock_Scripts/data_flags_rem_true.json" -Raw
$result2 = Invoke-RestMethod -Uri "$baseUrl/embedded/flags" -Method POST -Body $flagsData -ContentType "application/json"

Write-Host "`nRESULTS:" -ForegroundColor Green
Write-Host "  REM Detected: $($result2.analysis_result.rem_detected)" -ForegroundColor Cyan
Write-Host "  REM Phase: $($result2.analysis_result.current_rem_phase)" -ForegroundColor Cyan  
Write-Host "  State Changed: $($result2.analysis_result.state_changed)" -ForegroundColor Yellow
Write-Host "  HR Samples Used: $($result2.data_analysis.hr_samples_used)" -ForegroundColor Cyan
Write-Host "  Average HR: $($result2.data_analysis.hr_stats.avg_hr_all)" -ForegroundColor Cyan

if ($result2.analysis_result.rem_detected -eq $true) {
    Write-Host "`nREM DETECTED! Checking audio generation..." -ForegroundColor Green
    
    # Sprawdz czy sa scenariusze zaladowane
    Write-Host "Loading dream scenarios for audio generation..." -ForegroundColor Yellow
    $scenarioData = Get-Content "Mock_Scripts/mobile_scenarios.json" -Raw
    $scenarioResult = Invoke-RestMethod -Uri "$baseUrl/mobile/load_scenarios" -Method POST -Body $scenarioData -ContentType "application/json"
    Write-Host "Scenarios loaded: $($scenarioResult.processed_scenarios)" -ForegroundColor Cyan
    
    # Poczekaj na generowanie audio
    Start-Sleep -Seconds 5
    
    # Sprawdz nowe pliki audio
    $audioFiles = Get-ChildItem "audio_files\*.mp3" -ErrorAction SilentlyContinue | Sort-Object CreationTime -Descending
    if ($audioFiles) {
        Write-Host "NEW AUDIO FILES:" -ForegroundColor Green
        $audioFiles | Select-Object -First 3 | ForEach-Object { 
            Write-Host "  $($_.Name)" -ForegroundColor Cyan
        }
    }
} else {
    Write-Host "`nREM not detected with current conditions" -ForegroundColor Red
}

Write-Host "`nCOMPLETE: Full REM test complete!" -ForegroundColor Green