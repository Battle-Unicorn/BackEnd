# Test REM detection z flagami = true
Write-Host "REM: Testing REM Detection with flags=true..." -ForegroundColor Green

$baseUrl = "http://localhost:8080"

# Wysłij najpierw dane z pulsoksymetru (HR)
Write-Host "`n1. Sending plethysmometer data first..." -ForegroundColor Yellow
$plethysmometerData = Get-Content "../mock_data/data_plethysmometer.json" -Raw
$result1 = Invoke-RestMethod -Uri "$baseUrl/embedded/plethysmometer" -Method POST -Body $plethysmometerData -ContentType "application/json"
Write-Host "Plethysmometer data sent: HR samples=$($result1.samples_received)" -ForegroundColor Cyan

# Wyślij flagi z REM=true
Write-Host "`n2. Sending flags with sleep=true, atonia=true..." -ForegroundColor Yellow
Start-Sleep -Seconds 1
$flagsData = Get-Content "../mock_data/data_flags_rem_true.json" -Raw
$result2 = Invoke-RestMethod -Uri "$baseUrl/embedded/flags" -Method POST -Body $flagsData -ContentType "application/json"

Write-Host "FLAGS RESULT:" -ForegroundColor Green
Write-Host "  REM Detected: $($result2.analysis_result.rem_detected)" -ForegroundColor Cyan
Write-Host "  REM Phase: $($result2.analysis_result.current_rem_phase)" -ForegroundColor Cyan
Write-Host "  State Changed: $($result2.analysis_result.state_changed)" -ForegroundColor Yellow
Write-Host "  Sleep Flag: $($result2.input_flags.sleep)" -ForegroundColor Cyan
Write-Host "  Atonia Flag: $($result2.input_flags.atonia)" -ForegroundColor Cyan
Write-Host "  HR Samples Used: $($result2.data_analysis.hr_samples_used)" -ForegroundColor Cyan

# Sprawdź audio files jeśli REM zostało wykryte
if ($result2.analysis_result.rem_detected -eq $true -and $result2.analysis_result.state_changed -eq $true) {
    Write-Host "`n3. REM PHASE DETECTED! Checking for generated audio..." -ForegroundColor Green
    Start-Sleep -Seconds 3  # Czas na wygenerowanie audio
    
    $audioFiles = Get-ChildItem "audio_files\*.mp3" -ErrorAction SilentlyContinue | Sort-Object CreationTime -Descending
    if ($audioFiles) {
        Write-Host "AUDIO: New audio files found:" -ForegroundColor Green
        $audioFiles | Select-Object -First 5 | ForEach-Object { 
            Write-Host "  $($_.Name) ($('{0:yyyy-MM-dd HH:mm:ss}' -f $_.CreationTime))" -ForegroundColor Cyan
        }
    } else {
        Write-Host "WARNING: No new audio files found" -ForegroundColor Yellow
    }
} else {
    Write-Host "`nINFO: No new REM phase detected" -ForegroundColor Yellow
}

Write-Host "`nCOMPLETE: REM detection test complete!" -ForegroundColor Green