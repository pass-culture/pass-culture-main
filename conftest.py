import pytest
from flask import Flask

from models import *
from models.db import db


@pytest.fixture(scope='session')
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    app.model = {
        'Booking': Booking,
        'Event': Event,
        'EventOccurence': EventOccurence,
        'Mediation': Mediation,
        'Offer': Offer,
        'Offerer': Offerer,
        'VenueProvider': VenueProvider,
        'LocalProviderEvent': LocalProviderEvent,
        'LocalProvider': LocalProvider,
        'Occasion': Occasion,
        'Provider': Provider,
        'Recommendation': Recommendation,
        'Thing': Thing,
        'UserOfferer': UserOfferer,
        'User': User,
        'Venue': Venue
    }

    with app.app_context():
        import models
        import local_providers
    return app
