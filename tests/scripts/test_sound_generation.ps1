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
            Write-Host "Downloading background sound (30s loop)..."
            try {
                Invoke-WebRequest -Uri "$baseUrl/mobile/download_audio/$sessionKey/sound" -OutFile "test_sound.mp3"
                Write-Host "✓ Background sound downloaded successfully!" -ForegroundColor Green
            } catch {
                Write-Host "✗ Sound download failed: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
        
        if ($response1.audio_download_info.extended_available) {
            Write-Host "Downloading extended 15-minute audio..."
            try {
                Invoke-WebRequest -Uri "$baseUrl/mobile/download_audio/$sessionKey/extended" -OutFile "test_extended.mp3"
                Write-Host "✓ Extended 15-minute audio downloaded successfully!" -ForegroundColor Green
                
                # Check file size to verify it's actually 15 minutes
                $fileSize = (Get-Item "test_extended.mp3").Length
                $fileSizeMB = [Math]::Round($fileSize / 1MB, 2)
                Write-Host "Extended file size: $fileSizeMB MB" -ForegroundColor Cyan
                
                if ($fileSizeMB -gt 10) {
                    Write-Host "✓ File size indicates ~15 minutes of audio!" -ForegroundColor Green
                } else {
                    Write-Host "⚠ File size seems small for 15-minute audio" -ForegroundColor Yellow
                }
            } catch {
                Write-Host "✗ Extended audio download failed: $($_.Exception.Message)" -ForegroundColor Red
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

Write-Host "`n4. Testing extended audio functionality specifically..." -ForegroundColor Yellow

# Test specific dream scenario optimized for extended audio
$extendedTestScenario = @{
    key_words = "gentle rain forest birds peaceful meditation"
    place = "quiet forest clearing surrounded by ancient trees"
} | ConvertTo-Json

try {
    Write-Host "Generating scenario optimized for 15-minute meditation audio..."
    $extendedResponse = Invoke-RestMethod -Uri "$baseUrl/mobile/generate_audio" -Method POST -Body $extendedTestScenario -ContentType "application/json"
    
    Write-Host "✓ Extended audio scenario generated!" -ForegroundColor Green
    Write-Host "TTS Text: $($extendedResponse.tts_text)" -ForegroundColor Cyan
    Write-Host "Sound Description: $($extendedResponse.sound_description)" -ForegroundColor Cyan
    
    if ($extendedResponse.audio_available) {
        Write-Host "`nAudio file info:" -ForegroundColor Yellow
        Write-Host "  - TTS Available: $($extendedResponse.audio_download_info.tts_available)" -ForegroundColor Cyan
        Write-Host "  - 30s Loop Available: $($extendedResponse.audio_download_info.sound_available)" -ForegroundColor Cyan
        Write-Host "  - 15min Extended Available: $($extendedResponse.audio_download_info.extended_available)" -ForegroundColor Cyan
        
        if ($extendedResponse.audio_download_info.extended_available) {
            Write-Host "`n🎵 Ready for lucid dreaming with 15-minute extended audio!" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "✗ Extended audio test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Green
Write-Host "Note: If API keys are not configured, audio generation will return text-only responses." -ForegroundColor Yellow
Write-Host "The extended audio feature creates:" -ForegroundColor Cyan
Write-Host "  🔸 30-second looped background sounds" -ForegroundColor White
Write-Host "  🔸 15-minute extended version with fade-in/out" -ForegroundColor White  
Write-Host "  🔸 TTS mixed after 10-second fade-in" -ForegroundColor White