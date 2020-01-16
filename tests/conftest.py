import os
from functools import wraps
from pprint import pprint
from unittest.mock import Mock

import pytest
from flask import Flask, jsonify
from flask.testing import FlaskClient
from flask_login import LoginManager, login_user
from mailjet_rest import Client
from requests import Response
from requests.auth import _basic_auth_str

from local_providers.install import install_local_providers
from models.db import db
from models.install import install_models, install_database_extensions, install_materialized_views
from repository.clean_database import clean_all_database
from repository.user_queries import find_user_by_email
from routes import install_routes
from tests.model_creators.generic_creators import PLAIN_DEFAULT_TESTING_PASSWORD
from utils.json_encoder import EnumJSONEncoder


def pytest_configure(config):
    if config.getoption('capture') == 'no':
        TestClient.WITH_DOC = True


@pytest.fixture(scope='session')
def app():
    app = Flask(__name__, template_folder='../templates')

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL_TEST')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = '@##&6cweafhv3426445'
    app.config['REMEMBER_COOKIE_HTTPONLY'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = False
    app.config['TESTING'] = True
    app.url_map.strict_slashes = False
    app.json_encoder = EnumJSONEncoder

    login_manager = LoginManager()
    login_manager.init_app(app)
    db.init_app(app)

    app.app_context().push()
    install_database_extensions()
    install_models()
    install_materialized_views()
    install_routes()
    install_local_providers()
    app.mailjet_client = Mock()
    app.redis_client = Mock()

    @app.route('/test/signin', methods=['POST'])
    def test_signin():
        from flask import request
        identifier = request.get_json().get("identifier")
        user = find_user_by_email(identifier)
        login_user(user, remember=True)
        return jsonify({}), 204

    return app


def mocked_mail(f):
    @wraps(f)
    def decorated_function(app, *args, **kwargs):
        app.mailjet_client = Mock(spec=Client)
        app.mailjet_client.send = Mock()
        return f(app, *args, **kwargs)

    return decorated_function


def clean_database(f: object) -> object:
    @wraps(f)
    def decorated_function(*args, **kwargs):
        db.session.rollback()
        clean_all_database()
        return f(*args, **kwargs)

    return decorated_function


class TestClient:
    WITH_DOC = False
    USER_TEST_ADMIN_EMAIL = "pctest.admin93.0@btmx.fr"
    LOCAL_ORIGIN_HEADER = {'origin': 'http://localhost:3000'}

    def __init__(self, client: FlaskClient):
        self.client = client
        self.auth_header = {}

    def with_auth(self, email: str = None):
        self.email = email
        if email is None:
            self.auth_header = {
                'Authorization': _basic_auth_str(TestClient.USER_TEST_ADMIN_EMAIL, PLAIN_DEFAULT_TESTING_PASSWORD),
            }
        else:
            self.auth_header = {
                'Authorization': _basic_auth_str(email, PLAIN_DEFAULT_TESTING_PASSWORD),
            }

        return self

    def delete(self, route: str, headers=LOCAL_ORIGIN_HEADER):
        result = self.client.delete(route, headers={**self.auth_header, **headers})
        self._print_spec('DELETE', route, None, result)
        return result

    def get(self, route: str, headers=LOCAL_ORIGIN_HEADER):
        result = self.client.get(route, headers={**self.auth_header, **headers})
        self._print_spec('GET', route, None, result)
        return result

    def post(self, route: str, json: dict = None, form: dict = None, files: dict = None, headers=LOCAL_ORIGIN_HEADER):
        if form or files:
            result = self.client.post(route, data=form if form else files, headers={**self.auth_header, **headers})
        else:
            result = self.client.post(route, json=json, headers={**self.auth_header, **headers})

        self._print_spec('POST', route, json, result)
        return result

    def patch(self, route: str, json: dict = None, headers=LOCAL_ORIGIN_HEADER):
        result = self.client.patch(route, json=json, headers={**self.auth_header, **headers})
        self._print_spec('PATCH', route, json, result)
        return result

    def put(self, route: str, json: dict = None, headers=LOCAL_ORIGIN_HEADER):
        result = self.client.put(route, json=json, headers={**self.auth_header, **headers})
        self._print_spec('PUT', route, json, result)
        return result

    def _print_spec(self, verb: str, route: str, request_body: dict, result: Response):
        if not TestClient.WITH_DOC:
            return

        print('\n===========================================')
        print('%s :: %s' % (verb, route))
        print('STATUS CODE :: %s' % result.status_code)

        if request_body:
            print('REQUEST BODY')
            pprint(request_body)

        if result.data:
            print('RESPONSE BODY')
            pprint(result.json)

        print('===========================================\n')
