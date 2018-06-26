import pytest
from flask import Flask

@pytest.fixture(scope='session')
def app():
    app = Flask(__name__)
    with app.app_context():
        import models
        import local_providers
    return app
