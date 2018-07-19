import os
import pytest
from flask import Flask
from models.db import db
import models

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

        app.model = {}
        for model_name in models.__all__:
            app.model[model_name] = getattr(models, model_name)

    return app
