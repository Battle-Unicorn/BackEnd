from flask import Blueprint, jsonify

embedded_bp = Blueprint('embedded', __name__)


@embedded_bp.route('/embedded/hello')
def embedded_helo():
    return jsonify("Hello from embedded")
