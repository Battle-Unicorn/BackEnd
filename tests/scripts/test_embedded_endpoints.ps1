# Test nowych endpointów embedded - osobne endpointy dla każdego sensora
Write-Host "EMBEDDED: Testing New Separate Sensor Endpoints..." -ForegroundColor Green

$baseUrl = "http://localhost:8080"

# Test 1: Wyślij dane z pulsoksymetru
Write-Host "`n1. Testing /embedded/plethysmometer..." -ForegroundColor Yellow
try {
    $plethysmometerData = Get-Content "../mock_data/data_plethysmometer.json" -Raw
    $result1 = Invoke-RestMethod -Uri "$baseUrl/embedded/plethysmometer" -Method POST -Body $plethysmometerData -ContentType "application/json"
    Write-Host "SUCCESS: Plethysmometer data sent!" -ForegroundColor Green
    Write-Host "HR samples received: $($result1.samples_received)" -ForegroundColor Cyan
    Write-Host "Total HR samples stored: $($result1.total_hr_samples_stored)" -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: Plethysmometer data failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Wyślij dane z MPU
Write-Host "`n2. Testing /embedded/mpu..." -ForegroundColor Yellow
try {
    $mpuData = Get-Content "../mock_data/data_mpu.json" -Raw
    $result2 = Invoke-RestMethod -Uri "$baseUrl/embedded/mpu" -Method POST -Body $mpuData -ContentType "application/json"
    Write-Host "SUCCESS: MPU data sent!" -ForegroundColor Green
    Write-Host "MPU samples received: $($result2.samples_received)" -ForegroundColor Cyan
    Write-Host "Total MPU samples stored: $($result2.total_mpu_samples_stored)" -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: MPU data failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Wyślij dane z EMG
Write-Host "`n3. Testing /embedded/emg..." -ForegroundColor Yellow
try {
    $emgData = Get-Content "../mock_data/data_emg.json" -Raw
    $result3 = Invoke-RestMethod -Uri "$baseUrl/embedded/emg" -Method POST -Body $emgData -ContentType "application/json"
    Write-Host "SUCCESS: EMG data sent!" -ForegroundColor Green
    Write-Host "EMG samples received: $($result3.samples_received)" -ForegroundColor Cyan
    Write-Host "Total EMG samples stored: $($result3.total_emg_samples_stored)" -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: EMG data failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Wyślij flagi (po 2 sekundach żeby dane się zprzetwarzały)
Write-Host "`n4. Testing /embedded/flags..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

try {
    $flagsData = Get-Content "../mock_data/data_flags.json" -Raw
    $result4 = Invoke-RestMethod -Uri "$baseUrl/embedded/flags" -Method POST -Body $flagsData -ContentType "application/json"
    Write-Host "SUCCESS: Flags processed!" -ForegroundColor Green
    Write-Host "REM Detected: $($result4.analysis_result.rem_detected)" -ForegroundColor Cyan
    Write-Host "REM Phase: $($result4.analysis_result.current_rem_phase)" -ForegroundColor Cyan
    Write-Host "State Changed: $($result4.analysis_result.state_changed)" -ForegroundColor Yellow
    Write-Host "HR Samples Used: $($result4.data_analysis.hr_samples_used)" -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: Flags processing failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Sprawdź status REM
Write-Host "`n5. Testing /embedded/rem_status..." -ForegroundColor Yellow
try {
    $result5 = Invoke-RestMethod -Uri "$baseUrl/embedded/rem_status" -Method GET
    Write-Host "SUCCESS: REM status retrieved!" -ForegroundColor Green
    Write-Host "Current REM: $($result5.rem_detected)" -ForegroundColor Cyan
    Write-Host "Sleep: $($result5.sleep_detected)" -ForegroundColor Cyan
    Write-Host "Atonia: $($result5.atonia_detected)" -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: REM status failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nCOMPLETE: Embedded endpoints test complete!" -ForegroundColor Green