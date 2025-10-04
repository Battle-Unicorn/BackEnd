# Test REM Detection System - Simple PowerShell Script
# Run this script when Flask server is already running

Write-Host "=== TEST SYSTEMU DETEKCJI REM ===" -ForegroundColor Cyan

# Load test data
$jsonPath = "Mock_Scripts\data_embedded.json"
if (-not (Test-Path $jsonPath)) {
    Write-Host "ERROR: File not found $jsonPath" -ForegroundColor Red
    exit 1
}

$testData = Get-Content $jsonPath | ConvertFrom-Json

# Endpoint URLs
$dataUrl = "http://localhost:8080/embedded/data"
$statusUrl = "http://localhost:8080/embedded/rem_status"

Write-Host "Testing Flask endpoints..." -ForegroundColor Yellow

# Test 1: No flags (no REM)
Write-Host ""
Write-Host "TEST 1: User awake (no flags)" -ForegroundColor Green
$testData.sensor_data.mpu.sleep_flag = $false
$testData.sensor_data.emg.atonia_flag = $false
$testData.timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")

try {
    $response = Invoke-RestMethod -Uri $dataUrl -Method POST -Body ($testData | ConvertTo-Json -Depth 10) -ContentType "application/json"
    Write-Host "OK: Response: REM=$($response.rem_detected), samples=$($response.total_hr_history)" -ForegroundColor White
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "INFO: Make sure Flask server is running: python run.py" -ForegroundColor Yellow
    exit 1
}

Start-Sleep 2

# Test 2: Sleep without atonia
Write-Host ""
Write-Host "TEST 2: Sleep without muscle atonia" -ForegroundColor Green
$testData.sensor_data.mpu.sleep_flag = $true
$testData.sensor_data.emg.atonia_flag = $false
$testData.timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")

try {
    $response = Invoke-RestMethod -Uri $dataUrl -Method POST -Body ($testData | ConvertTo-Json -Depth 10) -ContentType "application/json"
    Write-Host "OK: Response: REM=$($response.rem_detected), samples=$($response.total_hr_history)" -ForegroundColor White
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

Start-Sleep 2

# Test 3: Build history - send more data to reach 15 minutes
Write-Host ""
Write-Host "TEST 3: Building HR history (simulate 15 minutes)" -ForegroundColor Green
$testData.sensor_data.mpu.sleep_flag = $true
$testData.sensor_data.emg.atonia_flag = $true

for ($i = 1; $i -le 30; $i++) {
    Write-Host "Sending packet $i/30..." -NoNewline
    
    # Update timestamp
    $testData.timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
    
    try {
        $response = Invoke-RestMethod -Uri $dataUrl -Method POST -Body ($testData | ConvertTo-Json -Depth 10) -ContentType "application/json"
        Write-Host " OK samples: $($response.total_hr_history)" -ForegroundColor Green
    } catch {
        Write-Host " ERROR" -ForegroundColor Red
    }
    
    Start-Sleep 1
}

# Test 4: Increase HR and test REM
Write-Host ""
Write-Host "TEST 4: HR INCREASE -> TEST REM!" -ForegroundColor Magenta

# Increase all HR values by 8 BPM
foreach ($sample in $testData.sensor_data.plethysmometer) {
    $sample.heart_rate += 8
}

$testData.timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")

try {
    $response = Invoke-RestMethod -Uri $dataUrl -Method POST -Body ($testData | ConvertTo-Json -Depth 10) -ContentType "application/json"
    Write-Host "FINAL RESULT: REM=$($response.rem_detected)" -ForegroundColor $(if ($response.rem_detected) { "Green" } else { "Red" })
    Write-Host "HR Samples: $($response.total_hr_history)" -ForegroundColor White
    Write-Host "Sleep: $($response.flags.sleep)" -ForegroundColor White
    Write-Host "Atonia: $($response.flags.atonia)" -ForegroundColor White
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

# Check final status
Write-Host ""
Write-Host "=== CHECKING STATUS ===" -ForegroundColor Cyan

try {
    $status = Invoke-RestMethod -Uri $statusUrl -Method GET
    Write-Host "REM detected: $($status.rem_detected)" -ForegroundColor $(if ($status.rem_detected) { "Green" } else { "Red" })
    Write-Host "Sleep active: $($status.sleep_detected)" -ForegroundColor White
    Write-Host "Atonia active: $($status.atonia_detected)" -ForegroundColor White
    Write-Host "Total HR samples: $($status.hr_stats.total_samples)" -ForegroundColor White
    Write-Host "Average HR: $([math]::Round($status.hr_stats.avg_hr_all, 1)) BPM" -ForegroundColor White
    Write-Host "Last update: $($status.last_update)" -ForegroundColor Gray
} catch {
    Write-Host "ERROR: Could not get status: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Test completed!" -ForegroundColor Cyan