from flask import Blueprint, jsonify, request
from ..rem_detection import rem_detection

embedded_bp = Blueprint('embedded', __name__)


@embedded_bp.route('/embedded/hello')
def embedded_helo():
    return jsonify("Hello from embedded")

@embedded_bp.route('/embedded/data', methods=['POST'])
def embedded_data():
    data = request.get_json()
    # Parsujemy i analizujemy dane żeby zapisać w sesji na ich podstawie czy użytkownik śpi i jest w fazie rem
    # Zapisujemy je w sesji żeby móc odpowiedzieć na ping aplikacji mobilnej i odpowiedzieć flagą

    # WARUNKI DLA N_REM:
    # - HR - jest zwolnione
    # - HR - jest stabilne (można sprawdzić za pomocą HRV)
    # - HRV - Oddechy są równe
    # - HRV - Oddechy są długie
    # - RR - Na jego podstawie określamy czy długość oddechu jest dłuższa niż normalnie

    # WARUNKI DO ZMIERZENIA 
    # Sprawdzamy średni HR z ostatnich 15 minut - jeśli w ciągu ostatniej pół minuty wzrosło o daną wartość - flaga rem true
    print(data)
    return jsonify({"status": "success","device_id": "Dev_001", "timestamp": "2025-09-24T23:45:12Z"})
