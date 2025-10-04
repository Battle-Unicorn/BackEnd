# Test REM Detection System - PowerShell
# Uruchom ten skrypt gdy serwer Flask juz dziala

Write-Host "=== TEST SYSTEMU DETEKCJI REM ===" -ForegroundColor Cyan

# Wczytujemy dane testowe
$jsonPath = "Mock_Scripts\data_embedded.json"
if (-not (Test-Path $jsonPath)) {
    Write-Host "ERROR: Nie znaleziono pliku $jsonPath" -ForegroundColor Red
    exit 1
}

$testData = Get-Content $jsonPath | ConvertFrom-Json

# URL endpointów
$dataUrl = "http://localhost:8080/embedded/data"
$statusUrl = "http://localhost:8080/embedded/rem_status"

Write-Host "Testowanie endpointow Flask..." -ForegroundColor Yellow

# Test 1: Dane bez flag (brak REM)
Write-Host "`nTEST 1: Uzytkownik czuwa (brak flag)" -ForegroundColor Green
$testData.sensor_data.mpu.sleep_flag = $false
$testData.sensor_data.emg.atonia_flag = $false
$testData.timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")

try {
    $response = Invoke-RestMethod -Uri $dataUrl -Method POST -Body ($testData | ConvertTo-Json -Depth 10) -ContentType "application/json"
    Write-Host "OK: Odpowiedz: REM=$($response.rem_detected), probek=$($response.total_hr_history)" -ForegroundColor White
} catch {
    Write-Host "ERROR: Blad: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "INFO: Upewnij sie ze serwer Flask jest uruchomiony: python run.py" -ForegroundColor Yellow
    exit 1
}

Start-Sleep 2

# Test 2: Sen bez atonii
Write-Host "`nTEST 2: Sen bez atonii miesni" -ForegroundColor Green
$testData.sensor_data.mpu.sleep_flag = $true
$testData.sensor_data.emg.atonia_flag = $false
$testData.timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")

try {
    $response = Invoke-RestMethod -Uri $dataUrl -Method POST -Body ($testData | ConvertTo-Json -Depth 10) -ContentType "application/json"
    Write-Host "OK: Odpowiedz: REM=$($response.rem_detected), probek=$($response.total_hr_history)" -ForegroundColor White
} catch {
    Write-Host "ERROR: Blad: $($_.Exception.Message)" -ForegroundColor Red
}

Start-Sleep 2

# Test 3: Budowanie historii - wysylamy wiecej danych zeby osiagnac 15 minut
Write-Host "`nTEST 3: Budowanie historii HR (symulacja 15 minut)" -ForegroundColor Green
$testData.sensor_data.mpu.sleep_flag = $true
$testData.sensor_data.emg.atonia_flag = $true

for ($i = 1; $i -le 30; $i++) {
    Write-Host "Wysylanie pakietu $i/30..." -NoNewline
    
    # Aktualizujemy timestamp
    $testData.timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
    
    try {
        $response = Invoke-RestMethod -Uri $dataUrl -Method POST -Body ($testData | ConvertTo-Json -Depth 10) -ContentType "application/json"
        Write-Host " OK probek: $($response.total_hr_history)" -ForegroundColor Green
    } catch {
        Write-Host " ERROR Blad" -ForegroundColor Red
    }
    
    Start-Sleep 1
}

# Test 4: Zwiekszamy HR i testujemy REM
Write-Host "`nTEST 4: WZROST HR -> TESTUJEMY REM!" -ForegroundColor Magenta

# Zwiekszamy wszystkie wartosci HR o 8 BPM
foreach ($sample in $testData.sensor_data.plethysmometer) {
    $sample.heart_rate += 8
}

$testData.timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")

try {
    $response = Invoke-RestMethod -Uri $dataUrl -Method POST -Body ($testData | ConvertTo-Json -Depth 10) -ContentType "application/json"
    Write-Host "WYNIK FINAL: REM=$($response.rem_detected)" -ForegroundColor $(if ($response.rem_detected) { "Green" } else { "Red" })
    Write-Host "Probek HR: $($response.total_hr_history)" -ForegroundColor White
    Write-Host "Sleep: $($response.flags.sleep)" -ForegroundColor White
    Write-Host "Atonia: $($response.flags.atonia)" -ForegroundColor White
} catch {
    Write-Host "ERROR: Blad: $($_.Exception.Message)" -ForegroundColor Red
}

# Sprawdzamy koncowy status
Write-Host "`n=== SPRAWDZANIE STATUSU ===" -ForegroundColor Cyan

try {
    $status = Invoke-RestMethod -Uri $statusUrl -Method GET
    Write-Host "REM wykryty: $($status.rem_detected)" -ForegroundColor $(if ($status.rem_detected) { "Green" } else { "Red" })
    Write-Host "Sleep aktywny: $($status.sleep_detected)" -ForegroundColor White
    Write-Host "Atonia aktywna: $($status.atonia_detected)" -ForegroundColor White
    Write-Host "Calkowite probki HR: $($status.hr_stats.total_samples)" -ForegroundColor White
    Write-Host "Sredni HR: $([math]::Round($status.hr_stats.avg_hr_all, 1)) BPM" -ForegroundColor White
    Write-Host "Ostatnia aktualizacja: $($status.last_update)" -ForegroundColor Gray
} catch {
    Write-Host "ERROR: Nie udalo sie pobrac statusu: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nTest zakonczony!" -ForegroundColor Cyan