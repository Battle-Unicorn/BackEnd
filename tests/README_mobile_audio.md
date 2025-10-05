# Mobile Audio Generation Tests

Testy dla systemu generowania audio dla aplikacji mobile w HackYeah25.

## Struktura testów

- `test_mobile_audio.py` - Testy API endpointów przez HTTP requests
- `test_direct_audio.py` - Testy bezpośrednie funkcji generowania audio  
- `test_mobile_audio.ps1` - Skrypt PowerShell do uruchamiania wszystkich testów
- `test_audio.py` - Podstawowy test diagnostyczny

## Przygotowanie środowiska

### 1. Klucze API

Utwórz plik `.env` z kluczami API:

```bash
DEEPSEEK_API_KEY=your_deepseek_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
FLASK_SECRET_KEY=your_secret_key
```

Lub użyj komendy do utworzenia template:
```bash
python test_direct_audio.py --create-env
```

### 2. Zależności Python

```bash
pip install -r requirements.txt
```

### 3. FFmpeg (dla pydub)

Pobierz i zainstaluj FFmpeg:
- Windows: https://ffmpeg.org/download.html#build-windows
- Lub użyj chocolatey: `choco install ffmpeg`

## Uruchamianie testów

### Opcja 1: PowerShell Script (Zalecane)

```powershell
# Wszystkie testy
.\test_mobile_audio.ps1

# Tylko testy bezpośrednie (bez Flask)
.\test_mobile_audio.ps1 -TestType direct

# Tylko testy API (wymaga uruchomionego Flask)
.\test_mobile_audio.ps1 -TestType api

# Pomoc
.\test_mobile_audio.ps1 -Help
```

### Opcja 2: Poszczególne testy

#### Testy bezpośrednie (bez Flask)
```bash
python test_direct_audio.py
```

#### Testy API (wymaga uruchomionego Flask)
```bash
# Najpierw uruchom Flask
python run.py
# lub
docker-compose up

# Potem uruchom testy API
python test_mobile_audio.py
```

## Co testują poszczególne skrypty

### test_direct_audio.py
- ✅ Sprawdza konfigurację środowiska (klucze API, zależności)
- ✅ Testuje funkcję `generate_sound()` bezpośrednio
- ✅ Sprawdza generowanie plików TTS, sound effects i extended audio
- ✅ Weryfikuje poprawność zapisanych plików

### test_mobile_audio.py  
- ✅ Testuje endpoint `/mobile/hello`
- ✅ Testuje endpoint `/mobile/connect_device` 
- ✅ Testuje endpoint `/mobile/generate_audio` (pojedynczy scenariusz)
- ✅ Testuje endpoint `/mobile/load_scenarios` (wiele scenariuszy naraz)
- ✅ Testuje endpoint `/mobile/polling`
- ✅ Testuje pobieranie plików audio przez `/mobile/download_audio`

## Przykładowe dane testowe

### Scenariusz pojedynczy
```json
{
    "key_words": "ocean waves gentle breeze",
    "place": "peaceful beach at sunset"
}
```

### Wiele scenariuszy
```json
{
    "mobile_id": "TEST_MOB_001", 
    "device_id": "TEST_DEV_001",
    "dream_keywords": [
        {
            "key_words": "ocean waves gentle breeze",
            "place": "peaceful beach at sunset"  
        },
        {
            "key_words": "forest birds chirping leaves",
            "place": "quiet woodland clearing"
        }
    ]
}
```

## Rozwiązywanie problemów

### Błąd: "ModuleNotFoundError: No module named 'flask'"
```bash
pip install -r requirements.txt
```

### Błąd: "pydub not available" 
```bash
# Zainstaluj FFmpeg
choco install ffmpeg
# lub pobierz z https://ffmpeg.org/
```

### Błąd: "DEEPSEEK_API_KEY not found"
- Sprawdź czy plik `.env` istnieje i zawiera klucze API
- Sprawdź czy zmienne są poprawnie ustawione

### Błąd: "Audio files not found on disk"
- Sprawdź uprawnienia do zapisu w katalogu `audio_files/`
- Sprawdź czy katalog istnieje i jest dostępny do zapisu

### Błąd połączenia z API ElevenLabs
- Sprawdź klucz API ElevenLabs
- Sprawdź połączenie internetowe
- Sprawdź limity API (ElevenLabs ma ograniczenia dla darmowych kont)

## Oczekiwane wyniki

### Udane testy powinny pokazać:
- ✅ Successful API connections
- ✅ Audio files generated (TTS, sound, extended)
- ✅ File sizes > 1KB
- ✅ Proper HTTP response codes (200)
- ✅ Valid JSON responses

### Pliki wygenerowane:
- `dream_tts_[timestamp].mp3` - Tekst TTS (polski)
- `dream_sound_[timestamp].mp3` - Efekt dźwiękowy (30s pętla)  
- `dream_extended_[timestamp].mp3` - Pełny 15-minutowy plik (TTS + background)

## Struktura odpowiedzi API

### /mobile/generate_audio
```json
{
    "status": "success",
    "key_words": "ocean waves", 
    "place": "beach",
    "tts_text": "Tekst po polsku dla TTS...",
    "sound_description": "Gentle ocean sounds...",
    "audio_available": true,
    "audio_download_info": {
        "download_urls": {
            "tts": "/mobile/download_audio/[key]/tts",
            "sound": "/mobile/download_audio/[key]/sound", 
            "extended": "/mobile/download_audio/[key]/extended"
        }
    }
}
```

### /mobile/load_scenarios
```json
{
    "status": "success",
    "scenarios_count": 3,
    "processed_scenarios": 3,
    "mobile_id": "TEST_MOB_001",
    "generated_audio": [
        {
            "scenario_index": 0,
            "generation_result": {
                "status": "success",
                "audio_available": true
            }
        }
    ]
}
```

## Kontakt

W przypadku problemów z testami, sprawdź logi w terminalu lub skonsultuj się z dokumentacją API endpointów w `app/routes/mobile.py`.