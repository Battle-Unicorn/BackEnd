# Mobile API Comprehensive Test
Write-Host "=== MOBILE API TESTS ===" -ForegroundColor Green

$baseUrl = "http://localhost:8080"
$results = @()

# Test 1: Hello endpoint
Write-Host "`nTest 1: Mobile Hello" -ForegroundColor Yellow
try {
    $hello = Invoke-RestMethod -Uri "$baseUrl/mobile/hello" -Method GET
    Write-Host "SUCCESS: $hello" -ForegroundColor Green
    $results += "PASS: Hello endpoint"
} catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
    $results += "FAIL: Hello endpoint"
}

# Test 2: Initial polling
Write-Host "`nTest 2: Initial Polling" -ForegroundColor Yellow
try {
    $polling = Invoke-RestMethod -Uri "$baseUrl/mobile/polling" -Method GET
    Write-Host "SUCCESS: REM detected = $($polling.session_data.rem_detected)" -ForegroundColor Green
    $results += "PASS: Polling endpoint"
} catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
    $results += "FAIL: Polling endpoint"
}

# Test 3: Generate audio
Write-Host "`nTest 3: Generate Audio" -ForegroundColor Yellow
$audioRequest = @{
    key_words = "peaceful mountain wind"
    place = "high alpine meadow"
} | ConvertTo-Json

try {
    $audioResult = Invoke-RestMethod -Uri "$baseUrl/mobile/generate_audio" -Method POST -Body $audioRequest -ContentType "application/json"
    
    if ($audioResult.audio_available) {
        Write-Host "SUCCESS: Audio generated!" -ForegroundColor Green
        Write-Host "  TTS: $($audioResult.tts_text)" -ForegroundColor Cyan
        Write-Host "  Extended available: $($audioResult.audio_download_info.extended_available)" -ForegroundColor Cyan
        $sessionKey = $audioResult.audio_download_info.session_key
        $results += "PASS: Audio generation"
        
        # Test download extended audio
        Write-Host "`nTest 4: Download Extended Audio" -ForegroundColor Yellow
        try {
            Invoke-WebRequest -Uri "$baseUrl/mobile/download_audio/$sessionKey/extended" -OutFile "mobile_test_extended.mp3"
            $fileSize = (Get-Item "mobile_test_extended.mp3").Length / 1MB
            Write-Host "SUCCESS: Downloaded $([Math]::Round($fileSize, 2)) MB" -ForegroundColor Green
            $results += "PASS: Extended audio download"
        } catch {
            Write-Host "FAIL: Download failed - $($_.Exception.Message)" -ForegroundColor Red
            $results += "FAIL: Extended audio download"
        }
        
    } else {
        Write-Host "INFO: Audio not available (API keys missing)" -ForegroundColor Yellow
        $results += "SKIP: Audio generation (no API keys)"
    }
} catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
    $results += "FAIL: Audio generation"
}

# Test 5: Load scenarios
Write-Host "`nTest 5: Load Multiple Scenarios" -ForegroundColor Yellow
$scenarios = @{
    mobile_id = "TEST_001"
    dream_keywords = @(
        @{ key_words = "forest birds"; place = "quiet woods" },
        @{ key_words = "ocean waves"; place = "sandy beach" }
    )
} | ConvertTo-Json -Depth 3

try {
    $scenarioResult = Invoke-RestMethod -Uri "$baseUrl/mobile/load_scenarios" -Method POST -Body $scenarios -ContentType "application/json"
    Write-Host "SUCCESS: Loaded $($scenarioResult.scenarios_count) scenarios" -ForegroundColor Green
    Write-Host "  Processed: $($scenarioResult.processed_scenarios)" -ForegroundColor Cyan
    $results += "PASS: Multiple scenarios"
} catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
    $results += "FAIL: Multiple scenarios"
}

# Test 6: Error handling
Write-Host "`nTest 6: Error Handling" -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "$baseUrl/mobile/generate_audio" -Method POST -Body "{}" -ContentType "application/json"
    Write-Host "UNEXPECTED: Should have failed" -ForegroundColor Red
    $results += "FAIL: Error handling"
} catch {
    Write-Host "SUCCESS: Correctly rejected invalid request" -ForegroundColor Green
    $results += "PASS: Error handling"
}

# Results summary
Write-Host "`n=== RESULTS ===" -ForegroundColor Green
$passCount = ($results | Where-Object {$_ -like "PASS:*"}).Count
$failCount = ($results | Where-Object {$_ -like "FAIL:*"}).Count
$skipCount = ($results | Where-Object {$_ -like "SKIP:*"}).Count

Write-Host "Passed: $passCount" -ForegroundColor Green
Write-Host "Failed: $failCount" -ForegroundColor Red
Write-Host "Skipped: $skipCount" -ForegroundColor Yellow

Write-Host "`nDetailed Results:" -ForegroundColor Cyan
$results | ForEach-Object {
    if ($_ -like "PASS:*") { Write-Host "  $_" -ForegroundColor Green }
    elseif ($_ -like "FAIL:*") { Write-Host "  $_" -ForegroundColor Red }
    else { Write-Host "  $_" -ForegroundColor Yellow }
}

if ($failCount -eq 0) {
    Write-Host "`nMOBILE API IS FULLY FUNCTIONAL!" -ForegroundColor Green
} else {
    Write-Host "`nSome issues found - check failures above" -ForegroundColor Yellow
}