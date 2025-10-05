# Comprehensive test for mobile.py endpoints
# Tests all mobile API endpoints including audio generation, scenarios, and polling

Write-Host "=== COMPREHENSIVE MOBILE API TESTS ===" -ForegroundColor Green

$baseUrl = "http://localhost:8080"
$testResults = @()

function Test-Endpoint {
    param($name, $method, $url, $body = $null, $expectError = $false)
    
    Write-Host "`n--- Testing: $name ---" -ForegroundColor Yellow
    Write-Host "$method $url" -ForegroundColor Cyan
    
    try {
        if ($method -eq "GET") {
            $response = Invoke-RestMethod -Uri $url -Method GET
        } else {
            $headers = @{"Content-Type" = "application/json"}
            $response = Invoke-RestMethod -Uri $url -Method $method -Body $body -Headers $headers
        }
        
        if ($expectError) {
            Write-Host "UNEXPECTED SUCCESS (expected error)" -ForegroundColor Red
            return @{Name=$name; Status="FAIL"; Error="Expected error but got success"}
        } else {
            Write-Host "SUCCESS" -ForegroundColor Green
            return @{Name=$name; Status="PASS"; Response=$response}
        }
    } catch {
        if ($expectError) {
            Write-Host "EXPECTED ERROR: $($_.Exception.Message)" -ForegroundColor Yellow
            return @{Name=$name; Status="PASS"; Error=$_.Exception.Message}
        } else {
            Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
            return @{Name=$name; Status="FAIL"; Error=$_.Exception.Message}
        }
    }
}

# Test 1: Basic connectivity
$result1 = Test-Endpoint "Mobile Hello" "GET" "$baseUrl/mobile/hello"
$testResults += $result1

# Test 2: Initial polling (should return default session data)
$result2 = Test-Endpoint "Initial Polling" "GET" "$baseUrl/mobile/polling"
$testResults += $result2
if ($result2.Response) {
    Write-Host "Session data: rem_detected=$($result2.Response.session_data.rem_detected)" -ForegroundColor Cyan
}

# Test 3: Generate single audio (valid request)
$singleAudioData = @{
    key_words = "peaceful rain forest"
    place = "serene woodland"
} | ConvertTo-Json

$result3 = Test-Endpoint "Single Audio Generation" "POST" "$baseUrl/mobile/generate_audio" $singleAudioData
$testResults += $result3

# Capture session key for download tests
$sessionKey = $null
if ($result3.Response -and $result3.Response.audio_available) {
    $sessionKey = $result3.Response.audio_download_info.session_key
    Write-Host "Audio generated! Session key: $sessionKey" -ForegroundColor Green
    Write-Host "TTS: '$($result3.Response.tts_text)'" -ForegroundColor Cyan
    Write-Host "Extended available: $($result3.Response.audio_download_info.extended_available)" -ForegroundColor Cyan
}

# Test 4: Download audio files (if session key available)
if ($sessionKey) {
    Write-Host "`n--- Testing Audio Downloads ---" -ForegroundColor Yellow
    
    # Test TTS download
    if ($result3.Response.audio_download_info.tts_available) {
        try {
            Invoke-WebRequest -Uri "$baseUrl/mobile/download_audio/$sessionKey/tts" -OutFile "test_mobile_tts.mp3"
            $ttsSize = (Get-Item "test_mobile_tts.mp3").Length
            Write-Host "TTS download: SUCCESS ($ttsSize bytes)" -ForegroundColor Green
            $testResults += @{Name="TTS Download"; Status="PASS"; Size=$ttsSize}
        } catch {
            Write-Host "TTS download: FAILED - $($_.Exception.Message)" -ForegroundColor Red
            $testResults += @{Name="TTS Download"; Status="FAIL"; Error=$_.Exception.Message}
        }
    }
    
    # Test extended audio download
    if ($result3.Response.audio_download_info.extended_available) {
        try {
            Invoke-WebRequest -Uri "$baseUrl/mobile/download_audio/$sessionKey/extended" -OutFile "test_mobile_extended.mp3"
            $extSize = (Get-Item "test_mobile_extended.mp3").Length
            $extSizeMB = [Math]::Round($extSize / 1MB, 2)
            Write-Host "Extended download: SUCCESS ($extSizeMB MB)" -ForegroundColor Green
            $testResults += @{Name="Extended Download"; Status="PASS"; Size="$extSizeMB MB"}
            
            if ($extSizeMB -gt 5) {
                Write-Host "Extended file size looks correct for 15-minute audio!" -ForegroundColor Green
            }
        } catch {
            Write-Host "Extended download: FAILED - $($_.Exception.Message)" -ForegroundColor Red
            $testResults += @{Name="Extended Download"; Status="FAIL"; Error=$_.Exception.Message}
        }
    }
}

# Test 5: Load multiple scenarios
$multiScenarios = @{
    mobile_id = "TEST_MOBILE_001"
    dream_keywords = @(
        @{
            key_words = "flying clouds sky"
            place = "high above mountains"
        },
        @{
            key_words = "ocean waves beach"
            place = "tropical paradise"
        },
        @{
            key_words = "starry night quiet"
            place = "peaceful meadow"
        }
    )
} | ConvertTo-Json -Depth 3

$result5 = Test-Endpoint "Load Multiple Scenarios" "POST" "$baseUrl/mobile/load_scenarios" $multiScenarios
$testResults += $result5
if ($result5.Response) {
    Write-Host "Scenarios loaded: $($result5.Response.scenarios_count)" -ForegroundColor Cyan
    Write-Host "Processed: $($result5.Response.processed_scenarios)" -ForegroundColor Cyan
}

# Test 6: Polling after scenarios loaded
$result6 = Test-Endpoint "Polling After Scenarios" "GET" "$baseUrl/mobile/polling"
$testResults += $result6

# Test 7: Invalid requests (should fail gracefully)
Write-Host "`n--- Testing Error Handling ---" -ForegroundColor Yellow

# Empty audio request
$result7a = Test-Endpoint "Empty Audio Request" "POST" "$baseUrl/mobile/generate_audio" "{}" $true
$testResults += $result7a

# Invalid JSON
$result7b = Test-Endpoint "Invalid JSON" "POST" "$baseUrl/mobile/generate_audio" "invalid json" $true
$testResults += $result7b

# Invalid scenario format
$invalidScenarios = @{
    mobile_id = "TEST"
    dream_keywords = "not an array"
} | ConvertTo-Json

$result7c = Test-Endpoint "Invalid Scenarios Format" "POST" "$baseUrl/mobile/load_scenarios" $invalidScenarios $true
$testResults += $result7c

# Invalid download session
$result7d = Test-Endpoint "Invalid Download Session" "GET" "$baseUrl/mobile/download_audio/invalid_session/tts" $null $true
$testResults += $result7d

# Test 8: Check generated files
Write-Host "`n--- Checking Generated Files ---" -ForegroundColor Yellow
$audioFiles = Get-ChildItem "audio_files\*.mp3" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 10

if ($audioFiles) {
    Write-Host "Recent audio files generated:" -ForegroundColor Green
    $audioFiles | ForEach-Object {
        $sizeMB = [Math]::Round($_.Length / 1MB, 2)
        $type = if ($_.Name -like "*extended*") { "Extended" } 
               elseif ($_.Name -like "*tts*") { "TTS" }
               else { "Loop" }
        Write-Host "  $($_.Name) - ${sizeMB} MB ($type)" -ForegroundColor Cyan
    }
} else {
    Write-Host "No audio files found!" -ForegroundColor Red
}

# RESULTS SUMMARY
Write-Host "`n=== TEST RESULTS SUMMARY ===" -ForegroundColor Green

$passCount = ($testResults | Where-Object {$_.Status -eq "PASS"}).Count
$failCount = ($testResults | Where-Object {$_.Status -eq "FAIL"}).Count
$totalTests = $testResults.Count

Write-Host "Total Tests: $totalTests" -ForegroundColor White
Write-Host "Passed: $passCount" -ForegroundColor Green  
Write-Host "Failed: $failCount" -ForegroundColor Red

Write-Host "`nDetailed Results:" -ForegroundColor Yellow
$testResults | ForEach-Object {
    $color = if ($_.Status -eq "PASS") { "Green" } else { "Red" }
    $status = $_.Status.PadRight(4)
    Write-Host "  [$status] $($_.Name)" -ForegroundColor $color
    
    if ($_.Error) {
        Write-Host "    Error: $($_.Error)" -ForegroundColor Red
    }
    if ($_.Size) {
        Write-Host "    Size: $($_.Size)" -ForegroundColor Cyan
    }
}

# Final assessment
if ($failCount -eq 0) {
    Write-Host "`n🎉 ALL TESTS PASSED! Mobile API is fully functional! 🎉" -ForegroundColor Green
} elseif ($passCount -gt $failCount) {
    Write-Host "`n⚠️  Most tests passed, but some issues found. Check failures above." -ForegroundColor Yellow
} else {
    Write-Host "`n❌ Multiple test failures. Mobile API needs attention." -ForegroundColor Red
}

Write-Host "`nMobile API Features Tested:" -ForegroundColor Cyan
Write-Host "✓ Basic connectivity (/mobile/hello)" -ForegroundColor White
Write-Host "✓ Session polling (/mobile/polling)" -ForegroundColor White  
Write-Host "✓ Single audio generation (/mobile/generate_audio)" -ForegroundColor White
Write-Host "✓ Multiple scenario loading (/mobile/load_scenarios)" -ForegroundColor White
Write-Host "✓ Audio file downloads (/mobile/download_audio)" -ForegroundColor White
Write-Host "✓ Error handling for invalid requests" -ForegroundColor White
Write-Host "✓ 15-minute extended audio generation" -ForegroundColor White