import pytest

from models import PcObject, UserOfferer
from repository.user_offerer_queries import find_user_offerer_email, find_first_by_user_id
from tests.conftest import clean_database
from utils.test_utils import create_user, create_offerer, create_user_offerer


@pytest.mark.standalone
@clean_database
def test_find_user_offerer_email(app):
    # Given
    user = create_user(email='offerer@email.com')
    offerer = create_offerer()
    user_offerer = create_user_offerer(user, offerer)
    PcObject.check_and_save(user_offerer)

    # When
    email = find_user_offerer_email(user_offerer.id)

    # Then
    assert email == 'offerer@email.com'


@pytest.mark.standalone
@clean_database
def test_find_first_by_user_id_should_return_one_user_offerers_with_user_id(app):
    # Given
    user = create_user(email='offerer@email.com')
    offerer1 = create_offerer(siren='123456789')
    offerer2 = create_offerer(siren='987654321')
    offerer3 = create_offerer(siren='123456780')
    user_offerer1 = create_user_offerer(user, offerer1)
    user_offerer2 = create_user_offerer(user, offerer2)
    PcObject.check_and_save(user_offerer1, user_offerer2, offerer3)

    # When
    first_user_offerer = find_first_by_user_id(user.id)

    # Then
    assert type(first_user_offerer) == UserOfferer
    assert first_user_offerer == user_offerer1 or first_user_offerer == user_offerer2
