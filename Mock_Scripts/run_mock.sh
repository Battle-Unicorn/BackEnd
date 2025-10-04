#!/bin/bash

# Pobierz nazwę pliku JSON jako argument, domyślnie data_Linux.json
jsonFile=${1:-data_Linux.json}

# Wczytaj dane z pliku JSON i wyślij żądanie POST do endpointu /add
curl -X POST http://localhost:8080/add \
     -H "Content-Type: application/json" \
     -d @"$jsonFile"

# Opcjonalnie wyświetl wynik
echo "Żądanie wysłane"
