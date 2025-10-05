# Test nowych endpointów embedded - sensor_data i flags
Write-Host "EMBEDDED: Testing New Embedded Endpoints..." -ForegroundColor Green

$baseUrl = "http://localhost:8080"

# Test 1: Wyślij dane sensorowe
Write-Host "`n1. Testing /embedded/sensor_data..." -ForegroundColor Yellow
try {
    $sensorData = Get-Content "Mock_Scripts/data_sensor_data.json" -Raw
    $result1 = Invoke-RestMethod -Uri "$baseUrl/embedded/sensor_data" -Method POST -Body $sensorData -ContentType "application/json"
    Write-Host "SUCCESS: Sensor data sent!" -ForegroundColor Green
    Write-Host "HR samples received: $($result1.samples_received.hr)" -ForegroundColor Cyan
    Write-Host "MPU samples received: $($result1.samples_received.mpu)" -ForegroundColor Cyan
    Write-Host "EMG samples received: $($result1.samples_received.emg)" -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: Sensor data failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Wyślij flagi (po 2 sekundach żeby dane się zprzetwarzały)
Write-Host "`n2. Testing /embedded/flags..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

try {
    $flagsData = Get-Content "Mock_Scripts/data_flags.json" -Raw
    $result2 = Invoke-RestMethod -Uri "$baseUrl/embedded/flags" -Method POST -Body $flagsData -ContentType "application/json"
    Write-Host "SUCCESS: Flags processed!" -ForegroundColor Green
    Write-Host "REM Detected: $($result2.analysis_result.rem_detected)" -ForegroundColor Cyan
    Write-Host "REM Phase: $($result2.analysis_result.current_rem_phase)" -ForegroundColor Cyan
    Write-Host "State Changed: $($result2.analysis_result.state_changed)" -ForegroundColor Yellow
    Write-Host "HR Samples Used: $($result2.data_analysis.hr_samples_used)" -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: Flags processing failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Sprawdź status REM
Write-Host "`n3. Testing /embedded/rem_status..." -ForegroundColor Yellow
try {
    $result3 = Invoke-RestMethod -Uri "$baseUrl/embedded/rem_status" -Method GET
    Write-Host "SUCCESS: REM status retrieved!" -ForegroundColor Green
    Write-Host "Current REM: $($result3.rem_detected)" -ForegroundColor Cyan
    Write-Host "Sleep: $($result3.sleep_detected)" -ForegroundColor Cyan
    Write-Host "Atonia: $($result3.atonia_detected)" -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: REM status failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Test legacy endpoint (dla kompatybilności)
Write-Host "`n4. Testing legacy /embedded/data..." -ForegroundColor Yellow
try {
    $legacyData = '{"device_id": "TEST_001", "test": true}'
    $result4 = Invoke-RestMethod -Uri "$baseUrl/embedded/data" -Method POST -Body $legacyData -ContentType "application/json"
    Write-Host "INFO: Legacy endpoint response:" -ForegroundColor Yellow
    Write-Host $result4.message -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: Legacy endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nCOMPLETE: Embedded endpoints test complete!" -ForegroundColor Green