# Szybki test API
Write-Host "🧪 Testing Sound Generation API..." -ForegroundColor Green

# Test 1: Single scenario
Write-Host "`n1️⃣ Testing single scenario..." -ForegroundColor Yellow
$singleTest = @{
    key_words = "ocean waves dolphins"
    place = "crystal blue lagoon"
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "http://localhost:8080/mobile/generate_audio" -Method POST -Body $singleTest -ContentType "application/json"
    Write-Host "✅ SUCCESS!" -ForegroundColor Green
    Write-Host "TTS Text: $($result.tts_text)" -ForegroundColor Cyan
    Write-Host "Sound Description: $($result.sound_description)" -ForegroundColor Cyan
    Write-Host "Audio Available: $($result.audio_available)" -ForegroundColor Yellow
} catch {
    Write-Host "❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Multiple scenarios from file
Write-Host "`n2️⃣ Testing multiple scenarios from file..." -ForegroundColor Yellow
try {
    $jsonContent = Get-Content "Mock_Scripts/mobile_scenarios.json" -Raw
    $result2 = Invoke-RestMethod -Uri "http://localhost:8080/mobile/load_scenarios" -Method POST -Body $jsonContent -ContentType "application/json"
    Write-Host "✅ SUCCESS!" -ForegroundColor Green
    Write-Host "Processed $($result2.processed_scenarios) scenarios" -ForegroundColor Cyan
    Write-Host "Generated audio for $($result2.generated_audio.Count) scenarios" -ForegroundColor Cyan
} catch {
    Write-Host "❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n✨ Test complete!" -ForegroundColor Green