#!/usr/bin/env python3
"""
Test dla systemu detekcji REM
Symuluje wysyłanie danych co 30 sekund
"""

import json
import requests
import time
from datetime import datetime

def load_test_data():
    """Wczytaj dane testowe z pliku JSON"""
    with open('Mock_Scripts/data_embedded.json', 'r') as f:
        return json.load(f)

def simulate_rem_scenario():
    """
    Symuluje scenariusz w którym użytkownik przechodzi w fazę REM
    """
    print("🧪 === SYMULACJA DETEKCJI REM ===\n")
    
    # Wczytujemy bazowe dane
    base_data = load_test_data()
    
    # Endpoint Flask (uruchom serwer przed testem)
    url = "http://localhost:5000/embedded/data"
    status_url = "http://localhost:5000/embedded/rem_status"
    
    scenarios = [
        # Scenariusz 1: Użytkownik nie śpi
        {
            "name": "1. Użytkownik czuwa",
            "sleep_flag": False,
            "atonia_flag": False,
            "hr_boost": 0,
            "iterations": 3
        },
        # Scenariusz 2: Użytkownik śpi, ale brak atonii
        {
            "name": "2. Sen bez atonii mięśni",  
            "sleep_flag": True,
            "atonia_flag": False,
            "hr_boost": 0,
            "iterations": 3
        },
        # Scenariusz 3: Sen + atonia, ale stabilny HR
        {
            "name": "3. Sen + atonia, stabilny HR",
            "sleep_flag": True,
            "atonia_flag": True,
            "hr_boost": 0,
            "iterations": 10  # Budujemy historię 15 minut
        },
        # Scenariusz 4: Wszystkie warunki + wzrost HR → REM!
        {
            "name": "4. 🎯 WSZYSTKIE WARUNKI → REM!",
            "sleep_flag": True,
            "atonia_flag": True,
            "hr_boost": 8,  # +8 BPM wzrost
            "iterations": 3
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{'='*50}")
        print(f"📋 {scenario['name']}")
        print(f"😴 Sleep: {scenario['sleep_flag']}")
        print(f"💪 Atonia: {scenario['atonia_flag']}")
        print(f"❤️ HR boost: +{scenario['hr_boost']} BPM")
        print(f"🔄 Wysyłek: {scenario['iterations']}")
        print('='*50)
        
        for i in range(scenario['iterations']):
            # Przygotowujemy dane do wysłania
            test_data = base_data.copy()
            test_data['timestamp'] = datetime.now().isoformat()
            
            # Modyfikujemy flagi
            test_data['sensor_data']['mpu']['sleep_flag'] = scenario['sleep_flag']
            test_data['sensor_data']['emg']['atonia_flag'] = scenario['atonia_flag']
            
            # Modyfikujemy HR jeśli potrzeba
            if scenario['hr_boost'] > 0:
                for sample in test_data['sensor_data']['plethysmometer']:
                    sample['heart_rate'] += scenario['hr_boost']
            
            # Wysyłamy dane
            try:
                print(f"\n📤 Wysyłanie pakietu {i+1}/{scenario['iterations']}...")
                response = requests.post(url, json=test_data, timeout=5)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Odpowiedź: REM={result.get('rem_detected')}, próbek={result.get('total_hr_history')}")
                else:
                    print(f"❌ Błąd HTTP: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Błąd połączenia: {e}")
                print("💡 Upewnij się że serwer Flask jest uruchomiony!")
                return
            
            # Czekamy 2 sekundy (zamiast 30 dla testu)
            if i < scenario['iterations'] - 1:
                time.sleep(2)
        
        # Na koniec sprawdzamy status
        try:
            status_response = requests.get(status_url, timeout=5)
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"\n📊 Status końcowy:")
                print(f"   REM: {status.get('rem_detected')}")
                print(f"   Sleep: {status.get('sleep_detected')}")
                print(f"   Atonia: {status.get('atonia_detected')}")
                print(f"   HR próbek: {status.get('hr_stats', {}).get('total_samples', 0)}")
        except:
            print("❌ Nie udało się pobrać statusu")

def test_single_request():
    """Pojedynczy test wysłania danych"""
    print("🧪 === TEST POJEDYNCZEGO ŻĄDANIA ===\n")
    
    base_data = load_test_data()
    url = "http://localhost:5000/embedded/data"
    
    # Ustawiamy warunki dla REM
    base_data['sensor_data']['mpu']['sleep_flag'] = True
    base_data['sensor_data']['emg']['atonia_flag'] = True
    
    # Zwiększamy HR
    for sample in base_data['sensor_data']['plethysmometer']:
        sample['heart_rate'] += 10
    
    try:
        response = requests.post(url, json=base_data, timeout=5)
        print(f"📤 Status: {response.status_code}")
        print(f"📦 Odpowiedź: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Błąd: {e}")

if __name__ == "__main__":
    print("🔧 Wybierz test:")
    print("1. Pojedyncze żądanie")
    print("2. Pełna symulacja REM")
    
    choice = input("Wybór (1/2): ").strip()
    
    if choice == "1":
        test_single_request()
    elif choice == "2":
        simulate_rem_scenario()
    else:
        print("❌ Nieprawidłowy wybór")