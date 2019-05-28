""" routes offerer """

import pytest

from models import PcObject
from tests.conftest import clean_database
from utils.human_ids import humanize
from tests.test_utils import create_user, \
    create_user_offerer, \
    req_with_auth, create_offerer, API_URL


@pytest.mark.standalone
@clean_database
def test_get_user_offerer_should_return_only_user_offerer_from_current_user(app):
    # given
    user1 = create_user(email='patrick.fiori@test.com')
    user2 = create_user(email='celine.dion@test.com')
    offerer = create_offerer(siren='123456781')
    user_offerer1 = create_user_offerer(user1, offerer)
    user_offerer2 = create_user_offerer(user2, offerer)
    PcObject.save(user_offerer1, user_offerer2)

    # assert
    assert len(offerer.UserOfferers) == 2

    # when
    auth_request = req_with_auth(email=user1.email)
    url = API_URL + '/userOfferers/' + humanize(offerer.id)
    response = auth_request.get(url)

    # then
    assert response.status_code == 200
    assert response.json()[0]['userId'] == humanize(user1.id)
