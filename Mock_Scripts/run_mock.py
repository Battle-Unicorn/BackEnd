#!/usr/bin/env python3
"""
Mock script do testowania API - zastępuje run_mock.ps1
Użycie:
python run_mock.py <endpoint> <method> [json_file]

Przykłady:
python run_mock.py /embedded/data POST data_embedded.json
python run_mock.py /embedded/rem_status GET
python run_mock.py /embedded/reset_rem_counter POST
"""

import requests
import json
import sys
import os
from pathlib import Path

def main():
    if len(sys.argv) < 3:
        print("Użycie: python run_mock.py <endpoint> <method> [json_file]")
        print("Przykład: python run_mock.py /embedded/data POST data_embedded.json")
        sys.exit(1)
    
    endpoint = sys.argv[1]
    method = sys.argv[2].upper()
    json_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Buduj URL
    base_url = "http://localhost:8080"
    url = base_url + endpoint
    
    # Przygotuj headers
    headers = {
        "Content-Type": "application/json"
    }
    
    # Przygotuj body dla POST/PUT
    body = None
    if json_file and method in ['POST', 'PUT', 'PATCH']:
        json_path = Path(json_file)
        if not json_path.exists():
            print(f"ERROR: Plik {json_file} nie istnieje!")
            sys.exit(1)
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                body = json.load(f)
            print(f"Wczytano dane z pliku: {json_file}")
        except json.JSONDecodeError as e:
            print(f"ERROR: Nieprawidłowy JSON w pliku {json_file}: {e}")
            sys.exit(1)
    
    # Wyślij żądanie
    try:
        print(f"\nWysyłanie żądania: {method} {url}")
        if body:
            print(f"Body size: {len(json.dumps(body))} znaków")
        
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=body)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=body)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            print(f"ERROR: Nieobsługiwana metoda HTTP: {method}")
            sys.exit(1)
        
        # Wyświetl response
        print(f"\n=== RESPONSE ===")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        # Próbuj sparsować JSON response
        try:
            response_data = response.json()
            print(f"\nResponse JSON:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print(f"\nResponse Text:")
            print(response.text)
        
        # Sprawdź czy request się udał
        if response.status_code >= 400:
            print(f"\nERROR: Request failed with status {response.status_code}")
            sys.exit(1)
        else:
            print(f"\n✓ Request successful!")
            
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Nie można połączyć się z serwerem {base_url}")
        print("Czy serwer Flask jest uruchomiony?")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Problem z żądaniem HTTP: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()