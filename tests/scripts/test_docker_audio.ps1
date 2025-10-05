# Test Docker audio generation
Write-Host "DOCKER: Testing Docker Audio Generation..." -ForegroundColor Green

# Wait for container to be ready
Write-Host "Waiting for container to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test connection
Write-Host "`nTesting connection..." -ForegroundColor Yellow
try {
    $healthCheck = Invoke-RestMethod -Uri "http://localhost:8080/mobile/hello" -Method GET
    Write-Host "SUCCESS: Container is responding!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Container not responding: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test audio generation
Write-Host "`nAUDIO: Testing audio generation..." -ForegroundColor Yellow
$testData = @{
    key_words = "docker container cloud technology"
    place = "digital datacenter"
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "http://localhost:8080/mobile/generate_audio" -Method POST -Body $testData -ContentType "application/json"
    Write-Host "SUCCESS: Audio generation successful!" -ForegroundColor Green
    Write-Host "TTS Text: $($result.tts_text)" -ForegroundColor Cyan
    Write-Host "Audio Available: $($result.audio_available)" -ForegroundColor Yellow
    
    if ($result.audio_available) {
        Write-Host "DOWNLOAD: Audio files can be downloaded from:" -ForegroundColor Green
        Write-Host "  TTS: $($result.audio_download_info.download_urls.tts)" -ForegroundColor Cyan
        Write-Host "  Sound: $($result.audio_download_info.download_urls.sound)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "ERROR: Audio generation failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nFILES: Checking audio files in container..." -ForegroundColor Yellow
try {
    # List files in audio_files directory from host
    $audioFiles = Get-ChildItem "audio_files\*.mp3" -ErrorAction SilentlyContinue
    if ($audioFiles) {
        Write-Host "SUCCESS: Audio files found on host:" -ForegroundColor Green
        $audioFiles | ForEach-Object { Write-Host "  $($_.Name)" -ForegroundColor Cyan }
    } else {
        Write-Host "WARNING: No audio files found in audio_files directory" -ForegroundColor Yellow
    }
} catch {
    Write-Host "ERROR: Error checking audio files: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nCOMPLETE: Docker audio test complete!" -ForegroundColor Green