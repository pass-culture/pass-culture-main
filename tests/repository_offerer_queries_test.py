import secrets

import pytest

from datetime import datetime, timedelta
from models import PcObject
from repository.offerer_queries import find_all_offerers_with_managing_user_information, \
    find_all_offerers_with_managing_user_information_and_venue, \
    find_all_offerers_with_managing_user_information_and_not_virtual_venue, \
    find_all_offerers_with_venue, find_first_by_user_offerer_id, find_all_pending_validation, \
    find_filtered_offerers 
from repository.user_queries import find_all_emails_of_user_offerers_admins
from tests.conftest import clean_database
from utils.test_utils import create_user, create_offerer, create_user_offerer, create_venue, \
    create_offerer_activity, create_event_offer, create_thing_offer, create_event_occurrence, \
    create_stock_with_thing_offer, create_stock_from_event_occurrence, save_all_activities 


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



@pytest.mark.standalone
@clean_database
def test_find_filtered_offerers_with_dpt_param_return_filtered_offerers(app):
    # Given
    offerer_93 = create_offerer(postal_code="93125") 
    offerer_67 = create_offerer(postal_code="67000", siren="123456781")
    offerer_34 = create_offerer(postal_code="34758", siren="123456782")

    PcObject.check_and_save(offerer_93, offerer_67, offerer_34)

    # When
    query_with_dpt = find_filtered_offerers(dpt=['93','67'])

    # Then
    assert offerer_93 in query_with_dpt
    assert offerer_67 in query_with_dpt
    assert offerer_34 not in query_with_dpt


@pytest.mark.standalone
@clean_database
def test_find_filtered_offerers_with_zipcodes_param_return_filtered_offerers(app):
    # Given
    offerer_93125 = create_offerer(postal_code="93125") 
    offerer_67000 = create_offerer(postal_code="67000", siren="123456781")
    offerer_34758 = create_offerer(postal_code="34758", siren="123456782")

    PcObject.check_and_save(offerer_93125, offerer_67000, offerer_34758)

    # When
    query_with_zipcodes = find_filtered_offerers(zip_codes=['93125', '34758'])

    # Then
    assert offerer_93125 in query_with_dpt
    assert offerer_67000 in query_with_dpt
    assert offerer_34758 not in query_with_dpt


@pytest.mark.standalone
@clean_database
def test_find_filtered_offerers_with_date_params_return_filtered_offerers(app):
    # Given
    offerer_in_date_range = create_offerer(siren="123456781")
    offerer_20180701 = create_offerer(siren="123456782")
    offerer_20180801 = create_offerer(siren="123456783")
    offerer_before_date_range = create_offerer(siren="123456784")
    offerer_after_date_range = create_offerer(siren="123456785")

    PcObject.check_and_save(offerer_in_date_range, offerer_20180701, offerer_20180801, offerer_before_date_range, offerer_after_date_range)
    
    activity_in_date_range = create_offerer_activity(offerer_in_date_range, 'offerer', 'insert', issued_at=datetime(2018,7,15))
    activity_20180701 = create_offerer_activity(offerer_20180701, 'offerer', 'insert', issued_at=datetime(2018,7,1))
    activity_20180801 = create_offerer_activity(offerer_20180801, 'offerer', 'insert', issued_at=datetime(2018,8,1))
    activity_before_date_range = create_offerer_activity(offerer_before_date_range, 'offerer', 'insert', issued_at=datetime(2017,7,15))
    activity_after_date_range = create_offerer_activity(offerer_after_date_range, 'offerer', 'insert', issued_at=datetime(2018,12,15))

    save_all_activities(activity_in_date_range, activity_20180701, activity_20180801, activity_before_date_range, activity_after_date_range)

    # When
    query_with_date = find_filtered_offerers(from_date='2018-07-01',
        to_date='2018-08-01')

    # Then
    assert offerer_in_date_range in query_with_date
    assert offerer_20180701 in query_with_date
    assert offerer_20180801 in query_with_date
    assert offerer_before_date_range not in query_with_date
    assert offerer_after_date_range not in query_with_date


@pytest.mark.standalone
@clean_database
def test_find_filtered_offerers_with_has_siren_param_return_filtered_offerers(app):
    # Given
    offerer_with_siren = create_offerer(siren="123456789")
    offerer_without_siren = create_offerer(siren=None)

    PcObject.check_and_save(offerer_with_siren, offerer_without_siren)
    
    # When
    query_no_siren = find_filtered_offerers(has_siren=False)

    # Then
    assert offerer_with_siren not in query_no_siren
    assert offerer_without_siren in query_no_siren


@pytest.mark.standalone
@clean_database
def test_find_filtered_offerers_with_is_validated_param_return_filtered_offerers(app):
    # Given
    offerer_validated = create_offerer(siren="123456789", validation_token=None)
    offerer_not_validated = create_offerer(siren="123456781", validation_token="a_token")
    
    PcObject.check_and_save(offerer_validated, offerer_not_validated)
    
    # When
    query_only_validated = find_filtered_offerers(is_validated=True)

    # Then
    assert offerer_validated in query_only_validated 
    assert offerer_not_validated not in query_only_validated 


@pytest.mark.standalone
@clean_database
def test_find_filtered_offerers_with_is_active_param_return_filtered_offerers(app):
    # Given
    offerer_active = create_offerer(siren="123456789", is_active=True)
    offerer_not_active = create_offerer(siren="123456781", is_active=False)

    PcObject.check_and_save(offerer_active, offerer_not_active)
    
    # When
    query_only_active = find_filtered_offerers(is_active=True)

    # Then
    assert offerer_active in query_only_active 
    assert offerer_not_active not in query_only_active 

  
@pytest.mark.standalone
@clean_database
def test_find_filtered_offerers_with_has_bank_information_param_return_filtered_offerers(app):
    # Given
    offerer_with_bank_information = create_offerer(siren="123456781")
    offerer_without_bank_information = create_offerer(iban='DE89 3704 0044 0532 0130 00', bic="GENODEM1GLS")
    
    PcObject.check_and_save(offerer_with_bank_information, offerer_without_bank_information)
    
    # When
    query_with_bank_information = find_filtered_offerers(has_bank_information=True)

    # Then
    assert offerer_with_bank_information in query_with_bank_information
    assert offerer_without_bank_information not in query_with_bank_information


@pytest.mark.standalone
@clean_database
def test_find_filtered_offerers_with_True_has_validated_user_param_return_filtered_offerers(app):
    # Given
    offerer_with_not_validated_user = create_offerer(siren="123456781")
    offerer_with_validated_user = create_offerer(siren="123456782")
    offerer_with_both = create_offerer(siren="123456783")

    validated_user_1 = create_user(email="1@kikou.com", validation_token=None)
    validated_user_2 = create_user(email="2@kikou.com", validation_token=None)
    not_validated_user_1 = create_user(email="3@kikou.com", validation_token="a_token")
    not_validated_user_2 = create_user(email="4@kikou.com", validation_token="another_token")

    user_offerer_validated_user_1 = create_user_offerer(validated_user_1, offerer_with_validated_user)
    user_offerer_validated_user_2 = create_user_offerer(validated_user_2, offerer_with_both)
    user_offerer_not_validated_user_1 = create_user_offerer(not_validated_user_1, offerer_with_not_validated_user)
    user_offerer_not_validated_user_2 = create_user_offerer(not_validated_user_2, offerer_with_both)

    PcObject.check_and_save(user_offerer_validated_user_1, user_offerer_validated_user_2, user_offerer_not_validated_user_1, user_offerer_not_validated_user_2)

    # When
    query_validated_user = find_filtered_offerers(has_validated_user=True)

    # Then
    assert offerer_with_not_validated_user not in query_validated_user
    assert offerer_with_validated_user in query_validated_user
    assert offerer_with_both in query_validated_user


@pytest.mark.standalone
@clean_database
def test_find_filtered_offerers_with_False_has_validated_user_param_return_filtered_offerers(app):
    # Given
    offerer_with_not_validated_user = create_offerer(siren="123456781")
    offerer_with_validated_user = create_offerer(siren="123456782")
    offerer_with_both = create_offerer(siren="123456783")

    validated_user_1 = create_user(email="1@kikou.com", validation_token=None)
    validated_user_2 = create_user(email="2@kikou.com", validation_token=None)
    not_validated_user_1 = create_user(email="3@kikou.com", validation_token="a_token")
    not_validated_user_2 = create_user(email="4@kikou.com", validation_token="another_token")

    user_offerer_validated_user_1 = create_user_offerer(validated_user_1, offerer_with_validated_user)
    user_offerer_validated_user_2 = create_user_offerer(validated_user_2, offerer_with_both)
    user_offerer_not_validated_user_1 = create_user_offerer(not_validated_user_1, offerer_with_not_validated_user)
    user_offerer_not_validated_user_2 = create_user_offerer(not_validated_user_2, offerer_with_both)

    PcObject.check_and_save(user_offerer_validated_user_1, user_offerer_validated_user_2, user_offerer_not_validated_user_1, user_offerer_not_validated_user_2)

    # When
    query_not_validated = find_filtered_offerers(has_validated_user=False)

    # Then
    assert offerer_with_not_validated_user in query_validated_user
    assert offerer_with_validated_user not in query_validated_user
    assert offerer_with_both not in query_validated_user


@pytest.mark.standalone
@clean_database
def test_find_filtered_offerers_with_True_has_not_virtual_venue_param_return_filtered_offerers(app):
    # Given
    offerer_with_only_virtual_venue = create_offerer(siren="123456789")
    offerer_with_both_virtual_and_not_virtual_venue = create_offerer(siren="123456781")

    virtual_venue_1 = create_venue(offerer_with_only_virtual_venue, is_virtual=True, siret=None)
    virtual_venue_2 = create_venue(offerer_with_both_virtual_and_not_virtual_venue, is_virtual=True, siret=None)
    not_virtual_venue = create_venue(offerer_with_both_virtual_and_not_virtual_venue)

    PcObject.check_and_save(virtual_venue_1, virtual_venue_2, not_virtual_venue)

    # When
    query_with_not_virtual = find_filtered_offerers(has_not_virtual_venue=True)

    # Then
    assert offerer_with_only_virtual_venue not in query_with_not_virtual
    assert offerer_with_both_virtual_and_not_virtual_venue in query_with_not_virtual



@pytest.mark.standalone
@clean_database
def test_find_filtered_offerers_with_False_has_not_virtual_venue_param_return_filtered_offerers(app):
    # Given
    offerer_with_only_virtual_venue = create_offerer(siren="123456789")
    offerer_with_both_virtual_and_not_virtual_venue = create_offerer(siren="123456781")

    virtual_venue_1 = create_venue(offerer_with_only_virtual_venue, is_virtual=True, siret=None)
    virtual_venue_2 = create_venue(offerer_with_both_virtual_and_not_virtual_venue, is_virtual=True, siret=None)
    not_virtual_venue = create_venue(offerer_with_both_virtual_and_not_virtual_venue)

    PcObject.check_and_save(virtual_venue_1, virtual_venue_2, not_virtual_venue)

    # When
    query_only_virtual = find_filtered_offerers(has_not_virtual_venue=False)

    # Then
    assert offerer_with_only_virtual_venue in query_only_virtual
    assert offerer_with_both_virtual_and_not_virtual_venue not in query_only_virtual



@pytest.mark.standalone
@clean_database
def test_find_filtered_offerers_with_True_has_validated_venue_param_return_filtered_offerers(app):
    # Given
    offerer_with_not_validated_venue = create_offerer(siren="123456789")
    offerer_with_validated_venue = create_offerer(siren="123456781")
    offerer_with_both = create_offerer(siren="123456782")

    venue_with_not_validated_venue_1 = create_venue(offerer_with_not_validated_venue, siret="12345678912341", validation_token="another_token")
    venue_with_validated_venue_1 = create_venue(offerer_with_validated_venue, siret="12345678912342")
    venue_with_not_validated_venue_2 = create_venue(offerer_with_both, siret="12345678912343", validation_token="a_token")
    venue_with_validated_venue_2 = create_venue(offerer_with_both, siret="12345678912344")

    PcObject.check_and_save(venue_with_not_validated_venue_1, venue_with_validated_venue_1, venue_with_not_validated_venue_2, venue_with_validated_venue_2)

    # When
    query_validated = find_filtered_offerers(has_validated_venue=True)

    # Then
    assert offerer_with_not_validated_venue not in query_validated
    assert offerer_with_validated_venue in query_validated
    assert offerer_with_both in query_validated


@pytest.mark.standalone
@clean_database
def test_find_filtered_offerers_with_False_has_validated_venue_param_return_filtered_offerers(app):
    # Given
    offerer_with_not_validated_venue = create_offerer(siren="123456789")
    offerer_with_validated_venue = create_offerer(siren="123456781")
    offerer_with_both = create_offerer(siren="123456782")

    venue_with_not_validated_venue_1 = create_venue(offerer_with_not_validated_venue, siret="12345678912341", validation_token="another_token")
    venue_with_validated_venue_1 = create_venue(offerer_with_validated_venue, siret="12345678912342")
    venue_with_not_validated_venue_2 = create_venue(offerer_with_both, siret="12345678912343", validation_token="a_token")
    venue_with_validated_venue_2 = create_venue(offerer_with_both, siret="12345678912344")

    PcObject.check_and_save(venue_with_not_validated_venue_1, venue_with_validated_venue_1, venue_with_not_validated_venue_2, venue_with_validated_venue_2)

    # When
    query_not_validated = find_filtered_offerers(has_validated_venue=False)

    # Then
    assert offerer_with_not_validated_venue in query_not_validated
    assert offerer_with_validated_venue not in query_not_validated
    assert offerer_with_both not in query_not_validated


@pytest.mark.standalone
@clean_database
def test_find_filtered_offerers_with_True_has_validated_user_offerer_param_return_filtered_offerers(app):
    # Given
    offerer_with_not_validated_user_offerer = create_offerer(siren="123456781")
    offerer_with_validated_user_offerer = create_offerer(siren="123456782")
    offerer_with_both = create_offerer(siren="123456783")

    user = create_user()

    user_offerer_validated_1 = create_user_offerer(user, offerer_with_validated_user_offerer)
    user_offerer_validated_2 = create_user_offerer(user, offerer_with_both)
    user_offerer_not_validated_1 = create_user_offerer(user, offerer_with_not_validated_user_offerer, validation_token="a_token")
    user_offerer_not_validated_2 = create_user_offerer(user, offerer_with_both, validation_token="another_token")

    PcObject.check_and_save(user_offerer_validated_1, user_offerer_validated_2, user_offerer_not_validated_1, user_offerer_not_validated_2)

    # When
    query_validated = find_filtered_offerers(has_validated_user_offerer=True)

    # Then
    assert offerer_with_not_validated_user_offerer not in query_validated
    assert offerer_with_validated_user_offerer in query_validated
    assert offerer_with_both in query_validated



@pytest.mark.standalone
@clean_database
def test_find_filtered_offerers_with_False_has_validated_user_offerer_param_return_filtered_offerers(app):
    # Given
    offerer_with_not_validated_user_offerer = create_offerer(siren="123456781")
    offerer_with_validated_user_offerer = create_offerer(siren="123456782")
    offerer_with_both = create_offerer(siren="123456783")

    user = create_user()

    user_offerer_validated_1 = create_user_offerer(user, offerer_with_validated_user_offerer)
    user_offerer_validated_2 = create_user_offerer(user, offerer_with_both)
    user_offerer_not_validated_1 = create_user_offerer(user, offerer_with_not_validated_user_offerer, validation_token="a_token")
    user_offerer_not_validated_2 = create_user_offerer(user, offerer_with_both, validation_token="another_token")

    PcObject.check_and_save(user_offerer_validated_1, user_offerer_validated_2, user_offerer_not_validated_1, user_offerer_not_validated_2)

    # When
    query_not_validated = find_filtered_offerers(has_validated_user_offerer=False)

    # Then
    assert offerer_with_not_validated_user_offerer in query_not_validated
    assert offerer_with_validated_user_offerer not in query_not_validated
    assert offerer_with_both not in query_not_validated


@pytest.mark.standalone
@clean_database
def test_find_filtered_offerers_with_offer_status_with_VALID_param_return_filtered_offerers(app):
    # Given
    offerer_without_offer = create_offerer(siren="123456781")
    offerer_with_valid_event = create_offerer(siren="123456782")
    offerer_with_expired_event = create_offerer(siren="123456783")
    offerer_with_valid_thing = create_offerer(siren="123456784")
    offerer_with_expired_thing = create_offerer(siren="123456785")
    offerer_with_soft_deleted_thing = create_offerer(siren="123456786")
    offerer_with_soft_deleted_event = create_offerer(siren="123456787")
    offerer_with_not_available_event = create_offerer(siren="123456788")

    venue_without_offer = create_venue(offerer_without_offer)
    venue_with_valid_event = create_venue(offerer_with_valid_event, siret='12345678912346')
    venue_with_expired_event = create_venue(offerer_with_expired_event, siret='12345678912347')
    venue_with_valid_thing = create_venue(offerer_with_valid_thing, siret='12345678912348')
    venue_with_expired_thing = create_venue(offerer_with_expired_thing, siret='12345678912349')
    venue_with_soft_deleted_thing = create_venue(offerer_with_soft_deleted_thing, siret='12345678912342')
    venue_with_soft_deleted_event = create_venue(offerer_with_soft_deleted_event, siret='12345678912343')
    venue_with_not_available_event = create_venue(offerer_with_not_available_event, siret='12345678912344')

    valid_event = create_event_offer(venue_with_valid_event)
    expired_event = create_event_offer(venue_with_expired_event)
    valid_thing = create_thing_offer(venue_with_valid_thing)
    expired_thing = create_thing_offer(venue_with_expired_thing)
    soft_deleted_thing = create_thing_offer(venue_with_soft_deleted_thing)
    soft_deleted_event = create_event_offer(venue_with_soft_deleted_event)
    not_available_event = create_event_offer(venue_with_not_available_event)

    valid_event_occurrence = create_event_occurrence(valid_event,
        beginning_datetime=datetime.utcnow() + timedelta(days=4),
        end_datetime=datetime.utcnow() + timedelta(days=5))
    valid_event_occurrence_soft_deleted = create_event_occurrence(soft_deleted_event,
        beginning_datetime=datetime.utcnow() + timedelta(days=4),
        end_datetime=datetime.utcnow() + timedelta(days=5))
    valid_event_occurrence_not_available = create_event_occurrence(not_available_event,
        beginning_datetime=datetime.utcnow() + timedelta(days=4),
        end_datetime=datetime.utcnow() + timedelta(days=5))
    expired_event_occurence = create_event_occurrence(expired_event,
       beginning_datetime=datetime(2018,2,1), end_datetime=datetime(2018,3,2))

    valid_stock = create_stock_with_thing_offer(offerer_with_valid_thing, venue_with_valid_thing, valid_thing)
    expired_stock = create_stock_with_thing_offer(offerer_with_expired_thing, venue_with_expired_thing, expired_thing,
       available=0)
    soft_deleted_thing_stock = create_stock_with_thing_offer(offerer_with_soft_deleted_thing, venue_with_soft_deleted_thing,
       soft_deleted_thing, soft_deleted=True)
    
    expired_booking_limit_date_event_stock = create_stock_from_event_occurrence(expired_event_occurence,
       booking_limit_date=datetime(2018,1,1))
    valid_booking_limit_date_event_stock = create_stock_from_event_occurrence(valid_event_occurrence,
       booking_limit_date=datetime.utcnow() + timedelta(days=3))
    soft_deleted_event_stock = create_stock_from_event_occurrence(valid_event_occurrence_soft_deleted, 
       soft_deleted=True, booking_limit_date=datetime.utcnow() + timedelta(days=3))
    not_available_event_stock = create_stock_from_event_occurrence(valid_event_occurrence_not_available, 
       available=0, booking_limit_date=datetime.utcnow() + timedelta(days=3))

    PcObject.check_and_save(venue_without_offer, valid_event_occurrence, expired_event_occurence,
        valid_stock, expired_stock, soft_deleted_thing_stock, expired_booking_limit_date_event_stock,
        valid_booking_limit_date_event_stock, soft_deleted_event_stock)    # When
    query_has_valid_offer = find_filtered_offerers(offer_status='VALID')
   
    # Then
    assert offerer_without_offer in query_has_valid_offer
    assert offerer_with_valid_event not in query_has_valid_offer
    assert offerer_with_expired_event not in query_has_valid_offer
    assert offerer_with_valid_thing  in query_has_valid_offer
    assert offerer_with_expired_thing not in query_has_valid_offer
    assert offerer_with_soft_deleted_thing not in query_has_valid_offer
    assert offerer_with_soft_deleted_event not in query_has_valid_offer
    assert offerer_with_not_available_event not in query_has_valid_offer


@pytest.mark.standalone
@clean_database
def test_find_filtered_offerers_with_offer_status_with_EXPIRED_param_return_filtered_offerers(app):
    # Given
    offerer_without_offer = create_offerer(siren="123456781")
    offerer_with_valid_event = create_offerer(siren="123456782")
    offerer_with_expired_event = create_offerer(siren="123456783")
    offerer_with_valid_thing = create_offerer(siren="123456784")
    offerer_with_expired_thing = create_offerer(siren="123456785")
    offerer_with_soft_deleted_thing = create_offerer(siren="123456786")
    offerer_with_soft_deleted_event = create_offerer(siren="123456787")
    offerer_with_not_available_event = create_offerer(siren="123456788")

    venue_without_offer = create_venue(offerer_without_offer)
    venue_with_valid_event = create_venue(offerer_with_valid_event, siret='12345678912346')
    venue_with_expired_event = create_venue(offerer_with_expired_event, siret='12345678912347')
    venue_with_valid_thing = create_venue(offerer_with_valid_thing, siret='12345678912348')
    venue_with_expired_thing = create_venue(offerer_with_expired_thing, siret='12345678912349')
    venue_with_soft_deleted_thing = create_venue(offerer_with_soft_deleted_thing, siret='12345678912342')
    venue_with_soft_deleted_event = create_venue(offerer_with_soft_deleted_event, siret='12345678912343')
    venue_with_not_available_event = create_venue(offerer_with_not_available_event, siret='12345678912344')

    valid_event = create_event_offer(venue_with_valid_event)
    expired_event = create_event_offer(venue_with_expired_event)
    valid_thing = create_thing_offer(venue_with_valid_thing)
    expired_thing = create_thing_offer(venue_with_expired_thing)
    soft_deleted_thing = create_thing_offer(venue_with_soft_deleted_thing)
    soft_deleted_event = create_event_offer(venue_with_soft_deleted_event)
    not_available_event = create_event_offer(venue_with_not_available_event)

    valid_event_occurrence = create_event_occurrence(valid_event,
        beginning_datetime=datetime.utcnow() + timedelta(days=4),
        end_datetime=datetime.utcnow() + timedelta(days=5))
    valid_event_occurrence_soft_deleted = create_event_occurrence(soft_deleted_event,
        beginning_datetime=datetime.utcnow() + timedelta(days=4),
        end_datetime=datetime.utcnow() + timedelta(days=5))
    valid_event_occurrence_not_available = create_event_occurrence(not_available_event,
        beginning_datetime=datetime.utcnow() + timedelta(days=4),
        end_datetime=datetime.utcnow() + timedelta(days=5))
    expired_event_occurence = create_event_occurrence(expired_event,
       beginning_datetime=datetime(2018,2,1), end_datetime=datetime(2018,3,2))

    valid_stock = create_stock_with_thing_offer(offerer_with_valid_thing, venue_with_valid_thing, valid_thing)
    expired_stock = create_stock_with_thing_offer(offerer_with_expired_thing, venue_with_expired_thing, expired_thing,
       available=0)
    soft_deleted_thing_stock = create_stock_with_thing_offer(offerer_with_soft_deleted_thing, venue_with_soft_deleted_thing,
       soft_deleted_thing, soft_deleted=True)
    
    expired_booking_limit_date_event_stock = create_stock_from_event_occurrence(expired_event_occurence,
       booking_limit_date=datetime(2018,1,1))
    valid_booking_limit_date_event_stock = create_stock_from_event_occurrence(valid_event_occurrence,
       booking_limit_date=datetime.utcnow() + timedelta(days=3))
    soft_deleted_event_stock = create_stock_from_event_occurrence(valid_event_occurrence_soft_deleted, 
       soft_deleted=True, booking_limit_date=datetime.utcnow() + timedelta(days=3))
    not_available_event_stock = create_stock_from_event_occurrence(valid_event_occurrence_not_available, 
       available=0, booking_limit_date=datetime.utcnow() + timedelta(days=3))

    PcObject.check_and_save(venue_without_offer, valid_event_occurrence, expired_event_occurence,
        valid_stock, expired_stock, soft_deleted_thing_stock, expired_booking_limit_date_event_stock,
        valid_booking_limit_date_event_stock, soft_deleted_event_stock)   
    # When
    query_has_expired_offer = find_filtered_offerers(offer_status='EXPIRED')
   
    # Then
    assert offerer_with_valid_event not in query_has_expired_offer
    assert offerer_without_offer not in query_has_expired_offer
    assert offerer_with_expired_event in query_has_expired_offer
    assert offerer_with_valid_thing not in query_has_expired_offer
    assert offerer_with_expired_thing in query_has_expired_offer
    assert offerer_with_soft_deleted_thing in query_has_expired_offer
    assert offerer_with_soft_deleted_event in query_has_expired_offer
    assert offerer_with_not_available_event in query_has_expired_offer


@pytest.mark.standalone
@clean_database
def test_find_filtered_offerers_with_offer_status_with_WITHOUT_param_return_filtered_offerers(app):
    # Given
    offerer_without_offer = create_offerer(siren="123456781")
    offerer_with_valid_event = create_offerer(siren="123456782")
    offerer_with_expired_event = create_offerer(siren="123456783")
    offerer_with_valid_thing = create_offerer(siren="123456784")
    offerer_with_expired_thing = create_offerer(siren="123456785")
    offerer_with_soft_deleted_thing = create_offerer(siren="123456786")
    offerer_with_soft_deleted_event = create_offerer(siren="123456787")
    offerer_with_not_available_event = create_offerer(siren="123456788")

    venue_without_offer = create_venue(offerer_without_offer)
    venue_with_valid_event = create_venue(offerer_with_valid_event, siret='12345678912346')
    venue_with_expired_event = create_venue(offerer_with_expired_event, siret='12345678912347')
    venue_with_valid_thing = create_venue(offerer_with_valid_thing, siret='12345678912348')
    venue_with_expired_thing = create_venue(offerer_with_expired_thing, siret='12345678912349')
    venue_with_soft_deleted_thing = create_venue(offerer_with_soft_deleted_thing, siret='12345678912342')
    venue_with_soft_deleted_event = create_venue(offerer_with_soft_deleted_event, siret='12345678912343')
    venue_with_not_available_event = create_venue(offerer_with_not_available_event, siret='12345678912344')

    valid_event = create_event_offer(venue_with_valid_event)
    expired_event = create_event_offer(venue_with_expired_event)
    valid_thing = create_thing_offer(venue_with_valid_thing)
    expired_thing = create_thing_offer(venue_with_expired_thing)
    soft_deleted_thing = create_thing_offer(venue_with_soft_deleted_thing)
    soft_deleted_event = create_event_offer(venue_with_soft_deleted_event)
    not_available_event = create_event_offer(venue_with_not_available_event)

    valid_event_occurrence = create_event_occurrence(valid_event,
        beginning_datetime=datetime.utcnow() + timedelta(days=4),
        end_datetime=datetime.utcnow() + timedelta(days=5))
    valid_event_occurrence_soft_deleted = create_event_occurrence(soft_deleted_event,
        beginning_datetime=datetime.utcnow() + timedelta(days=4),
        end_datetime=datetime.utcnow() + timedelta(days=5))
    valid_event_occurrence_not_available = create_event_occurrence(not_available_event,
        beginning_datetime=datetime.utcnow() + timedelta(days=4),
        end_datetime=datetime.utcnow() + timedelta(days=5))
    expired_event_occurence = create_event_occurrence(expired_event,
       beginning_datetime=datetime(2018,2,1), end_datetime=datetime(2018,3,2))

    valid_stock = create_stock_with_thing_offer(offerer_with_valid_thing, venue_with_valid_thing, valid_thing)
    expired_stock = create_stock_with_thing_offer(offerer_with_expired_thing, venue_with_expired_thing, expired_thing,
       available=0)
    soft_deleted_thing_stock = create_stock_with_thing_offer(offerer_with_soft_deleted_thing, venue_with_soft_deleted_thing,
       soft_deleted_thing, soft_deleted=True)
    
    expired_booking_limit_date_event_stock = create_stock_from_event_occurrence(expired_event_occurence,
       booking_limit_date=datetime(2018,1,1))
    valid_booking_limit_date_event_stock = create_stock_from_event_occurrence(valid_event_occurrence,
       booking_limit_date=datetime.utcnow() + timedelta(days=3))
    soft_deleted_event_stock = create_stock_from_event_occurrence(valid_event_occurrence_soft_deleted, 
       soft_deleted=True, booking_limit_date=datetime.utcnow() + timedelta(days=3))
    not_available_event_stock = create_stock_from_event_occurrence(valid_event_occurrence_not_available, 
       available=0, booking_limit_date=datetime.utcnow() + timedelta(days=3))

    PcObject.check_and_save(venue_without_offer, valid_event_occurrence, expired_event_occurence,
        valid_stock, expired_stock, soft_deleted_thing_stock, expired_booking_limit_date_event_stock,
        valid_booking_limit_date_event_stock, soft_deleted_event_stock)   
    # When
    query_without_offer = find_filtered_offerers(offer_status='WITHOUT')
   
    # Then
    assert offerer_with_valid_event not in query_without_offer
    assert offerer_without_offer in query_without_offer
    assert offerer_with_expired_event not in query_without_offer
    assert offerer_with_valid_thing not in query_without_offer
    assert offerer_with_expired_thing not in query_without_offer
    assert offerer_with_soft_deleted_thing not in query_without_offer
    assert offerer_with_soft_deleted_event not in query_without_offer
    assert offerer_with_not_available_event not in query_without_offer


@pytest.mark.standalone
@clean_database
def test_find_filtered_offerers_with_offer_status_with_ALL_param_return_filtered_offerers(app):
    # Given
    offerer_without_offer = create_offerer(siren="123456781")
    offerer_with_valid_event = create_offerer(siren="123456782")
    offerer_with_expired_event = create_offerer(siren="123456783")
    offerer_with_valid_thing = create_offerer(siren="123456784")
    offerer_with_expired_thing = create_offerer(siren="123456785")
    offerer_with_soft_deleted_thing = create_offerer(siren="123456786")
    offerer_with_soft_deleted_event = create_offerer(siren="123456787")
    offerer_with_not_available_event = create_offerer(siren="123456788")

    venue_without_offer = create_venue(offerer_without_offer)
    venue_with_valid_event = create_venue(offerer_with_valid_event, siret='12345678912346')
    venue_with_expired_event = create_venue(offerer_with_expired_event, siret='12345678912347')
    venue_with_valid_thing = create_venue(offerer_with_valid_thing, siret='12345678912348')
    venue_with_expired_thing = create_venue(offerer_with_expired_thing, siret='12345678912349')
    venue_with_soft_deleted_thing = create_venue(offerer_with_soft_deleted_thing, siret='12345678912342')
    venue_with_soft_deleted_event = create_venue(offerer_with_soft_deleted_event, siret='12345678912343')
    venue_with_not_available_event = create_venue(offerer_with_not_available_event, siret='12345678912344')

    valid_event = create_event_offer(venue_with_valid_event)
    expired_event = create_event_offer(venue_with_expired_event)
    valid_thing = create_thing_offer(venue_with_valid_thing)
    expired_thing = create_thing_offer(venue_with_expired_thing)
    soft_deleted_thing = create_thing_offer(venue_with_soft_deleted_thing)
    soft_deleted_event = create_event_offer(venue_with_soft_deleted_event)
    not_available_event = create_event_offer(venue_with_not_available_event)

    valid_event_occurrence = create_event_occurrence(valid_event,
        beginning_datetime=datetime.utcnow() + timedelta(days=4),
        end_datetime=datetime.utcnow() + timedelta(days=5))
    valid_event_occurrence_soft_deleted = create_event_occurrence(soft_deleted_event,
        beginning_datetime=datetime.utcnow() + timedelta(days=4),
        end_datetime=datetime.utcnow() + timedelta(days=5))
    valid_event_occurrence_not_available = create_event_occurrence(not_available_event,
        beginning_datetime=datetime.utcnow() + timedelta(days=4),
        end_datetime=datetime.utcnow() + timedelta(days=5))
    expired_event_occurence = create_event_occurrence(expired_event,
       beginning_datetime=datetime(2018,2,1), end_datetime=datetime(2018,3,2))

    valid_stock = create_stock_with_thing_offer(offerer_with_valid_thing, venue_with_valid_thing, valid_thing)
    expired_stock = create_stock_with_thing_offer(offerer_with_expired_thing, venue_with_expired_thing, expired_thing,
       available=0)
    soft_deleted_thing_stock = create_stock_with_thing_offer(offerer_with_soft_deleted_thing, venue_with_soft_deleted_thing,
       soft_deleted_thing, soft_deleted=True)
    
    expired_booking_limit_date_event_stock = create_stock_from_event_occurrence(expired_event_occurence,
       booking_limit_date=datetime(2018,1,1))
    valid_booking_limit_date_event_stock = create_stock_from_event_occurrence(valid_event_occurrence,
       booking_limit_date=datetime.utcnow() + timedelta(days=3))
    soft_deleted_event_stock = create_stock_from_event_occurrence(valid_event_occurrence_soft_deleted, 
       soft_deleted=True, booking_limit_date=datetime.utcnow() + timedelta(days=3))
    not_available_event_stock = create_stock_from_event_occurrence(valid_event_occurrence_not_available, 
       available=0, booking_limit_date=datetime.utcnow() + timedelta(days=3))

    PcObject.check_and_save(venue_without_offer, valid_event_occurrence, expired_event_occurence,
        valid_stock, expired_stock, soft_deleted_thing_stock, expired_booking_limit_date_event_stock,
        valid_booking_limit_date_event_stock, soft_deleted_event_stock)
   
    # When
    query_with_all_offer = find_filtered_offerers(offer_status='ALL')
   
    # Then
    assert offerer_with_valid_event in query_with_all_offer
    assert offerer_without_offer not in query_with_all_offer
    assert offerer_with_expired_event in query_with_all_offer
    assert offerer_with_valid_thing in query_with_all_offer
    assert offerer_with_expired_thing in query_with_all_offer
    assert offerer_with_soft_deleted_thing in query_with_all_offer
    assert offerer_with_soft_deleted_event in query_with_all_offer
    assert offerer_with_not_available_event in query_with_all_offer


@pytest.mark.standalone
@clean_database
def test_find_filtered_offerers_with_offer_status_with_ALL_param_and_virtual_venues_return_filtered_offerers(app):


    assert (1+1) == 3