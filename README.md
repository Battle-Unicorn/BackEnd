# HackYeah25 - Dream Audio Generation System

System generujący personalizowane dźwięki do świadomych snów, stworzony na **HackYeah 2025** 🦄  

## ⚙️ Wymagania
- Docker + Docker Compose
- Python 3.11+ (dla lokalnego uruchomienia)
- Klucze API:
  - DEEPSEEK_API_KEY → https://platform.deepseek.com
  - ELEVENLABS_API_KEY → https://elevenlabs.io

## 🚀 Szybki start (Docker – zalecane)
```bash
git clone https://github.com/Battle-Unicorn/BackEnd.git
cd BackEnd
cp .env.example .env
# edytuj .env i dodaj swoje klucze API
docker-compose up --build
```
Dostępne po starcie:
- API → http://localhost:8080
- Adminer → http://localhost:5050

## 💻 Uruchomienie lokalne
```bash
git clone https://github.com/Battle-Unicorn/BackEnd.git
cd BackEnd
python -m venv venv
source venv/bin/activate   # Linux/Mac
# lub venv\Scripts\activate  # Windows
pip install -r requirements.txt
docker run --name hackyeah-db -e POSTGRES_DB=hackyeah -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=admin1 -p 5432:5432 -d postgres:15
python run.py
```

## 🧪 Testy
```bash
python -m pytest tests/ -v
```

## 🆘 Problemy
- Brak kluczy API → sprawdź .env
- Baza nie działa → docker ps | grep postgres
- Brak dźwięków → sprawdź audio_files/ i logi API

**Team Battle-Unicorn 💫 | HackYeah 2025 🦄**
