from flask import Blueprint, jsonify, request
from app.models import *

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    result = get_test()
    return jsonify(result)

@main_bp.route('/add', methods=['POST'])
def add():
    try:
        data = request.get_json()
        content_value = data.get("content")

        if not content_value:
            return jsonify({"error": "Brak pola 'content' w JSONie"}), 400

        # Użycie Twojej funkcji do dodania rekordu
        result_message = add_record_to_test(content_value)

        return jsonify({"message": result_message, "content": content_value}), 201

    except Exception as e:
        print(f"Błąd podczas dodawania danych: {str(e)}")
        return jsonify({"error": f"Błąd podczas dodawania danych: {str(e)}"}), 500