import secrets

import pytest

from models import PcObject
from repository.offerer_queries import find_all_offerers_with_managing_user_information, \
    find_all_offerers_with_managing_user_information_and_venue, \
    find_all_offerers_with_managing_user_information_and_not_virtual_venue, \
    find_all_offerers_with_venue, find_first_by_user_offerer_id, find_all_pending_validation
from tests.conftest import clean_database
from utils.test_utils import create_user, create_offerer, create_user_offerer, create_venue


@pytest.mark.standalone
@clean_database
def test_find_all_emails_of_user_offerers_admins_returns_list_of_user_emails_having_user_offerer_with_admin_rights_on_offerer(
        app):
    # Given
    offerer = create_offerer()
    user_admin1 = create_user(email='admin1@offerer.com')
    user_admin2 = create_user(email='admin2@offerer.com')
    user_editor = create_user(email='editor@offerer.com')
    user_admin_not_validated = create_user(email='admin_not_validated@offerer.com')
    user_random = create_user(email='random@user.com')
    user_offerer_admin1 = create_user_offerer(user_admin1, offerer, is_admin=True)
    user_offerer_admin2 = create_user_offerer(user_admin2, offerer, is_admin=True)
    user_offerer_admin_not_validated = create_user_offerer(user_admin_not_validated, offerer,
                                                           validation_token=secrets.token_urlsafe(20), is_admin=True)
    user_offerer_editor = create_user_offerer(user_editor, offerer, is_admin=False)
    PcObject.check_and_save(user_random, user_offerer_admin1, user_offerer_admin2, user_offerer_admin_not_validated,
                            user_offerer_editor)

    # When
    emails = find_all_emails_of_user_offerers_admins(offerer.id)

    # Then
    assert set(emails) == {'admin1@offerer.com', 'admin2@offerer.com'}
    assert type(emails) == list


@pytest.mark.standalone
@clean_database
def test_find_all_offerers_with_managing_user_information(app):
    # given
    user_admin1 = create_user(email='admin1@offerer.com')
    user_admin2 = create_user(email='admin2@offerer.com')
    user_editor1 = create_user(email='editor1@offerer.com')
    offerer1 = create_offerer(name='offerer1')
    offerer2 = create_offerer(name='offerer2', siren='789456123')
    user_offerer1 = create_user_offerer(user_admin1, offerer1, is_admin=True)
    user_offerer2 = create_user_offerer(user_editor1, offerer1, is_admin=False)
    user_offerer3 = create_user_offerer(user_admin1, offerer2, is_admin=True)
    user_offerer4 = create_user_offerer(user_admin2, offerer2, is_admin=True)
    PcObject.check_and_save(user_admin1, user_admin2, user_editor1, offerer1, offerer2,
                            user_offerer1, user_offerer2, user_offerer3, user_offerer4)

    # when
    offerers = find_all_offerers_with_managing_user_information()

    # then
    assert len(offerers) == 4
    assert len(offerers[0]) == 10
    assert offerer1.siren in offerers[1].siren
    assert user_admin2.email in offerers[3].email


@pytest.mark.standalone
@clean_database
def test_find_all_offerers_with_managing_user_information_and_venue(app):
    # given
    user_admin1 = create_user(email='admin1@offerer.com')
    user_admin2 = create_user(email='admin2@offerer.com')
    user_editor1 = create_user(email='editor1@offerer.com')
    offerer1 = create_offerer(name='offerer1')
    offerer2 = create_offerer(name='offerer2', siren='789456123')
    venue1 = create_venue(offerer1, siret='123456789abcde')
    venue2 = create_venue(offerer2, siret='123456789abcdf')
    venue3 = create_venue(offerer2, siret='123456789abcdg', booking_email='test@test.test')
    user_offerer1 = create_user_offerer(user_admin1, offerer1, is_admin=True)
    user_offerer2 = create_user_offerer(user_editor1, offerer1, is_admin=False)
    user_offerer3 = create_user_offerer(user_admin1, offerer2, is_admin=True)
    user_offerer4 = create_user_offerer(user_admin2, offerer2, is_admin=True)
    PcObject.check_and_save(venue1, venue2, venue3, user_offerer1, user_offerer2, user_offerer3,
                            user_offerer4)

    # when
    offerers = find_all_offerers_with_managing_user_information_and_venue()

    # then
    assert len(offerers) == 6
    assert len(offerers[0]) == 13
    assert offerer1.city in offerers[0].city
    assert offerer2.siren == offerers[2].siren
    assert offerer2.siren == offerers[3].siren


@pytest.mark.standalone
@clean_database
def test_find_all_offerers_with_managing_user_information_and_not_virtual_venue(app):
    # given
    user_admin1 = create_user(email='admin1@offerer.com')
    user_admin2 = create_user(email='admin2@offerer.com')
    offerer1 = create_offerer(name='offerer1')
    offerer2 = create_offerer(name='offerer2', siren='789456123')
    venue1 = create_venue(offerer1, is_virtual=True, siret=None)
    venue2 = create_venue(offerer2, is_virtual=True, siret=None)
    venue3 = create_venue(offerer2, is_virtual=False)
    user_offerer1 = create_user_offerer(user_admin1, offerer1, is_admin=True)
    user_offerer3 = create_user_offerer(user_admin1, offerer2, is_admin=True)
    user_offerer4 = create_user_offerer(user_admin2, offerer2, is_admin=True)
    PcObject.check_and_save(venue1, venue2, venue3, user_offerer1, user_offerer3, user_offerer4)

    # when
    offerers = find_all_offerers_with_managing_user_information_and_not_virtual_venue()

    # then
    assert len(offerers) == 2
    assert len(offerers[0]) == 13
    assert user_admin1.email in offerers[0].email
    assert user_admin2.email in offerers[1].email
    assert offerer2.siren == offerers[1].siren


@pytest.mark.standalone
@clean_database
def test_find_all_offerers_with_venue(app):
    # given
    offerer1 = create_offerer(name='offerer1')
    offerer2 = create_offerer(name='offerer2', siren='789456123')
    venue1 = create_venue(offerer1, is_virtual=True, siret=None)
    venue2 = create_venue(offerer2, is_virtual=True, siret=None, booking_email='test@test.test')
    venue3 = create_venue(offerer2, is_virtual=False)
    PcObject.check_and_save(offerer1, offerer2, venue1, venue2, venue3)

    # when
    offerers = find_all_offerers_with_venue()

    # then
    assert len(offerers) == 3
    assert len(offerers[0]) == 7
    assert offerer1.id == offerers[0][0]
    assert venue2.bookingEmail in offerers[1].bookingEmail
    assert venue1.bookingEmail in offerers[0].bookingEmail


@pytest.mark.standalone
@clean_database
def test_get_all_pending_offerers_with_user_offerer(app):
    # given
    offerer1 = create_offerer(name='offerer1', validation_token="a_token")
    offerer2 = create_offerer(name='offerer2', siren='789456123', validation_token="some_token")
    offerer3 = create_offerer(name='offerer3', siren='789456124')
    offerer4 = create_offerer(name='offerer4', siren='789456125')
    user1 = create_user(email='1@offerer.com')
    user2 = create_user(email='2@offerer.com')
    user3 = create_user(email='3@offerer.com')
    user4 = create_user(email='4@offerer.com')
    user_offerer1 = create_user_offerer(user1, offerer1, validation_token="nice_token")
    user_offerer2 = create_user_offerer(user2, offerer2)
    user_offerer3 = create_user_offerer(user3, offerer3, validation_token="another_token")
    user_offerer4 = create_user_offerer(user4, offerer4)
    user_offerer5 = create_user_offerer(user3, offerer3, validation_token="what_a_token")

    PcObject.check_and_save(user_offerer1, user_offerer2, user_offerer3, user_offerer4)

    # when
    offerers = find_all_pending_validation()

    # then
    assert len(offerers) == 3
    assert offerers[0].validationToken == offerer1.validationToken
    assert offerers[0].UserOfferers[0].validationToken == user_offerer1.validationToken
    assert offerers[1].validationToken == offerer2.validationToken
    assert offerers[1].UserOfferers[0].validationToken == None
    assert offerers[2].validationToken == None
    assert offerers[2].UserOfferers[0].validationToken == user_offerer3.validationToken
    assert offerers[2].UserOfferers[1].validationToken == user_offerer5.validationToken
    assert offerer4 not in offerers


@pytest.mark.standalone
@clean_database
def test_find_first_by_user_offerer_id_returns_the_first_offerer_that_was_created(app):
    # given
    user = create_user()
    offerer1 = create_offerer(name='offerer1', siren='123456789')
    offerer2 = create_offerer(name='offerer2', siren='789456123')
    offerer3 = create_offerer(name='offerer2', siren='987654321')
    user_offerer1 = create_user_offerer(user, offerer1)
    user_offerer2 = create_user_offerer(user, offerer2)
    PcObject.check_and_save(user_offerer1, user_offerer2, offerer3)

    # when
    offerer = find_first_by_user_offerer_id(user_offerer1.id)

    # then
    assert offerer.id == offerer1.id
