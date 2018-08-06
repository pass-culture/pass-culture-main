import os
from functools import wraps
from unittest.mock import Mock

import pytest
from flask import Flask
from mailjet_rest import Client

from models import User, Deposit, Booking, Mediation, Recommendation, UserOfferer
from models.db import db

items_by_category = {'first': [], 'last': []}


def _sort_alphabetically(category):
    return sorted(items_by_category[category], key=lambda item: item.location)


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

    with app.app_context():
        import models.install
        import local_providers
        app.mailjet_client = Mock(spec=Client)
        app.mailjet_client.send = Mock()

        app.model = {}
        for model_name in models.__all__:
            app.model[model_name] = getattr(models, model_name)

    return app


def clean_database(f):
    @wraps(f)
    def decorated_function(app, *args, **kwargs):
        """ Order of deletions matters because of foreign key constraints """
        UserOfferer.query.delete()
        Booking.query.delete()
        Recommendation.query.delete()
        Mediation.query.delete()
        Deposit.query.delete()
        User.query.delete()
        return f(app, *args, **kwargs)

    return decorated_function
