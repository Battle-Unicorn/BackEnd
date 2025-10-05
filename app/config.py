from dotenv import load_dotenv
import os
import warnings

# Load variables from a .env file (if present). This keeps secrets out of source files.
load_dotenv()


class Config:
    # Read DB credentials from environment (or from Docker Compose POSTGRES_* vars).
    # No hard-coded secrets in this file; if values are missing we'll warn and fall back to
    # insecure defaults for development only.
    DB_USER = os.getenv('DB_USER') or os.getenv('POSTGRES_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD') or os.getenv('POSTGRES_PASSWORD')
    DB_HOST = os.getenv('DB_HOST') or 'db'
    DB_PORT = os.getenv('DB_PORT') or os.getenv('POSTGRES_PORT') or '5432'
    DB_NAME = os.getenv('DB_NAME') or os.getenv('POSTGRES_DB') or 'hackyeah'

    if not DB_USER or not DB_PASSWORD:
        warnings.warn(
            "Database credentials not found in environment; falling back to insecure development defaults."
        )
        DB_USER = DB_USER or 'admin'
        DB_PASSWORD = DB_PASSWORD or 'admin1'

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv('FLASK_SECRET_KEY') or os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        warnings.warn("FLASK_SECRET_KEY/SECRET_KEY not set in environment; using insecure dev key.")
        SECRET_KEY = 'dev-secret'

    # AI API Keys
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
    
    if not DEEPSEEK_API_KEY:
        warnings.warn("DEEPSEEK_API_KEY not set in environment; AI text generation will not work.")
    if not ELEVENLABS_API_KEY:
        warnings.warn("ELEVENLABS_API_KEY not set in environment; audio generation will be limited to text only.")

    # Set to True to use local vendor files, False to use CDN
    USE_LOCAL_FILES = True
