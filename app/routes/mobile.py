from flask import Blueprint, jsonify
from app.models import get_test

mobile_bp = Blueprint('mobile', __name__)


@mobile_bp.route('/mobile/hello')
def mobile_hello():
    return jsonify("Hello from mobile")
