# Test script for sound generation functionality
# This script tests the new API endpoints for dream scenario processing

Write-Host "=== Testing Dream Sound Generation API ===" -ForegroundColor Green

# Base URL - adjust if running on different port
$baseUrl = "http://localhost:8080"

# Test data - single scenario
$singleScenario = @{
    key_words = "flying airplane clouds sky"
    place = "high above mountains"
} | ConvertTo-Json

# Test data - multiple scenarios (from mobile_scenarios.json format)
$multipleScenarios = @{
    mobile_id = "TEST_001"
    dream_keywords = @(
        @{
            key_words = "flying airplane clouds sky"
            place = "high above mountains"
        },
        @{
            key_words = "ocean waves swimming dolphins"
            place = "deep blue sea"
        }
    )
} | ConvertTo-Json -Depth 3

Write-Host "`n1. Testing single scenario audio generation..." -ForegroundColor Yellow
Write-Host "POST $baseUrl/mobile/generate_audio"

try {
    $response1 = Invoke-RestMethod -Uri "$baseUrl/mobile/generate_audio" -Method POST -Body $singleScenario -ContentType "application/json"
    Write-Host "✓ Single scenario test successful!" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor Cyan
    $response1 | ConvertTo-Json -Depth 5 | Write-Host
    
    # If audio is available, test download endpoints
    if ($response1.audio_available -eq $true) {
        Write-Host "`nTesting audio download..." -ForegroundColor Yellow
        $sessionKey = $response1.audio_download_info.session_key
        
        if ($response1.audio_download_info.tts_available) {
            Write-Host "Downloading TTS audio..."
            try {
                Invoke-WebRequest -Uri "$baseUrl/mobile/download_audio/$sessionKey/tts" -OutFile "test_tts.mp3"
                Write-Host "✓ TTS audio downloaded successfully!" -ForegroundColor Green
            } catch {
                Write-Host "✗ TTS download failed: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
        
        if ($response1.audio_download_info.sound_available) {
            Write-Host "Downloading background sound..."
            try {
                Invoke-WebRequest -Uri "$baseUrl/mobile/download_audio/$sessionKey/sound" -OutFile "test_sound.mp3"
                Write-Host "✓ Background sound downloaded successfully!" -ForegroundColor Green
            } catch {
                Write-Host "✗ Sound download failed: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }
} catch {
    Write-Host "✗ Single scenario test failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Response body: $($_.ErrorDetails.Message)" -ForegroundColor Red
}

Write-Host "`n2. Testing multiple scenarios loading..." -ForegroundColor Yellow
Write-Host "POST $baseUrl/mobile/load_scenarios"

try {
    $response2 = Invoke-RestMethod -Uri "$baseUrl/mobile/load_scenarios" -Method POST -Body $multipleScenarios -ContentType "application/json"
    Write-Host "✓ Multiple scenarios test successful!" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor Cyan
    $response2 | ConvertTo-Json -Depth 5 | Write-Host
} catch {
    Write-Host "✗ Multiple scenarios test failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Response body: $($_.ErrorDetails.Message)" -ForegroundColor Red
}

Write-Host "`n3. Testing mobile polling (should show session data)..." -ForegroundColor Yellow
Write-Host "GET $baseUrl/mobile/polling"

try {
    $response3 = Invoke-RestMethod -Uri "$baseUrl/mobile/polling" -Method GET
    Write-Host "✓ Mobile polling test successful!" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor Cyan
    $response3 | ConvertTo-Json -Depth 5 | Write-Host
} catch {
    Write-Host "✗ Mobile polling test failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Response body: $($_.ErrorDetails.Message)" -ForegroundColor Red
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Green
Write-Host "Note: If API keys are not configured, audio generation will return text-only responses." -ForegroundColor Yellow