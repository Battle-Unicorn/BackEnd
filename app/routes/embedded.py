from flask import Blueprint, jsonify, request, session
from ..rem_detection import rem_detection, get_hr_stats
from datetime import datetime

embedded_bp = Blueprint('embedded', __name__)

@embedded_bp.route('/embedded/hello')
def embedded_helo():
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
        print(f"\n🔄 Otrzymano dane z urządzenia {data.get('device_id')} o {datetime.now().strftime('%H:%M:%S')}")
        
        # Pobieramy dane z sensorów
        sensor_data = data.get('sensor_data', {})
        
        # 1. POBIERAMY DANE HR Z PLETHYSMOMETRU
        plethysmometer_data = sensor_data.get('plethysmometer', [])
        print(f"📊 Otrzymano {len(plethysmometer_data)} próbek HR")
        
        if plethysmometer_data:
            hr_values = [entry['heart_rate'] for entry in plethysmometer_data]
            print(f"❤️ HR w tym pakiecie: min={min(hr_values)}, max={max(hr_values)}, avg={sum(hr_values)/len(hr_values):.1f}")
        
        # 2. POBIERAMY FLAGI ZE SENSORÓW
        mpu_data = sensor_data.get('mpu', {})
        emg_data = sensor_data.get('emg', {})
        
        sleep_flag = mpu_data.get('sleep_flag', False)
        atonia_flag = emg_data.get('atonia_flag', False)
        
        print(f"😴 Sleep flag: {sleep_flag}")
        print(f"💪 Atonia flag: {atonia_flag}")
        
        # 3. ANALIZA REM - SPRAWDZAMY WARUNKI
        print("🔍 Sprawdzanie warunków REM...")
        
        # Wywołujemy funkcję detekcji REM z wszystkimi danymi
        rem_detected = rem_detection(
            plethysmometer_data=plethysmometer_data,
            sleep_flag=sleep_flag,
            atonia_flag=atonia_flag
        )
        
        # 4. ZAPISUJEMY WYNIKI W SESJI
        session['rem_flag'] = rem_detected
        session['sleep_flag'] = sleep_flag  
        session['atonia_flag'] = atonia_flag
        session['last_update'] = datetime.now().isoformat()
        session['device_id'] = data.get('device_id')
        
        # 5. POBIERAMY STATYSTYKI DO LOGOWANIA
        hr_stats = get_hr_stats()
        
        print(f"🎯 WYNIK: REM = {rem_detected}")
        print(f"📈 Statystyki HR: {hr_stats.get('total_samples', 0)} próbek, średnia: {hr_stats.get('avg_hr_all', 0):.1f} BPM")
        
        # 6. ODPOWIADAMY URZĄDZENIU
        response_data = {
            "status": "success",
            "device_id": data.get('device_id'),
            "timestamp": datetime.now().isoformat(),
            "rem_detected": rem_detected,
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
        print(f"❌ Błąd przetwarzania danych: {str(e)}")
        return jsonify({"error": "Błąd przetwarzania danych", "details": str(e)}), 500

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
    
    # Pobieramy statystyki HR
    hr_stats = get_hr_stats()
    
    return jsonify({
        "rem_detected": rem_flag,
        "sleep_detected": sleep_flag,
        "atonia_detected": atonia_flag,
        "last_update": last_update,
        "device_id": device_id,
        "hr_stats": hr_stats
    })
