import os
import pytest
from flask import Flask
from models.db import db
from unittest.mock import patch, Mock
from mailjet_rest import Client

from utils.mailing import MAILJET_API_KEY, MAILJET_API_SECRET


@pytest.fixture(scope='session')
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        import models
        import models.install
        import local_providers
        client = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET),
                        version='v3')

        app.mailjet_client = Mock(spec=Client)
        app.mailjet_client.send = Mock()

        app.model = {}
        for model_name in models.__all__:
            app.model[model_name] = getattr(models, model_name)

    return app
