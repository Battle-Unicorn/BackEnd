import os
from datetime import datetime
from openai import OpenAI
from elevenlabs.client import ElevenLabs
import json
import io

# Import shared storage for mobile session scenarios
def get_shared_storage():
    """Import shared storage - lazy import aby uniknąć cyklicznych importów"""
    try:
        from .routes.embedded import shared_storage
        return shared_storage
    except ImportError:
        # Fallback jeśli nie można zaimportować
        return None

def get_dream_scenarios_from_storage():
    """Pobiera scenariusze snów z shared storage"""
    shared_storage = get_shared_storage()
    if not shared_storage:
        return []
    
    # Szukamy scenariuszy w aktywnych sesjach mobile
    for mobile_id, mobile_data in shared_storage['mobile_sessions'].items():
        scenarios = mobile_data.get('dream_scenarios', [])
        if scenarios:
            print(f"Found {len(scenarios)} dream scenarios in mobile session {mobile_id}")
            return scenarios
    
    return []

def log_audio_generation_to_storage(scenario_result, audio_files):
    """Loguje aktywność generowania audio do shared storage"""
    shared_storage = get_shared_storage()
    if not shared_storage:
        return
    
    # Dodajemy log do global stats
    if 'audio_generation_log' not in shared_storage['global_stats']:
        shared_storage['global_stats']['audio_generation_log'] = []
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'tts_text': scenario_result.get('tts_text', ''),
        'sound_description': scenario_result.get('sound_description', ''),
        'files_generated': list(audio_files.keys()) if audio_files else [],
        'rem_phase': shared_storage['current_rem_state'].get('current_rem_phase', 0)
    }
    
    shared_storage['global_stats']['audio_generation_log'].append(log_entry)
    
    # Ograniczamy log do ostatnich 50 wpisów
    if len(shared_storage['global_stats']['audio_generation_log']) > 50:
        shared_storage['global_stats']['audio_generation_log'] = shared_storage['global_stats']['audio_generation_log'][-50:]
    
    print(f"Logged audio generation to shared storage: {len(audio_files) if audio_files else 0} files")

# Try to import pydub, but handle the Python 3.13 audioop issue
try:
    # Próbujemy zaimportować pydub
    from pydub import AudioSegment
    from pydub.utils import which
    # Sprawdź czy ffmpeg jest dostępny
    if which("ffmpeg") is None:
        print("Warning: ffmpeg not found - some pydub operations may fail")
    PYDUB_AVAILABLE = True
    print("pydub imported successfully")
except Exception as e:
    print(f"pydub not available: {e}")
    print("This is expected with Python 3.13 due to missing audioop module")
    print("Audio processing will use simple fallbacks")
    PYDUB_AVAILABLE = False
    AudioSegment = None

def process_dream_scenario(key_words, place):
    """
    Funkcja do przetwarzania scenariuszy snów na podstawie słów kluczowych i miejsca

    Args:
        key_words (str): Słowa kluczowe opisujące sen (np. "flying airplane clouds sky")
        place (str): Miejsce w którym toczy się sen (np. "high above mountains")

    Returns:
        dict: Zawiera wygenerowany tekst TTS i opis dźwięku
    """
    try:
        # Konfiguracja DeepSeek API
        deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        if not deepseek_api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables")

        client = OpenAI(
            api_key=deepseek_api_key,
            base_url="https://api.deepseek.com"
        )

        # Przygotowanie prompta dla DeepSeek
        prompt = f"""
        Jesteś ekspertem od świadomych snów. Na podstawie podanych słów kluczowych i miejsca, wygeneruj:

        1. TEKST_TTS: Krótki, uspokajający tekst (Do 50 słów) po polsku, który pomoże osobie śniącej uświadomić sobie, że śni. Tekst powinien być łagodny i pomocny w osiągnięciu świadomego snu.

        2. OPIS_DZWIEKU: Krótki opis efektu dźwiękowego po angielsku (max 300 znaków). Konkretne dźwięki ambientowe związane z miejscem i słowami kluczowymi.

        SŁOWA KLUCZOWE: {key_words}
        MIEJSCE: {place}

        Odpowiedz w formacie JSON:
        {{
            "tts_text": "tekst do TTS po polsku",
            "sound_description": "opis dźwięku po angielsku"
        }}
        """

        # Wywołanie DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )

        # Parsowanie odpowiedzi
        content = response.choices[0].message.content

        # Próba parsowania JSON z odpowiedzi
        try:
            # Szukamy JSON w odpowiedzi
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_content = content[json_start:json_end]
                result = json.loads(json_content)
            else:
                # Fallback - tworzymy domyślną odpowiedź
                result = {
                    "tts_text": f"Znajdujesz się w pięknym miejscu: {place}. Pamiętaj o {key_words}. To jest sen - możesz teraz świadomie go kontrolować.",
                    "sound_description": f"Gentle ambient sounds: {key_words} in {place}, soft peaceful music, calming atmosphere"
                }
        except json.JSONDecodeError:
            # Fallback w przypadku błędu parsowania
            result = {
                "tts_text": f"Znajdujesz się w pięknym miejscu: {place}. Pamiętaj o {key_words}. To jest sen - możesz teraz świadomie go kontrolować.",
                "sound_description": f"Gentle ambient sounds related to {key_words} in {place}, soft and peaceful background music"
            }

        print(f"DeepSeek response: {result}")
        return result

    except Exception as e:
        print(f"Błąd w process_dream_scenario: {str(e)}")
        # Zwracamy fallback w przypadku błędu
        return {
            "tts_text": f"Jesteś w miejscu: {place}. Pamiętaj o {key_words}. To jest twój sen.",
            "sound_description": f"Calming ambient sounds: {key_words} in {place}, peaceful background music"
        }


def generate_sound(key_words, place):
    """
    Główna funkcja generująca dźwięk na podstawie scenariusza snu

    Args:
        key_words (str): Słowa kluczowe opisujące sen
        place (str): Miejsce w którym toczy się sen

    Returns:
        dict: Zawiera informacje o wygenerowanych plikach audio
    """
    try:
        # Przetwarzamy scenariusz przez DeepSeek
        scenario_result = process_dream_scenario(key_words, place)

        # Konfiguracja ElevenLabs
        elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        if not elevenlabs_api_key:
            print("ELEVENLABS_API_KEY not found - skipping audio generation")
            return {
                "status": "success",
                "tts_text": scenario_result["tts_text"],
                "sound_description": scenario_result["sound_description"],
                "audio_files": None,
                "message": "API key missing - text only"
            }

        client = ElevenLabs(api_key=elevenlabs_api_key)

        # Generowanie TTS - użyjmy prawidłowego API
        print(f"Generating TTS for: {scenario_result['tts_text'][:100]}...")
        tts_audio = client.text_to_speech.convert(
            text=scenario_result["tts_text"],
            voice_id="EXAVITQu4vr4xnSDxMaL",  # Bella - wielojęzyczny głos
            model_id="eleven_multilingual_v2"
        )

        # Generowanie sound effect - dla efektów dźwiękowych użyjemy sound generation API
        sound_effect = client.text_to_sound_effects.convert(
            text=scenario_result["sound_description"],
            loop=True,  # Tworzymy pętlę dźwiękową
            duration_seconds=30.0,  # 30 sekund jak wymagane
            model_id="eleven_text_to_sound_v2"  # Model dla efektów dźwiękowych
        )

        # Zapisanie plików w katalogu audio_files
        audio_files = {}
        timestamp = int(datetime.now().timestamp())

        # Tworzenie nazw plików z timestampem
        audio_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'audio_files')
        os.makedirs(audio_dir, exist_ok=True)

        print(f"Audio directory: {audio_dir}")

        # Sprawdzamy czy mamy uprawnienia do zapisu
        if not os.access(audio_dir, os.W_OK):
            raise PermissionError(f"No write permission to audio directory: {audio_dir}")

        # Zbieranie bajtów audio do pamięci dla przetworzenia
        tts_bytes = b"".join(chunk for chunk in tts_audio)
        sound_effect_bytes = b"".join(chunk for chunk in sound_effect)
        
        print("Creating extended 15-minute audio with fade-in and TTS mixing...")
        extended_audio_bytes = create_extended_audio(tts_bytes, sound_effect_bytes)
        
        # TTS file (oryginalny)
        tts_filename = f"dream_tts_{timestamp}.mp3"
        tts_filepath = os.path.join(audio_dir, tts_filename)
        with open(tts_filepath, "wb") as f:
            f.write(tts_bytes)
        audio_files["tts_file"] = tts_filepath

        # Sound effect file (30s pętla)
        sound_filename = f"dream_sound_{timestamp}.mp3"
        sound_filepath = os.path.join(audio_dir, sound_filename)
        with open(sound_filepath, "wb") as f:
            f.write(sound_effect_bytes)
        audio_files["sound_file"] = sound_filepath
        
        # Extended 15-minute file (główny plik do użycia)
        extended_filename = f"dream_extended_{timestamp}.mp3"
        extended_filepath = os.path.join(audio_dir, extended_filename)
        with open(extended_filepath, "wb") as f:
            f.write(extended_audio_bytes)
        audio_files["extended_file"] = extended_filepath

        print(f"Audio files generated: {audio_files}")

        # Logujemy aktywność do shared storage
        log_audio_generation_to_storage(scenario_result, audio_files)
        
        return {
            "status": "success",
            "tts_text": scenario_result["tts_text"],
            "sound_description": scenario_result["sound_description"],
            "audio_files": audio_files,
            "message": "Audio generated successfully"
        }

    except Exception as e:
        print(f"Błąd w generate_sound: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "tts_text": None,
            "sound_description": None,
            "audio_files": None
        }


def create_simple_extended_audio(tts_audio_bytes, sound_effect_bytes):
    """
    Prosty fallback - tworzy 15-minutowe audio bez zaawansowanego miksowania
    Gdy pydub nie jest dostępny, zapisuje pliki osobno i zwraca background
    
    Args:
        tts_audio_bytes: Bajty TTS audio
        sound_effect_bytes: Bajty sound effect (30s)
        
    Returns:
        bytes: Rozszerzone background audio (bez prawidłowego miksowania)
    """
    print("Creating simple extended audio fallback...")
    print("WARNING: Without pydub, audio mixing is not available!")
    print("This will create a looped background - TTS will be in separate file")
    
    # Bez pydub nie możemy prawidłowo miksować - zwracamy tylko rozszerzony background
    # TTS będzie w osobnym pliku
    
    # Szacujemy ile powtórzeń potrzebujemy dla 15 minut
    # Zakładamy że 30s sound effect to około 480KB (16kbps * 30s)
    estimated_30s_duration = 30
    target_duration = 15 * 60  # 15 minut w sekundach
    repetitions = target_duration // estimated_30s_duration
    
    print(f"Repeating 30s loop {repetitions} times for ~{repetitions * 30/60:.1f} minutes")
    
    # Tworzymy rozszerzony background przez powtórzenie
    extended_background = sound_effect_bytes
    for i in range(repetitions - 1):  # -1 bo już mamy jeden
        extended_background += sound_effect_bytes
        if i % 10 == 0:
            print(f"Added repetition {i+2}/{repetitions}")
    
    print(f"Simple fallback created: Extended background ({len(extended_background)} bytes)")
    print("Note: TTS audio will be saved as separate file due to mixing limitations")
    
    return extended_background


def create_extended_audio(tts_audio_bytes, sound_effect_bytes):
    """
    Tworzy 15-minutowe audio z 30-sekundowej pętli i TTS z fade-in i miksowaniem
    
    Args:
        tts_audio_bytes: Surowe bajty audio TTS 
        sound_effect_bytes: Surowe bajty audio sound effect (30s pętla)
        
    Returns:
        bytes: 15-minutowe audio MP3 z fade-in i zmiksowanym TTS
    """
    try:
        # Sprawdzenie czy pydub jest dostępny
        if not PYDUB_AVAILABLE:
            print("pydub not available - using simple fallback...")
            return create_simple_extended_audio(tts_audio_bytes, sound_effect_bytes)
            
        print("Creating extended audio with pydub...")
        
        # Konwersja bajtów do AudioSegment
        print("Converting audio bytes to AudioSegment...")
        try:
            tts_segment = AudioSegment.from_mp3(io.BytesIO(tts_audio_bytes))
            sound_loop = AudioSegment.from_mp3(io.BytesIO(sound_effect_bytes))
            print(f"Successfully loaded: TTS ({len(tts_segment)}ms), Loop ({len(sound_loop)}ms)")
        except Exception as conversion_error:
            print(f"Error converting audio to AudioSegment: {conversion_error}")
            print("Falling back to simple audio extension...")
            return create_simple_extended_audio(tts_audio_bytes, sound_effect_bytes)
        
        # Sprawdzenie długości pętli
        loop_duration_ms = len(sound_loop)
        print(f"Sound loop duration: {loop_duration_ms}ms (~{loop_duration_ms/1000:.1f}s)")
        
        # Obliczenie ile razy powtórzyć pętlę dla 15 minut
        target_duration_ms = 15 * 60 * 1000  # 15 minut w ms
        repetitions = target_duration_ms // loop_duration_ms
        remaining_ms = target_duration_ms % loop_duration_ms
        
        print(f"Creating {repetitions} full loops + {remaining_ms}ms partial loop")
        
        # Tworzenie 15-minutowego tła przez powtarzanie pętli
        extended_background = AudioSegment.empty()
        
        # Dodanie pełnych pętli
        for i in range(repetitions):
            extended_background += sound_loop
            if i % 10 == 0:  # Progress info co 10 pętli
                print(f"Added {i+1}/{repetitions} loops...")
            
        # Dodanie częściowej pętli jeśli potrzebna
        if remaining_ms > 0:
            extended_background += sound_loop[:remaining_ms]
            
        print(f"Extended background duration: {len(extended_background)}ms ({len(extended_background)/60000:.1f} min)")
        
        # 10-sekundowy fade-in na początku
        print("Adding 10s fade-in...")
        fade_in_duration_ms = 10000  # 10 sekund
        extended_background = extended_background.fade_in(fade_in_duration_ms)
        
        # 5-sekundowy fade-out na końcu dla gładkiego zakończenia
        print("Adding 5s fade-out...")
        fade_out_duration_ms = 5000  # 5 sekund  
        extended_background = extended_background.fade_out(fade_out_duration_ms)
        
        # Miksowanie TTS po fade-in (od 10. sekundy)
        print("Mixing TTS after fade-in...")
        tts_start_ms = fade_in_duration_ms  # Start od 10s
        
        # Normalizacja głośności TTS i background przed miksowaniem
        print("Normalizing audio levels...")
        # Zmniejszamy głośność background żeby TTS było wyraźnie słyszalne
        extended_background = extended_background - 15  # -15dB dla background
        
        # Jeśli TTS jest dłuższe niż pozostały czas, skracamy go
        available_time_ms = len(extended_background) - tts_start_ms
        if len(tts_segment) > available_time_ms:
            print(f"TTS too long ({len(tts_segment)}ms), trimming to {available_time_ms}ms")
            tts_segment = tts_segment[:available_time_ms]
            

        # Miksowanie bez clippingu - overlay z odpowiednimi poziomami
        print(f"Overlaying TTS at position {tts_start_ms}ms")
        final_audio = extended_background.overlay(tts_segment, position=tts_start_ms)
        
        print(f"Final audio duration: {len(final_audio)}ms (~{len(final_audio)/60000:.1f} minutes)")
        
        # Eksport do bajtów
        print("Exporting final audio to MP3...")
        output_buffer = io.BytesIO()
        final_audio.export(output_buffer, format="mp3", bitrate="128k")
        
        result_bytes = output_buffer.getvalue()
        print(f"Final file size: {len(result_bytes)} bytes")
        
        return result_bytes
        
    except Exception as e:
        print(f"Błąd w create_extended_audio: {str(e)}")
        print("Falling back to simple audio extension...")
        # Fallback - używamy funkcji simple fallback
        return create_simple_extended_audio(tts_audio_bytes, sound_effect_bytes)

def test_audio_generation():
    """
    Funkcja testowa do debugowania problemów z generowaniem audio
    """
    print("=== TESTING AUDIO GENERATION ===")
    
    # Test 1: Sprawdź pydub
    print(f"1. pydub available: {PYDUB_AVAILABLE}")
    if PYDUB_AVAILABLE:
        try:
            from pydub.utils import which
            ffmpeg_path = which("ffmpeg")
            print(f"   ffmpeg path: {ffmpeg_path}")
        except Exception as e:
            print(f"   ffmpeg check error: {e}")
    
    # Test 2: Sprawdź klucze API
    print("2. API keys:")
    deepseek_key = os.getenv('DEEPSEEK_API_KEY')
    elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
    print(f"   DEEPSEEK_API_KEY: {'✓' if deepseek_key else '✗'}")
    print(f"   ELEVENLABS_API_KEY: {'✓' if elevenlabs_key else '✗'}")
    
    # Test 3: Sprawdź katalog audio
    audio_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'audio_files')
    print(f"3. Audio directory: {audio_dir}")
    print(f"   Exists: {os.path.exists(audio_dir)}")
    if os.path.exists(audio_dir):
        print(f"   Writable: {os.access(audio_dir, os.W_OK)}")
        files = [f for f in os.listdir(audio_dir) if f.endswith('.mp3')]
        print(f"   MP3 files: {len(files)}")
    
    # Test 4: Test prostego generowania
    if deepseek_key and elevenlabs_key:
        print("4. Testing simple generation...")
        try:
            result = generate_sound("test ocean waves", "peaceful beach")
            print(f"   Generation result: {result.get('status', 'unknown')}")
            if result.get('audio_files'):
                for file_type, file_path in result['audio_files'].items():
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        print(f"   {file_type}: {file_size} bytes")
                    else:
                        print(f"   {file_type}: FILE NOT FOUND")
        except Exception as e:
            print(f"   Generation test failed: {e}")
    else:
        print("4. Skipping generation test - missing API keys")

def cleanup_old_audio_files(max_age_hours=24):
    """
    Czyści stare pliki audio starsze niż max_age_hours

    Args:
        max_age_hours (int): Maksymalny wiek plików w godzinach
    """
    try:
        audio_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'audio_files')
        if not os.path.exists(audio_dir):
            return

        now = datetime.now().timestamp()
        max_age_seconds = max_age_hours * 3600

        cleaned_count = 0
        for filename in os.listdir(audio_dir):
            if filename.endswith('.mp3') and filename.startswith('dream_'):
                filepath = os.path.join(audio_dir, filename)
                file_age = now - os.path.getctime(filepath)

                if file_age > max_age_seconds:
                    try:
                        os.remove(filepath)
                        cleaned_count += 1
                        print(f"Removed old audio file: {filename}")
                    except Exception as e:
                        print(f"Error removing file {filename}: {e}")

        if cleaned_count > 0:
            print(f"Cleaned up {cleaned_count} old audio files")

    except Exception as e:
        print(f"Error during audio cleanup: {e}")

# Dodajmy możliwość uruchomienia testów bezpośrednio
if __name__ == "__main__":
    test_audio_generation()
