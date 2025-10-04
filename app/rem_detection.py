
from datetime import datetime, timedelta
from typing import List, Dict

# Globalne przechowywanie danych HR (w produkcji powinno być w Redis lub bazie danych)
hr_history = []

def rem_detection(plethysmometer_data: list, sleep_flag: bool, atonia_flag: bool) -> bool:
    """
    Główna funkcja detekcji fazy REM
    
    Args:
        plethysmometer_data: Lista danych z plethysmometru (30 próbek co sekundę)
        sleep_flag: Czy użytkownik śpi (z MPU)
        atonia_flag: Czy jest atonia mięśni (z EMG)
    
    Returns:
        bool: True jeśli wykryto fazę REM
    """
    global hr_history
    
    # Sprawdzamy typ danych
    if not isinstance(plethysmometer_data, list):
        print(f"ERROR: plethysmometer_data nie jest lista: {type(plethysmometer_data)}")
        return False
    
    # Dodajemy nowe dane do historii
    current_time = datetime.now()
    
    for i, entry in enumerate(plethysmometer_data):
        # DEBUG: sprawdzamy każdy element
        if not isinstance(entry, dict):
            print(f"ERROR: Element {i} nie jest slownikiem: {type(entry)} = {entry}")
            continue
            
        if 'heart_rate' not in entry:
            print(f"ERROR: Element {i} nie ma klucza 'heart_rate': {entry}")
            continue
        try:
            hr_entry = {
                'heart_rate': entry['heart_rate'],
                'timestamp': entry.get('timestamp', current_time.isoformat()),
                'received_at': current_time
            }
            hr_history.append(hr_entry)
        except KeyError as e:
            print(f"ERROR: Brak klucza {e} w entry: {entry}")
            continue
    
    # Czyścimy stare dane (starsze niż 15 minut)
    cutoff_time = current_time - timedelta(minutes=15)
    hr_history = [entry for entry in hr_history if entry['received_at'] > cutoff_time]
    
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
    Funkcja sprawdza średnie HR z ostatnich 15 minut
    
    Returns:
        float: Średni HR z 15 minut
    """
    global hr_history
    
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
    Funkcja porównuje średnie HR do HR z ostatnich 30 sekund
    
    Args:
        medium_hr_15min: Średni HR z ostatnich 15 minut
    
    Returns:
        bool: True jeśli HR wzrósł o co najmniej 5 BPM
    """
    global hr_history
    
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
    Funkcja pomocnicza do debugowania - zwraca statystyki HR
    """
    global hr_history
    
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