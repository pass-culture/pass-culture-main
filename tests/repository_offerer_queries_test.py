import secrets

import pytest

from models import PcObject
from repository.offerer_queries import find_all_admin_offerer_emails, find_all_offerers_with_managing_user_information, \
     find_all_offerers_with_managing_user_information_and_venue, find_all_offerers_with_managing_user_information_and_not_virtual_venue, find_all_offerers_with_venue
from tests.conftest import clean_database
from utils.test_utils import create_user, create_offerer, create_user_offerer, create_venue


@pytest.mark.standalone
@clean_database
def test_find_all_admin_offerer_emails(app):
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
    emails = find_all_admin_offerer_emails(offerer.id)

    # Then
    assert set(emails) == {'admin1@offerer.com', 'admin2@offerer.com'}
    assert type(emails) == list

@pytest.mark.standalone
@clean_database
def test_find_all_offerers_with_managing_user_information(app):
    #given
    user_admin1 = create_user(email='admin1@offerer.com')
    user_admin2 = create_user(email='admin2@offerer.com')
    user_editor1 =  create_user(email='editor1@offerer.com')
    offerer1 = create_offerer(name='offerer1')
    offerer2 = create_offerer(name='offerer2', siren='789456123')
    user_offerer1 = create_user_offerer(user_admin1, offerer1, is_admin=True)
    user_offerer2 = create_user_offerer(user_editor1, offerer1, is_admin=False)
    user_offerer3 = create_user_offerer(user_admin1, offerer2, is_admin=True)
    user_offerer4 = create_user_offerer(user_admin2, offerer2, is_admin=True)
    PcObject.check_and_save(user_admin1, user_admin2, user_editor1, offerer1, offerer2, user_offerer1, user_offerer2, user_offerer3, user_offerer4)

    #when
    offerers = find_all_offerers_with_managing_user_information()

    #then
    assert len(offerers) == 4
    assert len(offerers[0]) == 10
    assert offerer1.siren in offerers[1].siren
    assert user_admin2.email in offerers[3].email

@pytest.mark.standalone
@clean_database
def test_find_all_offerers_with_managing_user_information_and_venue(app):
    #given
    user_admin1 = create_user(email='admin1@offerer.com')
    user_admin2 = create_user(email='admin2@offerer.com')
    user_editor1 =  create_user(email='editor1@offerer.com')
    offerer1 = create_offerer(name='offerer1')
    offerer2 = create_offerer(name='offerer2', siren='789456123')
    venue1 = create_venue(offerer1, siret='123456789abcde')
    venue2 = create_venue(offerer2, siret='123456789abcdf')
    venue3 = create_venue(offerer2, siret='123456789abcdg', booking_email='test@test.test')
    user_offerer1 = create_user_offerer(user_admin1, offerer1, is_admin=True)
    user_offerer2 = create_user_offerer(user_editor1, offerer1, is_admin=False)
    user_offerer3 = create_user_offerer(user_admin1, offerer2, is_admin=True)
    user_offerer4 = create_user_offerer(user_admin2, offerer2, is_admin=True)
    PcObject.check_and_save(user_admin1, user_admin2, user_editor1, offerer1, offerer2, venue1, venue2, venue3,  user_offerer1, user_offerer2, user_offerer3, user_offerer4)

    #when
    offerers = find_all_offerers_with_managing_user_information_and_venue()

    #then
    assert len(offerers) == 6
    assert len(offerers[0]) == 13
    assert offerer1.city in offerers[0].city
    assert offerer2.siren == offerers[2].siren
    assert offerer2.siren == offerers[3].siren


@pytest.mark.standalone
@clean_database
def test_find_all_offerers_with_managing_user_information_and_not_virtual_venue(app):
    #given
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
    PcObject.check_and_save(user_admin1, user_admin2, offerer1, offerer2, venue1, venue2, venue3,  user_offerer1, user_offerer3, user_offerer4)

    #when
    offerers = find_all_offerers_with_managing_user_information_and_not_virtual_venue()

    #then
    assert len(offerers) == 2
    assert len(offerers[0]) == 13
    assert user_admin1.email in offerers[0].email
    assert user_admin2.email in offerers[1].email
    assert offerer2.siren == offerers[1].siren


@pytest.mark.standalone
@clean_database
def test_find_all_offerers_with_venue(app):
    #given
    offerer1 = create_offerer(name='offerer1')
    offerer2 = create_offerer(name='offerer2', siren='789456123')
    venue1 = create_venue(offerer1, is_virtual=True, siret=None)
    venue2 = create_venue(offerer2, is_virtual=True, siret=None, booking_email='test@test.test')
    venue3 = create_venue(offerer2, is_virtual=False)
    PcObject.check_and_save(offerer1, offerer2, venue1, venue2, venue3)

    #when
    offerers = find_all_offerers_with_venue()

    #then
    assert len(offerers) == 3
    assert len(offerers[0]) == 7
    assert offerer1.id == offerers[0][0]
    assert venue2.bookingEmail in offerers[1].bookingEmail
    assert venue1.bookingEmail in offerers[0].bookingEmail
    