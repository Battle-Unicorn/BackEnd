from flask import Flask
from flask_cors import CORS
from .routes import main_bp, mobile_bp, embedded_bp
from .models import db
from .config import Config

def create_app():

    app = Flask(__name__)  # Utworzenie nowej instancji Flask
    # CORS konfiguracja - pozwalamy na wszystkie origins dla development
    CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
         allow_headers=["Content-Type", "Authorization"])
    app.config.from_object(Config)  # Załadowanie konfiguracji z klasy Config

    db.init_app(app)  # Inicjalizacja bazy danych
    app.register_blueprint(main_bp)
    app.register_blueprint(embedded_bp)
    app.register_blueprint(mobile_bp)

    return app
