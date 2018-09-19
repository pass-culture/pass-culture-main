import pytest

from models import ApiErrors, User, PcObject, RightsType
from tests.conftest import clean_database
from utils.test_utils import create_user, create_offerer, create_user_offerer


@clean_database
@pytest.mark.standalone
def test_cannot_create_admin_that_can_book(app):
    # Given
    user = create_user(can_book_free_offers=True, is_admin=True)

    # When
    with pytest.raises(ApiErrors):
        PcObject.check_and_save(user)


@clean_database
@pytest.mark.standalone
def test_user_has_no_editor_right_on_offerer_if_he_is_not_attached(app):
    # given
    offerer = create_offerer()
    user = create_user(is_admin=False)
    PcObject.check_and_save(offerer, user)

    # when
    has_rights = user.hasRights(RightsType.editor, offerer.id)

    # then
    assert has_rights is False


@clean_database
@pytest.mark.standalone
def test_user_has_editor_right_on_offerer_if_he_is_attached(app):
    # given
    offerer = create_offerer()
    user = create_user(is_admin=False)
    user_offerer = create_user_offerer(user, offerer)
    PcObject.check_and_save(user_offerer)

    # when
    has_rights = user.hasRights(RightsType.editor, offerer.id)

    # then
    assert has_rights is True


@clean_database
@pytest.mark.standalone
def test_user_has_no_editor_right_on_offerer_if_he_is_attached_but_not_validated_yet(app):
    # given
    offerer = create_offerer()
    user = create_user(email='bobby@test.com', is_admin=False)
    user_offerer = create_user_offerer(user, offerer, validation_token='AZEFRGTHRQFQ')
    PcObject.check_and_save(user_offerer)

    # when
    has_rights = user.hasRights(RightsType.editor, offerer.id)

    # then
    assert has_rights is False


@clean_database
@pytest.mark.standalone
def test_user_has_editor_right_on_offerer_if_he_is_not_attached_but_is_admin(app):
    # given
    offerer = create_offerer()
    user = create_user(can_book_free_offers=False, is_admin=True)
    PcObject.check_and_save(offerer, user)

    # when
    has_rights = user.hasRights(RightsType.editor, offerer.id)

    # then
    assert has_rights is True
