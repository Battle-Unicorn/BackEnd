from flask import Blueprint, jsonify
from app.models import get_test

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    result = get_test()
    return jsonify(result)
