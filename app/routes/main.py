from flask import Blueprint, jsonify
from app.models import get_test

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    # get_test() already executes the SQL and returns a dict (or {}).
    # The previous code called `text(get_test())` which referenced
    # sqlalchemy.text (imported in models) and caused a TypeError
    # because a dict was being passed to sqlalchemy.text().
    result = get_test()
    # Return the actual result (get_test already returns a dict or {}).
    # jsonify will convert the dict to a JSON response.
    return jsonify("Hello")
