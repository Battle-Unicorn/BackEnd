# Mock Scripts - Flask API Tester

Zbiór skryptów do testowania Flask API dla systemu wykrywania faz REM.

## Pliki:

### Skrypty:
- **`run_mock.ps1`** - Główny skrypt do wysyłania żądań HTTP
- **`mock_test.ps1`** - Pomocniczy skrypt z predefiniowanymi testami

### Dane testowe:
- **`data_embedded.json`** - Normalne dane z urządzenia (sleep=false, atonia=false)
- **`data_rem_test.json`** - Dane testowe z wyższym HR dla symulacji REM

## Użycie:

### Szybkie testy:
```powershell
.\mock_test.ps1 help     # Pomoc
.\mock_test.ps1 data     # Test normalnych danych
.\mock_test.ps1 rem      # Test danych REM
.\mock_test.ps1 status   # Sprawdź status
.\mock_test.ps1 reset    # Resetuj licznik
```

### Bezpośrednie użycie:
```powershell
.\run_mock.ps1 /embedded/data POST data_embedded.json
.\run_mock.ps1 /embedded/rem_status GET
.\run_mock.ps1 /embedded/reset_rem_counter POST
```

## Endpointy API:

- `POST /embedded/data` - Odbiera dane z urządzenia
- `GET /embedded/rem_status` - Zwraca aktualny status REM
- `POST /embedded/reset_rem_counter` - Resetuje licznik faz REM

## Wymagania:

- PowerShell 5.0+
- Działający serwer Flask na localhost:8080