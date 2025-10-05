from flask import Blueprint, jsonify, request, session
from ..rem_detection import rem_detection, get_hr_stats
from ..sound_gen import generate_sound
from datetime import datetime

embedded_bp = Blueprint('embedded', __name__)

@embedded_bp.route('/embedded/hello')
def embedded_hello():
    return jsonify("Hello from embedded")

@embedded_bp.route('/embedded/data', methods=['POST'])
def embedded_data():
    """
    Endpoint otrzymujący dane z urządzenia co 30 sekund.
    Analizuje dane HR i ustawia flagę REM w sesji.
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Brak danych JSON"}), 400
    
    try:
        print(f"\nOtrzymano dane z urzadzenia {data.get('device_id')} o {datetime.now().strftime('%H:%M:%S')}")
        
        # DEBUG: Sprawdzamy strukturę danych
        print(f"DEBUG: Typ data: {type(data)}")
        print(f"DEBUG: Klucze data: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        
        # Pobieramy dane z sensorów
        sensor_data = data.get('sensor_data', {})
        print(f"DEBUG: Typ sensor_data: {type(sensor_data)}")
        print(f"DEBUG: Klucze sensor_data: {list(sensor_data.keys()) if isinstance(sensor_data, dict) else 'Not a dict'}")
        
        # 1. POBIERAMY DANE HR Z PLETHYSMOMETRU
        plethysmometer_data = sensor_data.get('plethysmometer', [])
        print(f"DEBUG: Typ plethysmometer_data: {type(plethysmometer_data)}")
        print(f"Otrzymano {len(plethysmometer_data) if isinstance(plethysmometer_data, list) else 'NOT A LIST'} probek HR")
        
        if plethysmometer_data and isinstance(plethysmometer_data, list):
            # DEBUG: Sprawdzamy pierwszy element
            if len(plethysmometer_data) > 0:
                print(f"DEBUG: Pierwszy element: {plethysmometer_data[0]}")
                print(f"DEBUG: Typ pierwszego elementu: {type(plethysmometer_data[0])}")
            
            try:
                hr_values = [entry['heart_rate'] for entry in plethysmometer_data]
                print(f"HR w tym pakiecie: min={min(hr_values)}, max={max(hr_values)}, avg={sum(hr_values)/len(hr_values):.1f}")
            except Exception as hr_error:
                print(f"ERROR przy pobieraniu HR: {str(hr_error)}")
                print(f"DEBUG: plethysmometer_data content: {plethysmometer_data[:2]}")  # Pokazujemy pierwsze 2 elementy
        
        # 2. POBIERAMY FLAGI ZE SENSORÓW
        mpu_data = sensor_data.get('mpu', {})
        emg_data = sensor_data.get('emg', {})
        
        sleep_flag = mpu_data.get('sleep_flag', False)
        atonia_flag = emg_data.get('atonia_flag', False)
        
        print(f"Sleep flag: {sleep_flag}")
        print(f"Atonia flag: {atonia_flag}")
        
        # 3. ANALIZA REM - SPRAWDZAMY WARUNKI
        print("Sprawdzanie warunkow REM...")
        
        # Sprawdzamy czy mamy prawidłowe dane przed wywołaniem rem_detection
        if not isinstance(plethysmometer_data, list):
            raise ValueError(f"plethysmometer_data is not a list, it's {type(plethysmometer_data)}")
        
        # Wywołujemy funkcję detekcji REM z wszystkimi danymi
        rem_detected = rem_detection(
            plethysmometer_data=plethysmometer_data,
            sleep_flag=sleep_flag,
            atonia_flag=atonia_flag
        )
        
        # 4. ZAPISUJEMY WYNIKI W SESJI
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
        # Jeśli stan się nie zmienił, pozostawiamy obecny numer fazy
        
        session['rem_flag'] = rem_detected
        session['sleep_flag'] = sleep_flag  
        session['atonia_flag'] = atonia_flag
        session['last_update'] = datetime.now().isoformat()
        session['device_id'] = data.get('device_id')
        
        # Inicjalizujemy numer fazy jeśli nie istnieje
        if 'current_rem_phase' not in session:
            session['current_rem_phase'] = 0
        
        # 5. POBIERAMY STATYSTYKI DO LOGOWANIA
        hr_stats = get_hr_stats()
        
        print(f"WYNIK: REM = {rem_detected}")
        print(f"Statystyki HR: {hr_stats.get('total_samples', 0)} probek, srednia: {hr_stats.get('avg_hr_all', 0):.1f} BPM")
        
        # 6. ODPOWIADAMY URZĄDZENIU
        response_data = {
            "status": "success",
            "device_id": data.get('device_id'),
            "timestamp": datetime.now().isoformat(),
            "rem_detected": rem_detected,
            "current_rem_phase": session.get('current_rem_phase', 0),
            "samples_processed": len(plethysmometer_data),
            "total_hr_history": hr_stats.get('total_samples', 0),
            "flags": {
                "sleep": sleep_flag,
                "atonia": atonia_flag,
                "rem": rem_detected
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        import traceback
        print(f"ERROR przetwarzania danych: {str(e)}")
        print(f"DEBUG traceback: {traceback.format_exc()}")
        return jsonify({"error": "Blad przetwarzania danych", "details": str(e)}), 500

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
