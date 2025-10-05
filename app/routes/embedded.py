from flask import Blueprint, jsonify, request, session
from ..rem_detection import rem_detection, get_hr_stats
from ..sound_gen import generate_sound
from datetime import datetime

# In-memory storage dla danych sensorowych (temporary solution)
# W produkcji należy użyć bazy danych lub Redis
sensor_data_storage = {
    'hr_history': [],
    'mpu_history': [],
    'emg_history': [],
    'last_device_id': None,
    'last_update': None
}

embedded_bp = Blueprint('embedded', __name__)

@embedded_bp.route('/embedded/hello')
def embedded_hello():
    return jsonify("Hello from embedded")

@embedded_bp.route('/embedded/sensor_data', methods=['POST'])
def embedded_sensor_data():
    """
    Endpoint otrzymujący dane sensorowe z urządzenia (HR, MPU, EMG samples).
    Przechowuje dane dla dalszej analizy.
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Brak danych JSON"}), 400
    
    try:
        print(f"\nOtrzymano dane sensorowe z urzadzenia {data.get('device_id')} o {datetime.now().strftime('%H:%M:%S')}")
        
        # Pobieramy dane z sensorów
        sensor_data = data.get('sensor_data', {})
        
        # 1. PRZETWARZAMY DANE HR Z PLETHYSMOMETRU
        plethysmometer_data = sensor_data.get('plethysmometer', [])
        print(f"Otrzymano {len(plethysmometer_data)} probek HR")
        
        if plethysmometer_data and isinstance(plethysmometer_data, list):
            try:
                hr_values = [entry['heart_rate'] for entry in plethysmometer_data]
                print(f"HR w tym pakiecie: min={min(hr_values)}, max={max(hr_values)}, avg={sum(hr_values)/len(hr_values):.1f}")
                
                # Zapisujemy dane HR do global storage
                sensor_data_storage['hr_history'].extend(plethysmometer_data)
                print(f"DEBUG: Zapisano {len(plethysmometer_data)} próbek HR do storage")
                print(f"DEBUG: Łączna liczba próbek HR w storage: {len(sensor_data_storage['hr_history'])}")
                
            except Exception as hr_error:
                print(f"ERROR przy pobieraniu HR: {str(hr_error)}")
        
        # 2. PRZETWARZAMY DANE MPU (AKCELEROMETR/ŻYROSKOP)
        mpu_data = sensor_data.get('mpu', {})
        mpu_samples = mpu_data.get('samples', [])
        print(f"Otrzymano {len(mpu_samples)} probek MPU")
        
        # Zapisujemy dane MPU do storage
        sensor_data_storage['mpu_history'].extend(mpu_samples)
        
        # 3. PRZETWARZAMY DANE EMG (NAPIĘCIE MIĘŚNI)
        emg_data = sensor_data.get('emg', {})
        emg_samples = emg_data.get('samples', [])
        print(f"Otrzymano {len(emg_samples)} probek EMG")
        
        # Zapisujemy dane EMG do storage
        sensor_data_storage['emg_history'].extend(emg_samples)
        
        # 4. AKTUALIZUJEMY METADANE STORAGE I SESJI
        sensor_data_storage['last_update'] = datetime.now().isoformat()
        sensor_data_storage['last_device_id'] = data.get('device_id')
        
        session['last_sensor_update'] = datetime.now().isoformat()
        session['device_id'] = data.get('device_id')
        
        # 5. ODPOWIADAMY URZĄDZENIU
        response_data = {
            "status": "success",
            "message": "Sensor data received and stored",
            "device_id": data.get('device_id'),
            "timestamp": datetime.now().isoformat(),
            "samples_received": {
                "hr": len(plethysmometer_data),
                "mpu": len(mpu_samples),
                "emg": len(emg_samples)
            },
            "total_samples_stored": {
                "hr": len(sensor_data_storage['hr_history']),
                "mpu": len(sensor_data_storage['mpu_history']),
                "emg": len(sensor_data_storage['emg_history'])
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        import traceback
        print(f"ERROR przetwarzania danych sensorowych: {str(e)}")
        print(f"DEBUG traceback: {traceback.format_exc()}")
        return jsonify({"error": "Blad przetwarzania danych sensorowych", "details": str(e)}), 500


@embedded_bp.route('/embedded/flags', methods=['POST'])
def embedded_flags():
    """
    Endpoint otrzymujący flagi z urządzenia i wykonujący analizę REM.
    Na podstawie flag i zebranych wcześniej danych sensorowych decyduje o stanie REM.
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Brak danych JSON"}), 400
    
    try:
        print(f"\nOtrzymano flagi z urzadzenia {data.get('device_id')} o {datetime.now().strftime('%H:%M:%S')}")
        
        # Pobieramy flagi z requestu
        flags = data.get('flags', {})
        sleep_flag = flags.get('sleep_flag', False)
        atonia_flag = flags.get('atonia_flag', False)
        
        print(f"Sleep flag: {sleep_flag}")
        print(f"Atonia flag: {atonia_flag}")
        
        # Pobieramy zebrane wcześniej dane sensorowe z global storage
        hr_history = sensor_data_storage['hr_history']
        
        print("Sprawdzanie warunkow REM...")
        print(f"DEBUG: Storage last device: {sensor_data_storage['last_device_id']}")
        print(f"DEBUG: Storage last update: {sensor_data_storage['last_update']}")
        print(f"Dostępne dane HR z historii: {len(hr_history)} probek")
        
        # Sprawdzamy czy mamy wystarczające dane do analizy REM
        if not hr_history:
            print("BRAK DANYCH HR - nie można przeprowadzić analizy REM")
            rem_detected = False
        elif len(hr_history) < 900:  # Mniej niż 15 minut danych
            print(f"ZA MAŁO DANYCH HR - potrzeba 900 próbek, mamy {len(hr_history)}")
            print("TRYB TESTOWY: Sprawdzam REM z dostępnymi danymi")
            
            # Tryb testowy - sprawdzamy podstawowe warunki REM
            if sleep_flag and atonia_flag and len(hr_history) >= 60:  # Co najmniej 2 minuty danych
                # Prosty algorytm testowy - sprawdzamy wzrost HR
                recent_hr = [entry['heart_rate'] for entry in hr_history[-30:]]  # Ostatnie 30 próbek
                avg_recent = sum(recent_hr) / len(recent_hr)
                
                earlier_hr = [entry['heart_rate'] for entry in hr_history[-60:-30]]  # Wcześniejsze 30 próbek
                avg_earlier = sum(earlier_hr) / len(earlier_hr) if earlier_hr else avg_recent
                
                hr_increase = avg_recent - avg_earlier
                print(f"TRYB TESTOWY: HR wcześniej={avg_earlier:.1f}, teraz={avg_recent:.1f}, wzrost={hr_increase:+.1f}")
                
                if hr_increase >= 3.0:  # Niższy próg dla testów
                    print("TRYB TESTOWY: REM DETECTED (wzrost HR + flagi)")
                    rem_detected = True
                else:
                    print("TRYB TESTOWY: REM NIE WYKRYTY (brak wzrostu HR)")
                    rem_detected = False
            else:
                print("TRYB TESTOWY: REM NIE WYKRYTY (brak flag lub za mało danych)")
                rem_detected = False
        else:
            # Wywołujemy funkcję detekcji REM z danymi z storage
            rem_detected = rem_detection(
                plethysmometer_data=hr_history,
                sleep_flag=sleep_flag,
                atonia_flag=atonia_flag
            )
        
        # Sprawdzamy czy to nowa faza REM (przejście z False na True)
        previous_rem_flag = session.get('rem_flag', False)
        
        # Logika numeru bieżącej fazy REM
        if not previous_rem_flag and rem_detected:
            # Początek nowej fazy REM - zwiększamy numer fazy
            current_rem_phase = session.get('current_rem_phase', 0) + 1
            session['current_rem_phase'] = current_rem_phase
            print(f"NOWA FAZA REM WYKRYTA! Numer bieżącej fazy: {current_rem_phase}")
            
            # Automatyczne uruchomienie scenariusza dla tej fazy REM
            try_generate_sound_for_rem_phase(current_rem_phase)
            
        elif previous_rem_flag and not rem_detected:
            # Koniec fazy REM - resetujemy na 0 (nie w REM)
            session['current_rem_phase'] = 0
            print("KONIEC FAZY REM - powrót do normalnego snu")
        
        # Zapisujemy flagi i wynik analizy w sesji
        session['rem_flag'] = rem_detected
        session['sleep_flag'] = sleep_flag  
        session['atonia_flag'] = atonia_flag
        session['last_flags_update'] = datetime.now().isoformat()
        
        # Inicjalizujemy numer fazy jeśli nie istnieje
        if 'current_rem_phase' not in session:
            session['current_rem_phase'] = 0
        
        # Pobieramy statystyki do odpowiedzi
        hr_stats = get_hr_stats()
        
        print(f"WYNIK: REM = {rem_detected}")
        print(f"Statystyki HR: {hr_stats.get('total_samples', 0)} probek, srednia: {hr_stats.get('avg_hr_all', 0):.1f} BPM")
        
        # Odpowiadamy urządzeniu
        response_data = {
            "status": "success",
            "message": "Flags processed and REM analysis completed",
            "device_id": data.get('device_id'),
            "timestamp": datetime.now().isoformat(),
            "analysis_result": {
                "rem_detected": rem_detected,
                "current_rem_phase": session.get('current_rem_phase', 0),
                "previous_rem_state": previous_rem_flag,
                "state_changed": previous_rem_flag != rem_detected
            },
            "input_flags": {
                "sleep": sleep_flag,
                "atonia": atonia_flag
            },
            "data_analysis": {
                "hr_samples_used": len(hr_history),
                "hr_stats": hr_stats
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        import traceback
        print(f"ERROR przetwarzania flag: {str(e)}")
        print(f"DEBUG traceback: {traceback.format_exc()}")
        return jsonify({"error": "Blad przetwarzania flag", "details": str(e)}), 500


@embedded_bp.route('/embedded/data', methods=['POST'])
def embedded_data_legacy():
    """
    LEGACY ENDPOINT - dla kompatybilności wstecznej.
    Przekierowuje do nowych endpointów /embedded/sensor_data i /embedded/flags
    """
    # Ten endpoint może być używany przez stare urządzenia
    # Dzieli dane i wywołuje odpowiednie nowe endpointy
    return jsonify({
        "status": "deprecated",
        "message": "This endpoint is deprecated. Use /embedded/sensor_data and /embedded/flags instead",
        "new_endpoints": {
            "sensor_data": "/embedded/sensor_data",
            "flags": "/embedded/flags"
        }
    })

@embedded_bp.route('/embedded/rem_status', methods=['GET'])
def get_rem_status():
    """
    Endpoint dla aplikacji mobilnej - zwraca aktualny stan REM
    """
    rem_flag = session.get('rem_flag', False)
    sleep_flag = session.get('sleep_flag', False)
    atonia_flag = session.get('atonia_flag', False)
    last_update = session.get('last_update')
    device_id = session.get('device_id')
    current_rem_phase = session.get('current_rem_phase', 0)
    
    # Pobieramy statystyki HR
    hr_stats = get_hr_stats()
    
    return jsonify({
        "rem_detected": rem_flag,
        "sleep_detected": sleep_flag,
        "atonia_detected": atonia_flag,
        "current_rem_phase": current_rem_phase,
        "last_update": last_update,
        "device_id": device_id,
        "hr_stats": hr_stats
    })

@embedded_bp.route('/embedded/reset_rem_counter', methods=['POST'])
def reset_rem_counter():
    """
    Endpoint do resetowania numeru fazy REM (na początku nowej sesji snu)
    """
    session['current_rem_phase'] = 0
    session['rem_flag'] = False
    print("Zresetowano numer fazy REM")
    
    return jsonify({
        "status": "success",
        "message": "Numer fazy REM został zresetowany",
        "current_rem_phase": 0
    })

def try_generate_sound_for_rem_phase(rem_phase_number):
    """
    Próbuje wygenerować dźwięk dla danej fazy REM na podstawie załadowanych scenariuszy
    
    Args:
        rem_phase_number (int): Numer fazy REM (1, 2, 3, ...)
    """
    # Pobieramy scenariusze z sesji
    dream_scenarios = session.get('dream_scenarios', [])
    
    if not dream_scenarios:
        print(f"Brak scenariuszy dla fazy REM #{rem_phase_number}")
        return
    
    # Obliczamy indeks scenariusza (cyklicznie jeśli mamy więcej faz niż scenariuszy)
    scenario_index = (rem_phase_number - 1) % len(dream_scenarios)
    scenario = dream_scenarios[scenario_index]
    
    # Sprawdzamy czy scenariusz ma wymagane dane
    key_words = scenario.get('key_words', '').strip()
    place = scenario.get('place', '').strip()
    
    if not key_words and not place:
        print(f"Scenariusz #{scenario_index} nie ma żadnych danych (key_words i place są puste)")
        return
        
    print(f"Uruchamianie generate_sound dla fazy REM #{rem_phase_number}")
    print(f"  Scenariusz #{scenario_index}: key_words='{key_words}', place='{place}'")
    
    try:
        # Wywołujemy funkcję generowania dźwięku
        generate_sound(key_words, place)
        print(f"  Sukces: generate_sound wykonane dla fazy REM #{rem_phase_number}")
    except Exception as e:
        print(f"  ERROR: Błąd podczas generate_sound: {str(e)}")
