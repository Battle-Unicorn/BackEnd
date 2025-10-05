# Test REM z wzrostem HR
Write-Host "REM DEMO: Testing REM detection with HR increase..." -ForegroundColor Green

$baseUrl = "http://localhost:8080"

# 1. Wyślij normalne dane HR (64 BPM average)
Write-Host "`n1. Sending normal HR data (baseline)..." -ForegroundColor Yellow
$normalData = Get-Content "Mock_Scripts/data_sensor_data.json" -Raw
$result1 = Invoke-RestMethod -Uri "$baseUrl/embedded/sensor_data" -Method POST -Body $normalData -ContentType "application/json"
Write-Host "Normal HR data sent. Total HR samples: $($result1.total_samples_stored.hr)" -ForegroundColor Cyan

Start-Sleep -Seconds 2

# 2. Wyślij dane z wysokim HR (80+ BPM average)  
Write-Host "`n2. Sending HIGH HR data (REM simulation)..." -ForegroundColor Yellow
$highHrData = Get-Content "Mock_Scripts/data_sensor_high_hr.json" -Raw
$result2 = Invoke-RestMethod -Uri "$baseUrl/embedded/sensor_data" -Method POST -Body $highHrData -ContentType "application/json"
Write-Host "High HR data sent. Total HR samples: $($result2.total_samples_stored.hr)" -ForegroundColor Cyan

Start-Sleep -Seconds 2

# 3. Wyślij flagi REM (sleep=true, atonia=true)
Write-Host "`n3. Sending REM flags..." -ForegroundColor Yellow
$flagsData = Get-Content "Mock_Scripts/data_flags_rem_true.json" -Raw
$result3 = Invoke-RestMethod -Uri "$baseUrl/embedded/flags" -Method POST -Body $flagsData -ContentType "application/json"

Write-Host "`nREM ANALYSIS RESULTS:" -ForegroundColor Green
Write-Host "  REM Detected: $($result3.analysis_result.rem_detected)" -ForegroundColor Cyan
Write-Host "  REM Phase: $($result3.analysis_result.current_rem_phase)" -ForegroundColor Cyan
Write-Host "  State Changed: $($result3.analysis_result.state_changed)" -ForegroundColor Yellow
Write-Host "  Sleep Flag: $($result3.input_flags.sleep)" -ForegroundColor Cyan  
Write-Host "  Atonia Flag: $($result3.input_flags.atonia)" -ForegroundColor Cyan
Write-Host "  HR Samples: $($result3.data_analysis.hr_samples_used)" -ForegroundColor Cyan

if ($result3.analysis_result.rem_detected -eq $true -and $result3.analysis_result.state_changed -eq $true) {
    Write-Host "`n🎉 REM PHASE DETECTED! Loading scenarios for audio..." -ForegroundColor Green
    
    $scenarioData = Get-Content "Mock_Scripts/mobile_scenarios.json" -Raw
    $scenarioResult = Invoke-RestMethod -Uri "$baseUrl/mobile/load_scenarios" -Method POST -Body $scenarioData -ContentType "application/json"
    Write-Host "Dream scenarios processed: $($scenarioResult.processed_scenarios)" -ForegroundColor Cyan
    
    # Wait for audio generation
    Write-Host "Waiting for audio generation..." -ForegroundColor Yellow
    Start-Sleep -Seconds 8
    
    # Check for new audio files
    $audioFiles = Get-ChildItem "audio_files\*.mp3" -ErrorAction SilentlyContinue | Sort-Object CreationTime -Descending
    if ($audioFiles) {
        Write-Host "`n🎵 GENERATED AUDIO FILES:" -ForegroundColor Green
        $audioFiles | Select-Object -First 5 | ForEach-Object {
            $timeStr = $_.CreationTime.ToString("HH:mm:ss")
            Write-Host "  [$timeStr] $($_.Name)" -ForegroundColor Cyan
        }
    } else {
        Write-Host "`nNo new audio files found" -ForegroundColor Yellow
    }
    
} elseif ($result3.analysis_result.rem_detected -eq $true) {
    Write-Host "`n✅ REM detected but no state change (already in REM)" -ForegroundColor Yellow
} else {
    Write-Host "`n❌ REM not detected" -ForegroundColor Red
}

Write-Host "`nCOMPLETE: REM demo test complete!" -ForegroundColor Green