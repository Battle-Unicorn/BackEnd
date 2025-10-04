param(
    [string]$linkPart,
    [string]$httpMethod,
    [string]$jsonFile = ""
)

# Buduj URL z stałym hostem i portem 8080
$url = "http://localhost:8080" + $linkPart

if ($httpMethod -ieq "GET") {
    # Dla GET wysyłamy żądanie bez ciała
    $response = Invoke-RestMethod -Uri $url -Method GET
} else {
    if ($jsonFile -ne "") {
        # Jeśli podano plik JSON, wczytaj dane
        $data = Get-Content -Path "./$jsonFile" -Raw | ConvertFrom-Json
        $body = $data | ConvertTo-Json -Depth 10 -Compress
    } else {
        # Jeśli nie podano pliku, użyj pustego ciała
        $body = ""
    }
    $response = Invoke-RestMethod -Uri $url -Method $httpMethod -Headers @{ "Content-Type" = "application/json" } -Body $body
}

Write-Output "Response: $($response)"
$response | Format-List *
