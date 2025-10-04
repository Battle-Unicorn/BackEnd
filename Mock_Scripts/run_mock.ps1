param(
    [string]$jsonFile = "data_PS.json"
)

# Wczytaj zawartość pliku JSON do zmiennej
$data = Get-Content -Path "./$jsonFile" -Raw | ConvertFrom-Json

# Wyślij żądanie POST do endpointu /add
$response = Invoke-RestMethod -Uri http://localhost:8080/add -Method Post -Headers @{ "Content-Type" = "application/json" } -Body ($data | ConvertTo-Json)

# Wyświetl odpowiedź
Write-Output "Response: $($response)"

# Opcjonalnie wyświetl wszystkie szczegóły odpowiedzi
$response | Format-List *
