from flask import Blueprint, jsonify, request
#

embedded_bp = Blueprint('embedded', __name__)


@embedded_bp.route('/embedded/hello')
def embedded_helo():
    return jsonify("Hello from embedded")

@embedded_bp.route('/embedded/data', methods=['POST'])
def embedded_data():
    data = request.get_json()
    # Parsujemy i analizujemy dane żeby zapisać w sesji na ich podstawie czy użytkownik śpi i jest w fazie rem
    # Zapisujemy je w sesji żeby móc odpowiedzieć na ping aplikacji mobilnej i odpowiedzieć flagą
    print(data)
    return jsonify({"status": "success","device_id": "Dev_001", "timestamp": "2025-09-24T23:45:12Z"})
