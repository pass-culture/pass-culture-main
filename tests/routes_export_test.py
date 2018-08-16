import os

import pytest

from models import PcObject
from tests.conftest import clean_database

TOKEN = os.environ.get('EXPORT_TOKEN')

@pytest.mark.standalone
@clean_database
def test_export_model_returns_200_when_given_model_is_known(app):
    # given
    user = create_user(password='p@55sw0rd')
    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    # when
    response = auth_request.get(API_URL + '/export/%s?token=%s' % ('Venue', TOKEN))

    # then
    assert response.status_code == 200


@pytest.mark.standalone
@clean_database
def test_export_model_returns_400_when_given_model_is_not_exportable(app):
    # given
    user = create_user(password='p@55sw0rd')
    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    # when
    response = auth_request.get(API_URL + '/export/%s?token=%s' % ('VersionedMixin', TOKEN))

    # then
    assert response.status_code == 400
    assert response.json()['global'] == ['Classe non exportable : VersionedMixin']
import pytest

from tests.conftest import clean_database
from utils.test_utils import API_URL, req_with_auth, create_user


@pytest.mark.standalone
@clean_database
def test_get_users_per_department_returns_the_user_count_by_department_code_as_csv_file(app):
    # given
    user = create_user(email='user0@test.com', password='azerty123', departement_code='93')
    user.save()
    auth_request = req_with_auth(email=user.email, password='azerty123')

    create_user(email='user1@test.com', departement_code='93').save()
    create_user(email='user2@test.com', departement_code='75').save()
    create_user(email='user3@test.com', departement_code='93').save()
    create_user(email='user4@test.com', departement_code='34').save()
    create_user(email='user5@test.com', departement_code='34').save()

    # when
    response = auth_request.get(API_URL + '/export/users_per_department')

    # then
    assert response.status_code == 200
    assert response.content == b'departement_code,nb_users\r\n' \
                               b'93,3\r\n' \
                               b'34,2\r\n' \
                               b'75,1\r\n'


def test_export_model_returns_400_when_given_model_is_unknown(app):
    # given
    user = create_user(password='p@55sw0rd')
    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    # when
    response = auth_request.get(API_URL + '/export/%s?token=%s' % ('RandomStuff', TOKEN))

    # then
    assert response.status_code == 400
    assert response.json()['global'] == ['Classe inconnue : RandomStuff']
