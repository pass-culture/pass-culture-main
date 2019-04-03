"""events"""
from flask import current_app as app, jsonify

from models import Product
from utils.includes import EVENT_INCLUDES
from utils.rest import load_or_404, \
    login_or_api_key_required


@app.route('/events/<id>', methods=['GET'])
@login_or_api_key_required
def get_event(id):
    event = load_or_404(Product, id)
    return jsonify(
        event._asdict(include=EVENT_INCLUDES)
    ), 200
