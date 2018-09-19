import pytest

from models import PcObject
from repository.user_offerer_queries import find_user_offerer_email
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