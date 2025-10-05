
from datetime import datetime, timedelta
from typing import List, Dict

# Import shared storage from embedded module
# Usuwamy lokalny hr_history - używamy shared storage
def get_shared_storage():
    """Import shared storage - lazy import aby uniknąć cyklicznych importów"""
    try:
        from .routes.embedded import shared_storage
        return shared_storage
    except ImportError:
        # Fallback jeśli nie można zaimportować
        return None

def get_hr_history_from_storage():
    """Pobiera dane HR z shared storage"""
    shared_storage = get_shared_storage()
    if not shared_storage:
        return []
    
    # Zbieramy dane HR ze wszystkich urządzeń
    all_hr_data = []
    for device_id, device_data in shared_storage['devices'].items():
        all_hr_data.extend(device_data.get('hr_history', []))
    
    # Sortujemy po czasie otrzymania
    if all_hr_data:
        all_hr_data.sort(key=lambda x: x.get('received_at', datetime.now()))
    
    return all_hr_data

def rem_detection(plethysmometer_data: list, sleep_flag: bool, atonia_flag: bool) -> bool:
    """
    Główna funkcja detekcji fazy REM - używa shared storage zamiast globalnej zmiennej
    
    Args:
        plethysmometer_data: Lista danych z plethysmometru (30 próbek co sekundę)
        sleep_flag: Czy użytkownik śpi (z MPU)
        atonia_flag: Czy jest atonia mięśni (z EMG)
    
    Returns:
        bool: True jeśli wykryto fazę REM
    """
    # Pobieramy dane HR z shared storage
    hr_history = get_hr_history_from_storage()
    
    # Sprawdzamy typ danych
    if not isinstance(plethysmometer_data, list):
        print(f"ERROR: plethysmometer_data nie jest lista: {type(plethysmometer_data)}")
        return False
    
    # UWAGA: Dane są już dodane do shared storage przez embedded_sensor_data endpoint
    # Ta funkcja tylko analizuje istniejące dane, nie dodaje nowych
    print(f"Analizujemy {len(plethysmometer_data)} nowych próbek HR + {len(hr_history)} z historii")
    
    # Czyścimy stare dane z shared storage (starsze niż 15 minut)
    current_time = datetime.now()
    cutoff_time = current_time - timedelta(minutes=15)
    
    # Aktualizujemy shared storage aby usunąć stare dane
    shared_storage = get_shared_storage()
    if shared_storage:
        for device_id, device_data in shared_storage['devices'].items():
            original_count = len(device_data['hr_history'])
            device_data['hr_history'] = [
                entry for entry in device_data['hr_history'] 
                if entry.get('received_at', datetime.now()) > cutoff_time
            ]
            cleaned_count = original_count - len(device_data['hr_history'])
            if cleaned_count > 0:
                print(f"Cleaned {cleaned_count} old HR entries from device {device_id}")
    
    # Odświeżamy hr_history po czyszczeniu
    hr_history = get_hr_history_from_storage()
    
    print(f"Historia HR: {len(hr_history)} probek z ostatnich 15 minut")
    
    # Sprawdzamy czy mamy wystarczająco danych (co najmniej 15 minut)
    if len(hr_history) < 900:  # 15 minut * 60 sekund
        print(f"Za malo danych: {len(hr_history)}/900 probek")
        return False
    
    # Warunek 1: Użytkownik musi spać
    if not sleep_flag:
        print("Brak flagi snu - REM niemozliwy")
        return False
    
    # Warunek 2: Musi być atonia mięśni
    if not atonia_flag:
        print("Brak atonii miesni - REM niemozliwy")
        return False
    
    # Sprawdzamy wzrost HR
    medium_hr_15min = check_medium_hr()
    hr_increased = compare_medium_hr(medium_hr_15min)
    
    if hr_increased:
        print("Wykryto wzrost HR + wszystkie warunki spelnione -> REM DETECTED!")
        return True
    else:
        print("Brak wzrostu HR - REM nie wykryty")
        return False

def check_medium_hr() -> float:
    """
    Funkcja sprawdza średnie HR z ostatnich 15 minut - używa shared storage
    
    Returns:
        float: Średni HR z 15 minut
    """
    # Pobieramy dane z shared storage
    hr_history = get_hr_history_from_storage()
    
    if len(hr_history) < 900:
        return 0.0
    
    # Bierzemy ostatnie 15 minut danych (900 próbek)
    last_15_min = hr_history[-900:]
    
    # Obliczamy średnią
    total_hr = sum(entry['heart_rate'] for entry in last_15_min)
    medium_hr = total_hr / len(last_15_min)
    
    print(f"Sredni HR z 15 minut: {medium_hr:.1f} BPM")
    return medium_hr

def compare_medium_hr(medium_hr_15min: float) -> bool:
    """
    Funkcja porównuje średnie HR do HR z ostatnich 30 sekund - używa shared storage
    
    Args:
        medium_hr_15min: Średni HR z ostatnich 15 minut
    
    Returns:
        bool: True jeśli HR wzrósł o co najmniej 5 BPM
    """
    # Pobieramy dane z shared storage
    hr_history = get_hr_history_from_storage()
    
    if len(hr_history) < 30:
        print("Za malo danych do porownania (< 30 sekund)")
        return False
    
    # Bierzemy ostatnie 30 sekund
    last_30_sec = hr_history[-30:]

    # Obliczamy średnią z ostatnich 30 sekund
    current_hr = sum(entry['heart_rate'] for entry in last_30_sec) / len(last_30_sec)
    
    # Sprawdzamy wzrost
    hr_increase = current_hr - medium_hr_15min
    hr_threshold = 5.0  # Próg wzrostu w BPM
    
    print(f"HR ostatnie 30s: {current_hr:.1f} BPM")
    print(f"Wzrost HR: {hr_increase:+.1f} BPM (prog: +{hr_threshold})")
    
    return hr_increase >= hr_threshold

def get_hr_stats():
    """
    Funkcja pomocnicza do debugowania - zwraca statystyki HR z shared storage
    """
    # Pobieramy dane z shared storage
    hr_history = get_hr_history_from_storage()
    
    if not hr_history:
        return {"error": "Brak danych"}
    
    recent_hr = [entry['heart_rate'] for entry in hr_history[-30:]] if len(hr_history) >= 30 else []
    all_hr = [entry['heart_rate'] for entry in hr_history]
    
    return {
        "total_samples": len(hr_history),
        "avg_hr_all": sum(all_hr) / len(all_hr) if all_hr else 0,
        "avg_hr_recent": sum(recent_hr) / len(recent_hr) if recent_hr else 0,
        "min_hr": min(all_hr) if all_hr else 0,
        "max_hr": max(all_hr) if all_hr else 0,
        "recent_samples": len(recent_hr)
    }