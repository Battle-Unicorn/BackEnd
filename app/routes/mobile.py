from flask import Blueprint, jsonify, session, request
from ..rem_detection import get_hr_stats
from ..sound_gen import generate_sound
from datetime import datetime
import json
import os

mobile_bp = Blueprint('mobile', __name__)


@mobile_bp.route('/mobile/hello')
def mobile_hello():
    return jsonify("Hello from mobile")

@mobile_bp.route('/mobile/polling')
def mobile_polling():
    """
    Endpoint dla aplikacji mobilnej - zwraca dane z sesji
    """
    # Pobieramy dane z sesji
    rem_flag = session.get('rem_flag', False)
    sleep_flag = session.get('sleep_flag', False)
    atonia_flag = session.get('atonia_flag', False)
    #last_update = session.get('last_update')
    device_id = session.get('device_id')
    current_rem_phase = session.get('current_rem_phase', 0)
    
    # Pobieramy statystyki HR
    hr_stats = get_hr_stats()
    
    # REM wykrywany gdy wszystkie warunki spełnione
    # rem_flag już zawiera wynik detekcji z sesji
    
    # Przygotowujemy odpowiedź JSON
    response_data = {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "session_data": {
            "rem_detected": rem_flag,
            "sleep_detected": sleep_flag,
            "atonia_detected": atonia_flag,
            "device_id": device_id
        },
        "hr_statistics": hr_stats,
        "rem_phases": {
            "current_phase": current_rem_phase,
        }
    }
    
    return jsonify(response_data)

@mobile_bp.route('/mobile/load_scenarios', methods=['POST'])
def load_dream_scenarios():
    """
    Endpoint do ładowania scenariuszy snów z request body do sesji
    Oczekuje JSON w formacie:
    {
        "mobile_id": "MOB_001",
        "dream_keywords": [
            {"key_words": "flying airplane clouds sky", "place": "high above mountains"},
            ...
        ]
    }
    """
    try:
        # Pobieramy dane JSON z request body
        scenarios_data = request.get_json()
        
        if not scenarios_data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided in request body"
            }), 400
            
        if 'dream_keywords' not in scenarios_data:
            return jsonify({
                "status": "error",
                "message": "Missing 'dream_keywords' field in request data"
            }), 400
            
        if not isinstance(scenarios_data['dream_keywords'], list):
            return jsonify({
                "status": "error",
                "message": "'dream_keywords' must be an array"
            }), 400
            
        # Zapisujemy scenariusze w sesji
        session['dream_scenarios'] = scenarios_data['dream_keywords']
        session['current_scenario_index'] = 0
        session['mobile_id'] = scenarios_data.get('mobile_id', 'unknown')
        
        # Wywołujemy generate_sound dla każdego scenariusza który ma dane
        processed_scenarios = 0
        for i, scenario in enumerate(scenarios_data['dream_keywords']):
            key_words = scenario.get('key_words', '').strip()
            place = scenario.get('place', '').strip()
            
            # Sprawdzamy czy scenariusz ma jakiekolwiek dane
            if key_words or place:
                try:
                    print(f"Przetwarzanie scenariusza #{i}: key_words='{key_words}', place='{place}'")
                    generate_sound(key_words, place)
                    processed_scenarios += 1
                    print(f"  Sukces: generate_sound wykonane dla scenariusza #{i}")
                except Exception as e:
                    print(f"  ERROR: Błąd podczas generate_sound dla scenariusza #{i}: {str(e)}")
            else:
                print(f"Pominięto scenariusz #{i} - brak danych (key_words i place są puste)")
        
        return jsonify({
            "status": "success",
            "message": "Dream scenarios loaded successfully",
            "scenarios_count": len(scenarios_data['dream_keywords']),
            "processed_scenarios": processed_scenarios,
            "mobile_id": scenarios_data.get('mobile_id')
        })
        
    except json.JSONDecodeError:
        return jsonify({
            "status": "error", 
            "message": "Invalid JSON format in request body"
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error loading scenarios: {str(e)}"
        }), 500



