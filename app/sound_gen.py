import os
from datetime import datetime
from openai import OpenAI
from elevenlabs.client import ElevenLabs
import json

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

        1. TEKST_TTS: Krótki, uspokajający tekst (2-3 zdania) po polsku, który pomoże osobie śniącej uświadomić sobie, że śni. Tekst powinien być łagodny i pomocny w osiągnięciu świadomego snu.

        2. OPIS_DZWIEKU: Opis łagodnej, relaksacyjnej muzyki/dźwięków w tle (1-2 zdania po angielsku), która pasuje do scenariusza snu.

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
                    "sound_description": f"Gentle ambient sounds related to {key_words} in {place}, soft and peaceful background music"
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
            "sound_description": f"Peaceful ambient sounds with gentle music, related to {key_words}"
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
        tts_audio = client.text_to_speech.convert(
            text=scenario_result["tts_text"],
            voice_id="EXAVITQu4vr4xnSDxMaL",  # Bella - łagodny głos
            model_id="eleven_multilingual_v2"
        )
        
        # Generowanie sound effect - dla efektów dźwiękowych użyjemy sound generation API
        sound_effect = client.text_to_speech.convert(
            text=scenario_result["sound_description"], 
            voice_id="EXAVITQu4vr4xnSDxMaL",  # Ten sam głos
            model_id="eleven_multilingual_v2"
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
        
        # TTS file
        tts_filename = f"dream_tts_{timestamp}.mp3"
        tts_filepath = os.path.join(audio_dir, tts_filename)
        with open(tts_filepath, "wb") as f:
            for chunk in tts_audio:
                f.write(chunk)
        audio_files["tts_file"] = tts_filepath
        
        # Sound effect file  
        sound_filename = f"dream_sound_{timestamp}.mp3"
        sound_filepath = os.path.join(audio_dir, sound_filename)
        with open(sound_filepath, "wb") as f:
            for chunk in sound_effect:
                f.write(chunk)
        audio_files["sound_file"] = sound_filepath
        
        print(f"Audio files generated: {audio_files}")
        
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
