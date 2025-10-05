param(
    [string]$linkPart,
    [string]$httpMethod,
    [string]$jsonFile = ""
)

# Buduj URL z stałym hostem i portem 8080
$url = "http://localhost:8080" + $linkPart

Write-Host "=== Mock API Tester ===" -ForegroundColor Green
Write-Host "URL: $url" -ForegroundColor Cyan
Write-Host "Method: $httpMethod" -ForegroundColor Cyan

if ($httpMethod -ieq "GET") {
    # Dla GET wysyłamy żądanie bez ciała
    Write-Host "Sending GET request..." -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri $url -Method GET
        $statusCode = 200  # Invoke-RestMethod sukces oznacza 200-299
    }
    catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
} else {
    if ($jsonFile -ne "") {
        # Jeśli podano plik JSON, wczytaj dane
        Write-Host "Loading JSON from file: $jsonFile" -ForegroundColor Yellow
        
        if (-not (Test-Path $jsonFile)) {
            Write-Host "ERROR: File $jsonFile not found!" -ForegroundColor Red
            exit 1
        }
        
        try {
            $data = Get-Content -Path "./$jsonFile" -Raw | ConvertFrom-Json
            $body = $data | ConvertTo-Json -Depth 10 -Compress
            $bodySize = $body.Length
            Write-Host "JSON loaded successfully, size: $bodySize characters" -ForegroundColor Green
        }
        catch {
            Write-Host "ERROR: Invalid JSON in file $jsonFile - $($_.Exception.Message)" -ForegroundColor Red
            exit 1
        }
    } else {
        # Jeśli nie podano pliku, użyj pustego ciała
        $body = ""
        Write-Host "Sending request with empty body..." -ForegroundColor Yellow
    }
    
    try {
        Write-Host "Sending $httpMethod request..." -ForegroundColor Yellow
        $response = Invoke-RestMethod -Uri $url -Method $httpMethod -Headers @{ "Content-Type" = "application/json" } -Body $body
        $statusCode = 200  # Invoke-RestMethod sukces oznacza 200-299
    }
    catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            Write-Host "Status Code: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
        }
        exit 1
    }
}

Write-Host ""
Write-Host "=== RESPONSE ===" -ForegroundColor Green
Write-Host "Status: SUCCESS (2xx)" -ForegroundColor Green

# Sprawdź czy response to obiekt czy string
if ($response -is [PSCustomObject] -or $response -is [hashtable]) {
    Write-Host ""
    Write-Host "Response JSON:" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 10 | Write-Host
    
    Write-Host ""
    Write-Host "Response Details:" -ForegroundColor Cyan
    $response | Format-List *
} else {
    Write-Host ""
    Write-Host "Response Text:" -ForegroundColor Cyan
    Write-Host $response
}

Write-Host ""
Write-Host "SUCCESS: Request completed successfully!" -ForegroundColor Green
