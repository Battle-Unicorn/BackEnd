from flask import Blueprint, jsonify, session, request, send_file, abort
from ..rem_detection import get_hr_stats
from ..sound_gen import generate_sound, process_dream_scenario
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
    Endpoint dla aplikacji mobilnej - zwraca dane w formacie zgodnym z mobile_polling.json
    Obsługuje parametr ?detailed=true dla pełnych danych (kompatybilność wsteczna)
    """
    # Pobieramy dane z sesji
    rem_flag = session.get('rem_flag', False)
    current_rem_phase = session.get('current_rem_phase', 0)
    mobile_id = session.get('mobile_id', 'MOB_001')
    
    # Sprawdzamy czy klient chce szczegółowe dane
    detailed = request.args.get('detailed', 'false').lower() == 'true'
    
    if detailed:
        # Kompatybilność wsteczna - pełny format danych
        sleep_flag = session.get('sleep_flag', False)
        atonia_flag = session.get('atonia_flag', False)
        device_id = session.get('device_id')
        hr_stats = get_hr_stats()
        
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
    else:
        # Nowy prosty format - zgodny z mobile_polling.json
        response_data = {
            "mobile_id": mobile_id,
            "rem": "true" if rem_flag else "false",
            "current_rem_phase": str(current_rem_phase)
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
        generated_audio_data = []
        
        for i, scenario in enumerate(scenarios_data['dream_keywords']):
            key_words = scenario.get('key_words', '').strip()
            place = scenario.get('place', '').strip()
            
            # Sprawdzamy czy scenariusz ma jakiekolwiek dane
            if key_words or place:
                try:
                    print(f"Przetwarzanie scenariusza #{i}: key_words='{key_words}', place='{place}'")
                    audio_result = generate_sound(key_words, place)
                    
                    # Dodajemy informacje o wygenerowanym audio do odpowiedzi
                    scenario_audio = {
                        "scenario_index": i,
                        "key_words": key_words,
                        "place": place,
                        "generation_result": {
                            "status": audio_result.get("status"),
                            "tts_text": audio_result.get("tts_text"),
                            "sound_description": audio_result.get("sound_description"),
                            "message": audio_result.get("message")
                        }
                    }
                    
                    # Jeśli są pliki audio, dodajemy informację o ich dostępności
                    if audio_result.get("audio_files"):
                        scenario_audio["generation_result"]["audio_available"] = True
                        scenario_audio["generation_result"]["audio_files_info"] = {
                            "tts_file_available": "tts_file" in audio_result["audio_files"],
                            "sound_file_available": "sound_file" in audio_result["audio_files"]
                        }
                    else:
                        scenario_audio["generation_result"]["audio_available"] = False
                    
                    generated_audio_data.append(scenario_audio)
                    processed_scenarios += 1
                    print(f"  Sukces: generate_sound wykonane dla scenariusza #{i}")
                    
                except Exception as e:
                    print(f"  ERROR: Błąd podczas generate_sound dla scenariusza #{i}: {str(e)}")
                    # Dodajemy informację o błędzie
                    error_scenario = {
                        "scenario_index": i,
                        "key_words": key_words,
                        "place": place,
                        "generation_result": {
                            "status": "error",
                            "error": str(e),
                            "audio_available": False
                        }
                    }
                    generated_audio_data.append(error_scenario)
            else:
                print(f"Pominięto scenariusz #{i} - brak danych (key_words i place są puste)")
        
        return jsonify({
            "status": "success",
            "message": "Dream scenarios loaded successfully",
            "scenarios_count": len(scenarios_data['dream_keywords']),
            "processed_scenarios": processed_scenarios,
            "mobile_id": scenarios_data.get('mobile_id'),
            "generated_audio": generated_audio_data
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


@mobile_bp.route('/mobile/generate_audio', methods=['POST'])
def generate_audio_on_demand():
    """
    Endpoint do generowania audio na żądanie dla pojedynczego scenariusza
    Oczekuje JSON w formacie:
    {
        "key_words": "flying airplane clouds sky",
        "place": "high above mountains"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
            
        key_words = data.get('key_words', '').strip()
        place = data.get('place', '').strip()
        
        if not key_words and not place:
            return jsonify({
                "status": "error", 
                "message": "At least one of 'key_words' or 'place' must be provided"
            }), 400
        
        # Generujemy audio
        print(f"Generowanie audio na żądanie: key_words='{key_words}', place='{place}'")
        audio_result = generate_sound(key_words, place)
        
        # Przygotowujemy odpowiedź
        response = {
            "status": audio_result.get("status", "unknown"),
            "key_words": key_words,
            "place": place,
            "tts_text": audio_result.get("tts_text"),
            "sound_description": audio_result.get("sound_description"),
            "message": audio_result.get("message")
        }
        
        # Dodajemy informacje o plikach audio jeśli są dostępne
        if audio_result.get("audio_files"):
            response["audio_available"] = True
            audio_files = audio_result["audio_files"]
            
            # Zapisujemy ścieżki do plików w sesji dla późniejszego pobrania
            session_key = f"audio_files_{datetime.now().timestamp()}"
            session[session_key] = audio_files
            
            response["audio_download_info"] = {
                "session_key": session_key,
                "tts_available": "tts_file" in audio_files,
                "sound_available": "sound_file" in audio_files,
                "extended_available": "extended_file" in audio_files,
                "download_urls": {
                    "tts": f"/mobile/download_audio/{session_key}/tts",
                    "sound": f"/mobile/download_audio/{session_key}/sound",
                    "extended": f"/mobile/download_audio/{session_key}/extended"
                }
            }
        else:
            response["audio_available"] = False
            
        if audio_result.get("error"):
            response["error"] = audio_result["error"]
            return jsonify(response), 500
            
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error generating audio: {str(e)}"
        }), 500


@mobile_bp.route('/mobile/download_audio/<session_key>/<audio_type>')
def download_audio(session_key, audio_type):
    """
    Endpoint do pobierania wygenerowanych plików audio
    
    Args:
        session_key: Klucz sesji zawierający ścieżki do plików
        audio_type: 'tts' lub 'sound'
    """
    try:
        # Sprawdzamy czy mamy pliki w sesji
        audio_files = session.get(session_key)
        if not audio_files:
            return jsonify({
                "status": "error",
                "message": "Audio files not found in session"
            }), 404
            
        # Określamy który plik pobierać
        if audio_type == 'tts':
            file_key = 'tts_file'
        elif audio_type == 'sound':
            file_key = 'sound_file'
        elif audio_type == 'extended':
            file_key = 'extended_file'
        else:
            return jsonify({
                "status": "error",
                "message": "Invalid audio type. Use 'tts', 'sound', or 'extended'"
            }), 400
            
        file_path = audio_files.get(file_key)
        if not file_path:
            return jsonify({
                "status": "error",
                "message": f"Audio file type '{audio_type}' not available"
            }), 404
            
        # Sprawdzamy czy plik istnieje
        if not os.path.exists(file_path):
            return jsonify({
                "status": "error",
                "message": "Audio file not found on disk"
            }), 404
            
        # Zwracamy plik
        filename = f"dream_audio_{audio_type}_{session_key}.mp3"
        return send_file(file_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Error downloading audio: {str(e)}"
        }), 500



