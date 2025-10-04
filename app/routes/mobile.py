from flask import Blueprint, jsonify, session
from app.models import get_test
from ..rem_detection import get_hr_stats
from datetime import datetime

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
    current_phase = session.get('rem_phase_count')
    
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
            "current_phase": current_phase,
        }
    }
    
    return jsonify(response_data)
