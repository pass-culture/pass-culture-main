import pytest

from tests.conftest import clean_database
from utils.test_utils import API_URL, req, req_with_auth, create_user, create_offerer


@pytest.mark.standalone
def test_get_offerers_should_work_only_when_logged_in():
    # when
    response = req.get(API_URL + '/offerers')

    # then
    assert response.status_code == 401


@pytest.mark.standalone
@clean_database
def test_get_offerers_should_return_a_list_of_offerers(app):
    # given
    offerer = create_offerer()
    offerer.save()

    user = create_user(password='p@55sw0rd')
    user.offerers = [offerer]
    user.save()

    # when
    response = req_with_auth(email=user.email, password='p@55sw0rd').get(API_URL + '/offerers')

    # then
    assert response.status_code == 200
    assert len(response.json()) > 0
