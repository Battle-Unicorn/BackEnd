# Test skrypt do wysyłania scenariuszy mobilnych
# Wysyła dane z mobile_scenarios.json do endpointu /mobile/load_scenarios

param(
    [string]$ServerUrl = "http://localhost:5000",
    [string]$MobileId = "MOB_001",
    [string]$DeviceId = "DEV_001"
)

Write-Host "=== Test Mobile Scenarios ===" -ForegroundColor Green
Write-Host "Server: $ServerUrl" -ForegroundColor Cyan
Write-Host "Mobile ID: $MobileId" -ForegroundColor Cyan
Write-Host "Device ID: $DeviceId" -ForegroundColor Cyan
Write-Host ""

# Ścieżka do pliku ze scenariuszami
$scenariosFile = "..\..\tests\mock_data\mobile_scenarios.json"

# Sprawdź czy plik istnieje
if (-not (Test-Path $scenariosFile)) {
    Write-Host "ERROR: Nie znaleziono pliku $scenariosFile" -ForegroundColor Red
    exit 1
}

# Wczytaj dane ze scenariuszy
try {
    Write-Host "Wczytywanie scenariuszy z: $scenariosFile" -ForegroundColor Yellow
    $scenariosContent = Get-Content -Path $scenariosFile -Raw | ConvertFrom-Json
    Write-Host "Znaleziono $($scenariosContent.dream_keywords.Count) scenariuszy" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Błąd podczas wczytywania pliku JSON: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Dodaj device_id do danych jeśli podano
if ($DeviceId -ne "") {
    $scenariosContent | Add-Member -NotePropertyName "device_id" -NotePropertyValue $DeviceId -Force
}

# Aktualizuj mobile_id jeśli podano inny
if ($MobileId -ne $scenariosContent.mobile_id) {
    $scenariosContent.mobile_id = $MobileId
}

# Konwertuj z powrotem do JSON
$jsonBody = $scenariosContent | ConvertTo-Json -Depth 10

Write-Host "Przygotowane dane JSON:" -ForegroundColor Yellow
Write-Host $jsonBody -ForegroundColor Gray
Write-Host ""

# Wyślij request do /mobile/load_scenarios
$loadScenariosUrl = "$ServerUrl/mobile/load_scenarios"
Write-Host "Wysyłanie POST request do: $loadScenariosUrl" -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri $loadScenariosUrl -Method POST -Body $jsonBody -ContentType "application/json" -TimeoutSec 30
    
    Write-Host "SUCCESS: Scenariusze zostały załadowane pomyślnie!" -ForegroundColor Green
    Write-Host "Status: $($response.status)" -ForegroundColor Cyan
    Write-Host "Message: $($response.message)" -ForegroundColor Cyan
    Write-Host "Scenarios count: $($response.scenarios_count)" -ForegroundColor Cyan
    Write-Host "Processed scenarios: $($response.processed_scenarios)" -ForegroundColor Cyan
    
    if ($response.generated_audio -and $response.generated_audio.Count -gt 0) {
        Write-Host ""
        Write-Host "Wygenerowane audio dla scenariuszy:" -ForegroundColor Yellow
        foreach ($audioInfo in $response.generated_audio) {
            $status = $audioInfo.generation_result.status
            $statusColor = if ($status -eq "success") { "Green" } elseif ($status -eq "error") { "Red" } else { "Yellow" }
            
            Write-Host "  Scenariusz #$($audioInfo.scenario_index): $status" -ForegroundColor $statusColor
            Write-Host "    Keywords: $($audioInfo.key_words)" -ForegroundColor Gray
            Write-Host "    Place: $($audioInfo.place)" -ForegroundColor Gray
            
            if ($audioInfo.generation_result.audio_available) {
                Write-Host "    Audio dostępne: TTS=$($audioInfo.generation_result.audio_files_info.tts_file_available), Sound=$($audioInfo.generation_result.audio_files_info.sound_file_available)" -ForegroundColor Green
            } else {
                Write-Host "    Audio niedostępne" -ForegroundColor Red
            }
            
            if ($audioInfo.generation_result.error) {
                Write-Host "    Error: $($audioInfo.generation_result.error)" -ForegroundColor Red
            }
        }
    }
    
} catch {
    Write-Host "ERROR: Błąd podczas wysyłania requestu" -ForegroundColor Red
    Write-Host "Exception: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "HTTP Status Code: $statusCode" -ForegroundColor Red
        
        try {
            $errorResponse = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($errorResponse)
            $errorContent = $reader.ReadToEnd()
            Write-Host "Response Body: $errorContent" -ForegroundColor Red
        } catch {
            Write-Host "Nie można odczytać treści błędu" -ForegroundColor Red
        }
    }
    exit 1
}

Write-Host ""
Write-Host "=== Test zakończony ===" -ForegroundColor Green

# Opcjonalnie: test mobile/polling aby sprawdzić czy dane zostały załadowane
Write-Host ""
Write-Host "Sprawdzanie stanu przez /mobile/polling..." -ForegroundColor Yellow

try {
    $pollingUrl = "$ServerUrl/mobile/polling?mobile_id=$MobileId&detailed=true"
    $pollingResponse = Invoke-RestMethod -Uri $pollingUrl -Method GET -TimeoutSec 10
    
    Write-Host "Mobile polling response:" -ForegroundColor Green
    Write-Host "  Mobile ID: $($pollingResponse.mobile_session.mobile_id)" -ForegroundColor Cyan
    Write-Host "  Connected device: $($pollingResponse.mobile_session.connected_device)" -ForegroundColor Cyan
    Write-Host "  Scenarios loaded: $($pollingResponse.mobile_session.scenarios_loaded)" -ForegroundColor Cyan
    Write-Host "  REM detected: $($pollingResponse.session_data.rem_detected)" -ForegroundColor Cyan
    
} catch {
    Write-Host "WARNING: Nie można pobrać stanu przez polling: $($_.Exception.Message)" -ForegroundColor Yellow
}
