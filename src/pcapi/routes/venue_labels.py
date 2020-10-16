from flask import jsonify
from flask_login import login_required

from pcapi.flask_app import private_api
from pcapi.infrastructure.container import get_venue_labels
from pcapi.routes.serialization.venue_labels_serialize import serialize_venue_label


@private_api.route('/venue-labels', methods=['GET'])
@login_required
def fetch_venue_labels():
    venue_labels = get_venue_labels.execute()
    return jsonify([serialize_venue_label(venue_label) for venue_label in venue_labels]), 200
