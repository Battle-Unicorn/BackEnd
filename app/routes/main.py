from flask import Blueprint, jsonify
from app.models import *

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return jsonify("Hello")

