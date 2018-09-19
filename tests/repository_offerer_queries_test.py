import pytest

from models import PcObject
from repository.offerer_queries import find_all_admin_offerer_emails
from tests.conftest import clean_database
from utils.test_utils import create_user, create_offerer, create_user_offerer


@pytest.mark.standalone
@clean_database
def test_find_all_admin_offerer_emails(app):
    # Given
    offerer = create_offerer()
    user_admin1 = create_user(email='admin1@offerer.com')
    user_admin2 = create_user(email='admin2@offerer.com')
    user_editor = create_user(email='editor@offerer.com')
    user_random = create_user(email='random@user.com')
    user_offerer_admin1 = create_user_offerer(user_admin1, offerer, is_admin=True)
    user_offerer_admin2 = create_user_offerer(user_admin2, offerer, is_admin=True)
    user_offerer_editor = create_user_offerer(user_editor, offerer, is_admin=False)
    PcObject.check_and_save(user_random, user_offerer_admin1, user_offerer_admin2, user_offerer_editor)

    # When
    emails = find_all_admin_offerer_emails(offerer.id)

    # Then
    assert set(emails) == {'admin1@offerer.com', 'admin2@offerer.com'}
    assert type(emails) == list
