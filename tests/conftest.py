import os
from functools import wraps
from pprint import pprint
from unittest.mock import Mock

import pytest
import requests
from flask import Flask
from mailjet_rest import Client
from requests import Response

from models.db import db
from repository.clean_database import clean_all_database
from tests.test_utils import PLAIN_DEFAULT_TESTING_PASSWORD

items_by_category = {'first': [], 'last': []}


def _sort_alphabetically(category):
    return sorted(items_by_category[category], key=lambda item: item.location)


def pytest_configure(config):
    if config.getoption('capture') == 'no':
        TestClient.WITH_DOC = True


def pytest_collection_modifyitems(config, items):
    """
    This function can be deleted once the tests are truly order-independent.
    :param items: Test items parsed by pytest, available for sorting
    """

    for item in items:
        if 'standalone' in item.keywords:
            items_by_category['last'].append(item)
        else:
            items_by_category['first'].append(item)

    print('\n************************************************************')
    print('*                                                          *')
    print('*  %s tests are still depending on the execution order     *' % len(items_by_category['first']))
    print('*                                                          *')
    print('************************************************************')
    items[:] = _sort_alphabetically('first') + _sort_alphabetically('last')


@pytest.fixture(scope='session')
def app():
    app = Flask(__name__, template_folder='../templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app


def mocked_mail(f):
    @wraps(f)
    def decorated_function(app, *args, **kwargs):
        app.mailjet_client = Mock(spec=Client)
        app.mailjet_client.send = Mock()
        return f(app, *args, **kwargs)

    return decorated_function


def clean_database(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        clean_all_database()
        return f(*args, **kwargs)

    return decorated_function


class TestClient:
    WITH_DOC = False
    USER_TEST_ADMIN_EMAIL = "pctest.admin93.0@btmx.fr"
    LOCAL_ORIGIN_HEADER = {'origin': 'http://localhost:3000'}

    def __init__(self):
        self.session = None

    def with_auth(self, email: str = None, headers: dict = LOCAL_ORIGIN_HEADER):
        self.session = requests.Session()
        self.session.headers = headers

        if email is None:
            self.session.auth = (TestClient.USER_TEST_ADMIN_EMAIL, PLAIN_DEFAULT_TESTING_PASSWORD)
        else:
            self.session.auth = (email, PLAIN_DEFAULT_TESTING_PASSWORD)

        return self

    def delete(self, route: str, headers=LOCAL_ORIGIN_HEADER):
        if self.session:
            result = self.session.delete(route, headers=headers)
        else:
            result = requests.delete(route, headers=headers)

        if TestClient.WITH_DOC:
            self._print_spec('DELETE', route, None, result)

        return result

    def get(self, route: str, headers=LOCAL_ORIGIN_HEADER):
        if self.session:
            result = self.session.get(route, headers=headers)
        else:
            result = requests.get(route, headers=headers)

        if TestClient.WITH_DOC:
            self._print_spec('GET', route, None, result)

        return result

    def post(self, route: str, json: dict = None, headers=LOCAL_ORIGIN_HEADER):
        if self.session:
            result = self.session.post(route, json=json, headers=headers)
        else:
            result = requests.post(route, json=json, headers=headers)

        if TestClient.WITH_DOC:
            self._print_spec('POST', route, json, result)

        return result

    def patch(self, route: str, json: dict = None, headers=LOCAL_ORIGIN_HEADER):
        if self.session:
            result = self.session.patch(route, json=json, headers=headers)
        else:
            result = requests.patch(route, json=json, headers=headers)

        if TestClient.WITH_DOC:
            self._print_spec('PATCH', route, json, result)

        return result

    def put(self, route: str, json: dict = None, headers=LOCAL_ORIGIN_HEADER):
        if self.session:
            result = self.session.put(route, json=json, headers=headers)
        else:
            result = requests.put(route, json=json, headers=headers)

        if TestClient.WITH_DOC:
            self._print_spec('PUT', route, json, result)

        return result

    def _print_spec(self, verb: str, route: str, request_body: dict, result: Response):
        print('\n===========================================')
        print('%s :: %s' % (verb, route))
        print('STATUS CODE :: %s' % result.status_code)

        if request_body:
            print('REQUEST BODY')
            pprint(request_body)

        if result.content:
            print('RESPONSE BODY')
            pprint(result.json())

        print('===========================================\n')
