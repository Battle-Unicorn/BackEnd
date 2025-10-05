# Test script specifically for 15-minute extended audio functionality
# Tests the new pydub-based audio processing with fade-in/out and TTS mixing

Write-Host "=== Testing 15-Minute Extended Audio Generation ===" -ForegroundColor Green

# Base URL
$baseUrl = "http://localhost:8080"

# Test scenarios optimized for extended meditation audio
$testScenarios = @(
    @{
        name = "Forest Meditation"
        key_words = "gentle rain forest birds peaceful meditation leaves rustling"
        place = "quiet forest clearing surrounded by ancient oak trees"
    },
    @{
        name = "Ocean Dreams"
        key_words = "ocean waves seagulls sand warm breeze peaceful"
        place = "secluded beach at sunset with gentle waves"
    },
    @{
        name = "Mountain Serenity"
        key_words = "wind mountain echo silence stars crisp air"
        place = "high mountain peak under starry sky"
    }
)

foreach ($scenario in $testScenarios) {
    Write-Host "`n=== Testing: $($scenario.name) ===" -ForegroundColor Yellow
    
    $requestData = @{
        key_words = $scenario.key_words
        place = $scenario.place
    } | ConvertTo-Json
    
    Write-Host "Generating extended audio..." -ForegroundColor Cyan
    Write-Host "Keywords: $($scenario.key_words)" -ForegroundColor White
    Write-Host "Place: $($scenario.place)" -ForegroundColor White
    
    try {
        # Generate audio
        $response = Invoke-RestMethod -Uri "$baseUrl/mobile/generate_audio" -Method POST -Body $requestData -ContentType "application/json"
        
        Write-Host "✓ Audio generation successful!" -ForegroundColor Green
        Write-Host "TTS Text: $($response.tts_text)" -ForegroundColor Cyan
        Write-Host "Sound Description: $($response.sound_description)" -ForegroundColor Cyan
        
        if ($response.audio_available) {
            $sessionKey = $response.audio_download_info.session_key
            
            Write-Host "`nAudio Files Available:" -ForegroundColor Yellow
            Write-Host "  🔸 TTS (Voice): $($response.audio_download_info.tts_available)" -ForegroundColor White
            Write-Host "  🔸 30s Loop: $($response.audio_download_info.sound_available)" -ForegroundColor White
            Write-Host "  🔸 15min Extended: $($response.audio_download_info.extended_available)" -ForegroundColor White
            
            # Test downloading extended audio
            if ($response.audio_download_info.extended_available) {
                Write-Host "`nDownloading 15-minute extended audio..." -ForegroundColor Cyan
                
                $scenarioName = $scenario.name -replace ' ', '_'
                $filename = "extended_${scenarioName}.mp3"
                
                try {
                    $downloadStart = Get-Date
                    Invoke-WebRequest -Uri "$baseUrl/mobile/download_audio/$sessionKey/extended" -OutFile $filename
                    $downloadTime = (Get-Date) - $downloadStart
                    
                    # Check file properties
                    $fileInfo = Get-Item $filename
                    $fileSizeMB = [Math]::Round($fileInfo.Length / 1MB, 2)
                    
                    Write-Host "✓ Extended audio downloaded successfully!" -ForegroundColor Green
                    Write-Host "  📁 File: $filename" -ForegroundColor Cyan
                    Write-Host "  📏 Size: $fileSizeMB MB" -ForegroundColor Cyan
                    Write-Host "  ⏱️ Download time: $($downloadTime.TotalSeconds.ToString('F1'))s" -ForegroundColor Cyan
                    
                    # Validate file size (15 minutes of 128kbps MP3 ≈ 14-16MB)
                    if ($fileSizeMB -gt 10 -and $fileSizeMB -lt 25) {
                        Write-Host "  ✓ File size indicates ~15 minutes of audio!" -ForegroundColor Green
                    } elseif ($fileSizeMB -lt 1) {
                        Write-Host "  ⚠️ File suspiciously small - may be fallback repetition" -ForegroundColor Yellow
                    } else {
                        Write-Host "  ⚠️ Unexpected file size for 15-minute audio" -ForegroundColor Yellow
                    }
                    
                } catch {
                    Write-Host "✗ Failed to download extended audio: $($_.Exception.Message)" -ForegroundColor Red
                }
            } else {
                Write-Host "⚠️ Extended audio not available" -ForegroundColor Yellow
            }
            
            # Also test downloading individual components for comparison
            if ($response.audio_download_info.tts_available) {
                Write-Host "`nDownloading TTS component..." -ForegroundColor Cyan
                try {
                    $ttsFilename = "tts_${scenarioName}.mp3"
                    Invoke-WebRequest -Uri "$baseUrl/mobile/download_audio/$sessionKey/tts" -OutFile $ttsFilename
                    $ttsSize = [Math]::Round((Get-Item $ttsFilename).Length / 1KB, 1)
                    Write-Host "  ✓ TTS downloaded: ${ttsFilename} (${ttsSize} KB)" -ForegroundColor Green
                } catch {
                    Write-Host "  ✗ TTS download failed: $($_.Exception.Message)" -ForegroundColor Red
                }
            }
            
            if ($response.audio_download_info.sound_available) {
                Write-Host "Downloading 30s loop component..." -ForegroundColor Cyan
                try {
                    $loopFilename = "loop_${scenarioName}.mp3"
                    Invoke-WebRequest -Uri "$baseUrl/mobile/download_audio/$sessionKey/sound" -OutFile $loopFilename
                    $loopSize = [Math]::Round((Get-Item $loopFilename).Length / 1KB, 1)
                    Write-Host "  ✓ 30s loop downloaded: ${loopFilename} (${loopSize} KB)" -ForegroundColor Green
                } catch {
                    Write-Host "  ✗ Loop download failed: $($_.Exception.Message)" -ForegroundColor Red
                }
            }
            
        } else {
            Write-Host "⚠️ Audio not available (likely missing API keys)" -ForegroundColor Yellow
            Write-Host "Message: $($response.message)" -ForegroundColor White
        }
        
    } catch {
        Write-Host "✗ Test failed for $($scenario.name): $($_.Exception.Message)" -ForegroundColor Red
        if ($_.ErrorDetails.Message) {
            Write-Host "Error details: $($_.ErrorDetails.Message)" -ForegroundColor Red
        }
    }
}

Write-Host "`n=== Extended Audio Test Summary ===" -ForegroundColor Green
Write-Host "The extended audio feature provides:" -ForegroundColor Cyan
Write-Host "  🎵 15-minute seamless audio for lucid dreaming sessions" -ForegroundColor White
Write-Host "  🔄 30-second background loop repeated 30 times" -ForegroundColor White
Write-Host "  📈 10-second fade-in at the beginning" -ForegroundColor White
Write-Host "  🎙️ TTS mixed in after fade-in completes" -ForegroundColor White
Write-Host "  📉 5-second fade-out at the end" -ForegroundColor White
Write-Host "  🔊 Professional audio mixing without clipping" -ForegroundColor White

Write-Host "`nFiles generated in current directory:" -ForegroundColor Yellow
Get-ChildItem "*.mp3" -ErrorAction SilentlyContinue | ForEach-Object {
    $sizeMB = [Math]::Round($_.Length / 1MB, 2)
    Write-Host "  📁 $($_.Name) - ${sizeMB} MB" -ForegroundColor Cyan
}

Write-Host "`n✨ Extended Audio Test Complete! ✨" -ForegroundColor Green