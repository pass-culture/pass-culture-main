from flask import current_app as app
from flask import jsonify
from flask_login import login_required

from repository.venue_labels_queries import get_all_venue_labels
from routes.serialization import as_dict
from use_cases.get_venue_labels import get_venue_labels


@app.route('/venue-labels', methods=['GET'])
@login_required
def fetch_venue_labels():
    venue_labels = get_venue_labels(get_all_venue_labels)
    return jsonify([as_dict(label) for label in venue_labels]), 200
