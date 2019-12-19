""" repository venue queries """
from datetime import datetime, timedelta

from models import PcObject
from repository.venue_queries import find_filtered_venues, find_by_managing_user
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_user_offerer
from tests.model_creators.activity_creators import create_venue_activity, save_all_activities
from tests.model_creators.specific_creators import create_stock_from_event_occurrence, create_stock_with_thing_offer, \
    create_offer_with_thing_product, create_offer_with_event_product, create_event_occurrence


@clean_database
def test_find_filtered_venues_with_sirens_params_return_filtered_venues(app):
    # given
    offerer_123456789 = create_offerer(name="offerer_123456789", siren="123456789")
    offerer_123456781 = create_offerer(name="offerer_123456781", siren="123456781")
    offerer_123456782 = create_offerer(name="offerer_123456782", siren="123456782")
    offerer_123456783 = create_offerer(name="offerer_123456783", siren="123456783")
    offerer_123456784 = create_offerer(name="offerer_123456784", siren="123456784")

    venue_123456789 = create_venue(offerer_123456789, name="venue_123456789", siret="12345678912345")
    venue_123456781 = create_venue(offerer_123456781, name="venue_123456781", siret="12345678112345")
    venue_123456782 = create_venue(offerer_123456782, name="venue_123456782", siret="12345678212345")
    venue_123456783 = create_venue(offerer_123456783, name="venue_123456783", siret="12345678312345")
    venue_123456784 = create_venue(offerer_123456784, name="venue_123456784", siret="12345678412345")

    PcObject.save(venue_123456789, venue_123456781, venue_123456782, venue_123456783, venue_123456784)

    # when
    query_with_sirens = find_filtered_venues(sirens=["123456781", "123456782", "123456783"])

    # then
    assert venue_123456789 not in query_with_sirens
    assert venue_123456781 in query_with_sirens
    assert venue_123456782 in query_with_sirens
    assert venue_123456783 in query_with_sirens
    assert venue_123456784 not in query_with_sirens


@clean_database
def test_find_filtered_venues_with_has_validated_offerer_param_return_filtered_venues(app):
    # Given
    offerer_valid = create_offerer()
    offerer_not_valid = create_offerer(siren='123456798', validation_token='abc')
    venue_with_offerer_valid = create_venue(offerer_valid)
    venue_with_offerer_not_valid = create_venue(offerer_not_valid, siret='12345679812345')
    PcObject.save(venue_with_offerer_valid, venue_with_offerer_not_valid)

    # When
    query_with_not_valid_offerer_only = find_filtered_venues(has_validated_offerer=False)

    # Then
    assert venue_with_offerer_valid not in query_with_not_valid_offerer_only
    assert venue_with_offerer_not_valid in query_with_not_valid_offerer_only


@clean_database
def test_find_filtered_venues_with_dpts_param_return_filtered_venues(app):
    # Given
    offerer = create_offerer()
    venue_93 = create_venue(offerer, departement_code='93', postal_code='93000')
    venue_67 = create_venue(offerer, departement_code='67', postal_code='67000',
                            siret='12345678912346')
    venue_34 = create_venue(offerer, departement_code='34', postal_code='34000',
                            siret='12345678912347')
    venue_971 = create_venue(offerer, postal_code='97100', siret='12345678912348')

    venue_virtual = create_venue(offerer, is_virtual=True, siret=None, postal_code=None)
    PcObject.save(venue_93, venue_67, venue_34, venue_971, venue_virtual)

    # When
    query_with_dpts = find_filtered_venues(dpts=['93', '67', '971'])

    # Then
    assert venue_93 in query_with_dpts
    assert venue_67 in query_with_dpts
    assert venue_971 in query_with_dpts
    assert venue_34 not in query_with_dpts
    assert venue_virtual not in query_with_dpts


@clean_database
def test_find_filtered_venues_with_zipcodes_param_return_filtered_venues(app):
    # Given
    offerer = create_offerer()
    venue_93000 = create_venue(offerer, postal_code='93000')
    venue_67000 = create_venue(offerer, postal_code='67000', siret='12345678912346')
    venue_34000 = create_venue(offerer, postal_code='34000', siret='12345678912347')
    venue_virtual = create_venue(offerer, is_virtual=True, siret=None)
    PcObject.save(venue_virtual, venue_93000, venue_67000, venue_34000)

    # When
    query_with_zipcodes = find_filtered_venues(zip_codes=['93000', '34000'])

    # Then
    assert venue_93000 in query_with_zipcodes
    assert venue_34000 in query_with_zipcodes
    assert venue_virtual not in query_with_zipcodes
    assert venue_67000 not in query_with_zipcodes


@clean_database
def test_find_filtered_venues_with_date_params_return_filtered_venues(app):
    # Given
    offerer = create_offerer()
    venue_20180630 = create_venue(offerer)
    venue_20180730 = create_venue(offerer, siret='12345678912346')
    venue_20180830 = create_venue(offerer, siret='12345678912347')
    PcObject.save(venue_20180630, venue_20180730, venue_20180830)

    activity1 = create_venue_activity(venue_20180630, 'insert', issued_at=datetime(2018,
                                                                                   6, 30))
    activity2 = create_venue_activity(venue_20180730, 'insert', issued_at=datetime(2018,
                                                                                   7, 30))
    activity3 = create_venue_activity(venue_20180830, 'insert', issued_at=datetime(2018,
                                                                                   8, 30))
    save_all_activities(activity1, activity2, activity3)

    # When
    query_with_date = find_filtered_venues(from_date='2018-07-01',
                                           to_date='2018-08-01')

    # Then
    assert venue_20180630 not in query_with_date
    assert venue_20180830 not in query_with_date
    assert venue_20180730 in query_with_date


@clean_database
def test_find_filtered_venues_with_is_virtual_param_return_filtered_venues(app):
    # Given
    offerer = create_offerer()
    venue_virtual = create_venue(offerer, is_virtual=True, siret=None)
    venue_not_virtual = create_venue(offerer, is_virtual=False, postal_code='34000')
    PcObject.save(venue_virtual, venue_not_virtual)

    # When
    query_only_virtual = find_filtered_venues(is_virtual=True)

    # Then
    assert venue_virtual in query_only_virtual
    assert venue_not_virtual not in query_only_virtual


@clean_database
def test_find_filtered_venues_with_has_siret_param_return_filtered_venues(app):
    # Given
    offerer = create_offerer()
    venue_virtual = create_venue(offerer, is_virtual=True, siret=None)
    venue_with_siret = create_venue(offerer)
    venue_without_siret = create_venue(offerer, siret=None, comment="comment", is_virtual=False)
    PcObject.save(venue_virtual, venue_with_siret, venue_without_siret)

    # When
    query_no_siret = find_filtered_venues(has_siret=False)

    # Then
    assert venue_without_siret in query_no_siret
    assert venue_virtual in query_no_siret
    assert venue_with_siret not in query_no_siret


@clean_database
def test_find_filtered_venues_with_is_validated_param_return_filtered_venues(app):
    # Given
    offerer = create_offerer()
    venue_not_validated = create_venue(offerer, validation_token="there is a token here")
    venue_validated = create_venue(offerer, siret='12345678912346')
    PcObject.save(venue_not_validated, venue_validated)

    # When
    query_only_validated = find_filtered_venues(is_validated=True)

    # Then
    assert venue_not_validated not in query_only_validated
    assert venue_validated in query_only_validated


@clean_database
def test_find_filtered_venues_with_has_offerer_with_siren_param_return_filtered_venues(app):
    # Given
    offerer_with_siren = create_offerer(siren='123456789')
    offerer_without_siren = create_offerer(siren=None)

    venue_with_offerer_with_siren = create_venue(offerer_with_siren)
    venue_with_offerer_without_siren = create_venue(offerer_without_siren, siret='12345678912346')
    PcObject.save(venue_with_offerer_with_siren, venue_with_offerer_without_siren)

    # When
    query_validated = find_filtered_venues(has_offerer_with_siren=True)

    # Then
    assert venue_with_offerer_without_siren not in query_validated
    assert venue_with_offerer_with_siren in query_validated


@clean_database
def test_find_filtered_venues_with_True_has_validated_user_offerer_param_return_filtered_venues(app):
    # Given
    user = create_user()
    user2 = create_user(email="another@mail.com")
    offerer1 = create_offerer()
    offerer2 = create_offerer(siren="123456781")
    offerer3 = create_offerer(siren="123456782")

    validated_user_offerer = create_user_offerer(user, offerer1)
    not_validated_user_offerer = create_user_offerer(user, offerer2, validation_token="a_token")
    user_offerer_for_both1 = create_user_offerer(user, offerer3)
    user_offerer_for_both2 = create_user_offerer(user2, offerer3, validation_token="other_token")

    venue_with_validated_user_offerer = create_venue(offerer1, siret='12345678912346')
    venue_with_not_validated_user_offerer = create_venue(offerer2, siret='12345678912347')
    venue_with_both = create_venue(offerer3)

    PcObject.save(validated_user_offerer, not_validated_user_offerer,
                  user_offerer_for_both1, user_offerer_for_both2, venue_with_not_validated_user_offerer,
                  venue_with_validated_user_offerer, venue_with_both)

    # When
    query_validated = find_filtered_venues(has_validated_user_offerer=True)

    # Then
    assert venue_with_not_validated_user_offerer not in query_validated
    assert venue_with_validated_user_offerer in query_validated
    assert venue_with_both in query_validated


@clean_database
def test_find_filtered_venues_with_False_has_validated_user_offerer_param_return_filtered_venues(app):
    # Given
    user = create_user()
    user2 = create_user(email="another@mail.com")
    offerer1 = create_offerer()
    offerer2 = create_offerer(siren="123456781")
    offerer3 = create_offerer(siren="123456782")

    validated_user_offerer = create_user_offerer(user, offerer1)
    not_validated_user_offerer = create_user_offerer(user, offerer2, validation_token="a_token")
    user_offerer_for_both1 = create_user_offerer(user, offerer3)
    user_offerer_for_both2 = create_user_offerer(user2, offerer3, validation_token="other_token")

    venue_with_validated_user_offerer = create_venue(offerer1, siret='12345678912346')
    venue_with_not_validated_user_offerer = create_venue(offerer2, siret='12345678912347')
    venue_with_both = create_venue(offerer3)

    PcObject.save(validated_user_offerer, not_validated_user_offerer,
                  user_offerer_for_both1, user_offerer_for_both2, venue_with_not_validated_user_offerer,
                  venue_with_validated_user_offerer, venue_with_both)

    # When
    query_not_validated = find_filtered_venues(has_validated_user_offerer=False)

    # Then
    assert venue_with_not_validated_user_offerer in query_not_validated
    assert venue_with_validated_user_offerer not in query_not_validated
    assert venue_with_both not in query_not_validated


@clean_database
def test_find_filtered_venues_with_True_has_validated_user_param_return_filtered_venues(app):
    # Given
    validated_user = create_user()
    not_validated_user1 = create_user(email="mail1@mail.com", validation_token="hello token")
    not_validated_user2 = create_user(email="mail2@mail.com", validation_token="other token")
    offerer1 = create_offerer()
    offerer2 = create_offerer(siren="123456781")
    offerer3 = create_offerer(siren="123456782")
    user_offerer1 = create_user_offerer(validated_user, offerer1)
    user_offerer2 = create_user_offerer(not_validated_user1, offerer2)
    user_offerer3 = create_user_offerer(validated_user, offerer3)
    user_offerer4 = create_user_offerer(not_validated_user2, offerer3)

    venue_with_validated_user = create_venue(offerer1)
    venue_with_not_validated_user = create_venue(offerer2, siret='12345678912346')
    venue_with_both = create_venue(offerer3, siret='12345678912347')

    PcObject.save(user_offerer1, user_offerer2, user_offerer3, user_offerer4, venue_with_not_validated_user,
                  venue_with_validated_user, venue_with_both)

    # When
    query_validated = find_filtered_venues(has_validated_user=True)

    # Then
    assert venue_with_not_validated_user not in query_validated
    assert venue_with_validated_user in query_validated
    assert venue_with_both in query_validated


@clean_database
def test_find_filtered_venues_with_False_has_validated_user_param_return_filtered_venues(app):
    # Given
    validated_user = create_user()
    not_validated_user1 = create_user(email="mail1@mail.com", validation_token="hello token")
    not_validated_user2 = create_user(email="mail2@mail.com", validation_token="other token")
    offerer1 = create_offerer()
    offerer2 = create_offerer(siren="123456781")
    offerer3 = create_offerer(siren="123456782")
    user_offerer1 = create_user_offerer(validated_user, offerer1)
    user_offerer2 = create_user_offerer(not_validated_user1, offerer2)
    user_offerer3 = create_user_offerer(validated_user, offerer3)
    user_offerer4 = create_user_offerer(not_validated_user2, offerer3)

    venue_with_validated_user = create_venue(offerer1)
    venue_with_not_validated_user = create_venue(offerer2, siret='12345678912346')
    venue_with_both = create_venue(offerer3, siret='12345678912347')

    PcObject.save(user_offerer1, user_offerer2, user_offerer3, user_offerer4, venue_with_not_validated_user,
                  venue_with_validated_user, venue_with_both)

    # When
    query_not_validated = find_filtered_venues(has_validated_user=False)

    # Then
    assert venue_with_not_validated_user in query_not_validated
    assert venue_with_validated_user not in query_not_validated
    assert venue_with_both not in query_not_validated


@clean_database
def test_find_filtered_venues_with_offer_status_with_VALID_param_return_filtered_venues(app):
    # Given
    offerer = create_offerer()

    venue_without_offer = create_venue(offerer)
    venue_with_valid_event = create_venue(offerer, siret='12345678912346')
    venue_with_expired_event = create_venue(offerer, siret='12345678912347')
    venue_with_valid_thing = create_venue(offerer, siret='12345678912348')
    venue_with_expired_thing = create_venue(offerer, siret='12345678912349')
    venue_with_soft_deleted_thing = create_venue(offerer, siret='12345678912342')
    venue_with_soft_deleted_event = create_venue(offerer, siret='12345678912343')
    venue_with_not_available_event = create_venue(offerer, siret='12345678912344')

    valid_event = create_offer_with_event_product(venue_with_valid_event)
    expired_event = create_offer_with_event_product(venue_with_expired_event)
    valid_thing = create_offer_with_thing_product(venue_with_valid_thing)
    expired_thing = create_offer_with_thing_product(venue_with_expired_thing)
    soft_deleted_thing = create_offer_with_thing_product(venue_with_soft_deleted_thing)
    soft_deleted_event = create_offer_with_event_product(venue_with_soft_deleted_event)
    not_available_event = create_offer_with_event_product(venue_with_not_available_event)

    valid_event_occurrence = create_event_occurrence(valid_event,
                                                     beginning_datetime=datetime.utcnow() + timedelta(days=4),
                                                     end_datetime=datetime.utcnow() + timedelta(days=5))
    valid_event_occurrence_soft_deleted = create_event_occurrence(soft_deleted_event,
                                                                  beginning_datetime=datetime.utcnow() + timedelta(
                                                                      days=4),
                                                                  end_datetime=datetime.utcnow() + timedelta(days=5))
    valid_event_occurrence_not_available = create_event_occurrence(not_available_event,
                                                                   beginning_datetime=datetime.utcnow() + timedelta(
                                                                       days=4),
                                                                   end_datetime=datetime.utcnow() + timedelta(days=5))
    expired_event_occurence = create_event_occurrence(expired_event,
                                                      beginning_datetime=datetime(2018, 2, 1),
                                                      end_datetime=datetime(2018, 3, 2))

    valid_stock = create_stock_with_thing_offer(offerer, venue_with_valid_thing, valid_thing)
    expired_stock = create_stock_with_thing_offer(offerer, venue_with_expired_thing, expired_thing, available=0)
    soft_deleted_thing_stock = create_stock_with_thing_offer(offerer, venue_with_soft_deleted_thing, soft_deleted_thing,
                                                             soft_deleted=True)

    expired_booking_limit_date_event_stock = create_stock_from_event_occurrence(expired_event_occurence,
                                                                                booking_limit_date=datetime(2018, 1, 1))
    valid_booking_limit_date_event_stock = create_stock_from_event_occurrence(valid_event_occurrence,
                                                                              booking_limit_date=datetime.utcnow() + timedelta(
                                                                                  days=3))
    soft_deleted_event_stock = create_stock_from_event_occurrence(valid_event_occurrence_soft_deleted,
                                                                  soft_deleted=True,
                                                                  booking_limit_date=datetime.utcnow() + timedelta(
                                                                      days=3))
    not_available_event_stock = create_stock_from_event_occurrence(valid_event_occurrence_not_available,
                                                                   available=0,
                                                                   booking_limit_date=datetime.utcnow() + timedelta(
                                                                       days=3))

    PcObject.save(venue_without_offer,
                  valid_stock, expired_stock, soft_deleted_thing_stock,
                  expired_booking_limit_date_event_stock,
                  valid_booking_limit_date_event_stock, soft_deleted_event_stock)

    # When
    query_has_valid_offer = find_filtered_venues(offer_status='VALID')

    # Then
    assert venue_with_valid_event in query_has_valid_offer
    assert venue_without_offer not in query_has_valid_offer
    assert venue_with_expired_event not in query_has_valid_offer
    assert venue_with_valid_thing in query_has_valid_offer
    assert venue_with_expired_thing not in query_has_valid_offer
    assert venue_with_soft_deleted_thing not in query_has_valid_offer
    assert venue_with_soft_deleted_event not in query_has_valid_offer
    assert venue_with_not_available_event not in query_has_valid_offer


@clean_database
def test_find_filtered_venues_with_offer_status_with_EXPIRED_param_return_filtered_venues(app):
    # Given
    offerer = create_offerer()

    venue_without_offer = create_venue(offerer)
    venue_with_valid_event = create_venue(offerer, siret='12345678912346')
    venue_with_expired_event = create_venue(offerer, siret='12345678912347')
    venue_with_valid_thing = create_venue(offerer, siret='12345678912348')
    venue_with_expired_thing = create_venue(offerer, siret='12345678912349')
    venue_with_soft_deleted_thing = create_venue(offerer, siret='12345678912342')
    venue_with_soft_deleted_event = create_venue(offerer, siret='12345678912343')
    venue_with_not_available_event = create_venue(offerer, siret='12345678912344')

    valid_event = create_offer_with_event_product(venue_with_valid_event)
    expired_event = create_offer_with_event_product(venue_with_expired_event)
    valid_thing = create_offer_with_thing_product(venue_with_valid_thing)
    expired_thing = create_offer_with_thing_product(venue_with_expired_thing)
    soft_deleted_thing = create_offer_with_thing_product(venue_with_soft_deleted_thing)
    soft_deleted_event = create_offer_with_event_product(venue_with_soft_deleted_event)
    not_available_event = create_offer_with_event_product(venue_with_not_available_event)

    valid_event_occurrence = create_event_occurrence(valid_event,
                                                     beginning_datetime=datetime.utcnow() + timedelta(days=4),
                                                     end_datetime=datetime.utcnow() + timedelta(days=5))
    valid_event_occurrence_soft_deleted = create_event_occurrence(soft_deleted_event,
                                                                  beginning_datetime=datetime.utcnow() + timedelta(
                                                                      days=4),
                                                                  end_datetime=datetime.utcnow() + timedelta(days=5))
    valid_event_occurrence_not_available = create_event_occurrence(not_available_event,
                                                                   beginning_datetime=datetime.utcnow() + timedelta(
                                                                       days=4),
                                                                   end_datetime=datetime.utcnow() + timedelta(days=5))
    expired_event_occurence = create_event_occurrence(expired_event,
                                                      beginning_datetime=datetime(2018, 2, 1),
                                                      end_datetime=datetime(2018, 3, 2))

    valid_stock = create_stock_with_thing_offer(offerer, venue_with_valid_thing, valid_thing)
    expired_stock = create_stock_with_thing_offer(offerer, venue_with_expired_thing, expired_thing, available=0)
    soft_deleted_thing_stock = create_stock_with_thing_offer(offerer, venue_with_soft_deleted_thing, soft_deleted_thing,
                                                             soft_deleted=True)

    expired_booking_limit_date_event_stock = create_stock_from_event_occurrence(expired_event_occurence,
                                                                                booking_limit_date=datetime(2018, 1, 1))
    valid_booking_limit_date_event_stock = create_stock_from_event_occurrence(valid_event_occurrence,
                                                                              booking_limit_date=datetime.utcnow() + timedelta(
                                                                                  days=3))
    soft_deleted_event_stock = create_stock_from_event_occurrence(valid_event_occurrence_soft_deleted,
                                                                  soft_deleted=True,
                                                                  booking_limit_date=datetime.utcnow() + timedelta(
                                                                      days=3))
    not_available_event_stock = create_stock_from_event_occurrence(valid_event_occurrence_not_available,
                                                                   available=0,
                                                                   booking_limit_date=datetime.utcnow() + timedelta(
                                                                       days=3))

    PcObject.save(venue_without_offer,
                  valid_stock, expired_stock, soft_deleted_thing_stock,
                  expired_booking_limit_date_event_stock,
                  valid_booking_limit_date_event_stock, soft_deleted_event_stock)

    # When
    query_has_expired_offer = find_filtered_venues(offer_status='EXPIRED')

    # Then
    assert venue_with_valid_event not in query_has_expired_offer
    assert venue_without_offer not in query_has_expired_offer
    assert venue_with_expired_event in query_has_expired_offer
    assert venue_with_valid_thing not in query_has_expired_offer
    assert venue_with_expired_thing in query_has_expired_offer
    assert venue_with_soft_deleted_thing in query_has_expired_offer
    assert venue_with_soft_deleted_event in query_has_expired_offer
    assert venue_with_not_available_event in query_has_expired_offer


@clean_database
def test_find_filtered_venues_with_offer_status_with_WITHOUT_param_return_filtered_venues(app):
    # Given
    offerer = create_offerer()

    venue_without_offer = create_venue(offerer)
    venue_with_valid_event = create_venue(offerer, siret='12345678912346')
    venue_with_expired_event = create_venue(offerer, siret='12345678912347')
    venue_with_valid_thing = create_venue(offerer, siret='12345678912348')
    venue_with_expired_thing = create_venue(offerer, siret='12345678912349')
    venue_with_soft_deleted_thing = create_venue(offerer, siret='12345678912342')
    venue_with_soft_deleted_event = create_venue(offerer, siret='12345678912343')
    venue_with_not_available_event = create_venue(offerer, siret='12345678912344')

    valid_event = create_offer_with_event_product(venue_with_valid_event)
    expired_event = create_offer_with_event_product(venue_with_expired_event)
    valid_thing = create_offer_with_thing_product(venue_with_valid_thing)
    expired_thing = create_offer_with_thing_product(venue_with_expired_thing)
    soft_deleted_thing = create_offer_with_thing_product(venue_with_soft_deleted_thing)
    soft_deleted_event = create_offer_with_event_product(venue_with_soft_deleted_event)
    not_available_event = create_offer_with_event_product(venue_with_not_available_event)

    valid_event_occurrence = create_event_occurrence(valid_event,
                                                     beginning_datetime=datetime.utcnow() + timedelta(days=4),
                                                     end_datetime=datetime.utcnow() + timedelta(days=5))
    valid_event_occurrence_soft_deleted = create_event_occurrence(soft_deleted_event,
                                                                  beginning_datetime=datetime.utcnow() + timedelta(
                                                                      days=4),
                                                                  end_datetime=datetime.utcnow() + timedelta(days=5))
    valid_event_occurrence_not_available = create_event_occurrence(not_available_event,
                                                                   beginning_datetime=datetime.utcnow() + timedelta(
                                                                       days=4),
                                                                   end_datetime=datetime.utcnow() + timedelta(days=5))
    expired_event_occurence = create_event_occurrence(expired_event,
                                                      beginning_datetime=datetime(2018, 2, 1),
                                                      end_datetime=datetime(2018, 3, 2))

    valid_stock = create_stock_with_thing_offer(offerer, venue_with_valid_thing, valid_thing)
    expired_stock = create_stock_with_thing_offer(offerer, venue_with_expired_thing, expired_thing, available=0)
    soft_deleted_thing_stock = create_stock_with_thing_offer(offerer, venue_with_soft_deleted_thing, soft_deleted_thing,
                                                             soft_deleted=True)

    expired_booking_limit_date_event_stock = create_stock_from_event_occurrence(expired_event_occurence,
                                                                                booking_limit_date=datetime(2018, 1, 1))
    valid_booking_limit_date_event_stock = create_stock_from_event_occurrence(valid_event_occurrence,
                                                                              booking_limit_date=datetime.utcnow() + timedelta(
                                                                                  days=3))
    soft_deleted_event_stock = create_stock_from_event_occurrence(valid_event_occurrence_soft_deleted,
                                                                  soft_deleted=True,
                                                                  booking_limit_date=datetime.utcnow() + timedelta(
                                                                      days=3))
    not_available_event_stock = create_stock_from_event_occurrence(valid_event_occurrence_not_available,
                                                                   available=0,
                                                                   booking_limit_date=datetime.utcnow() + timedelta(
                                                                       days=3))

    PcObject.save(venue_without_offer,
                  valid_stock, expired_stock, soft_deleted_thing_stock,
                  expired_booking_limit_date_event_stock,
                  valid_booking_limit_date_event_stock, soft_deleted_event_stock)

    # When
    query_without_offer = find_filtered_venues(offer_status='WITHOUT')

    # Then
    assert venue_with_valid_event not in query_without_offer
    assert venue_without_offer in query_without_offer
    assert venue_with_expired_event not in query_without_offer
    assert venue_with_valid_thing not in query_without_offer
    assert venue_with_expired_thing not in query_without_offer
    assert venue_with_soft_deleted_thing not in query_without_offer
    assert venue_with_soft_deleted_event not in query_without_offer
    assert venue_with_not_available_event not in query_without_offer


@clean_database
def test_find_filtered_venues_with_offer_status_with_ALL_param_return_filtered_venues(app):
    # Given
    offerer = create_offerer()

    venue_without_offer = create_venue(offerer)
    venue_with_valid_event = create_venue(offerer, siret='12345678912346')
    venue_with_expired_event = create_venue(offerer, siret='12345678912347')
    venue_with_valid_thing = create_venue(offerer, siret='12345678912348')
    venue_with_expired_thing = create_venue(offerer, siret='12345678912349')
    venue_with_soft_deleted_thing = create_venue(offerer, siret='12345678912342')
    venue_with_soft_deleted_event = create_venue(offerer, siret='12345678912343')
    venue_with_not_available_event = create_venue(offerer, siret='12345678912344')

    valid_event = create_offer_with_event_product(venue_with_valid_event)
    expired_event = create_offer_with_event_product(venue_with_expired_event)
    valid_thing = create_offer_with_thing_product(venue_with_valid_thing)
    expired_thing = create_offer_with_thing_product(venue_with_expired_thing)
    soft_deleted_thing = create_offer_with_thing_product(venue_with_soft_deleted_thing)
    soft_deleted_event = create_offer_with_event_product(venue_with_soft_deleted_event)
    not_available_event = create_offer_with_event_product(venue_with_not_available_event)

    valid_event_occurrence = create_event_occurrence(valid_event,
                                                     beginning_datetime=datetime.utcnow() + timedelta(days=4),
                                                     end_datetime=datetime.utcnow() + timedelta(days=5))
    valid_event_occurrence_soft_deleted = create_event_occurrence(soft_deleted_event,
                                                                  beginning_datetime=datetime.utcnow() + timedelta(
                                                                      days=4),
                                                                  end_datetime=datetime.utcnow() + timedelta(days=5))
    valid_event_occurrence_not_available = create_event_occurrence(not_available_event,
                                                                   beginning_datetime=datetime.utcnow() + timedelta(
                                                                       days=4),
                                                                   end_datetime=datetime.utcnow() + timedelta(days=5))
    expired_event_occurence = create_event_occurrence(expired_event,
                                                      beginning_datetime=datetime(2018, 2, 1),
                                                      end_datetime=datetime(2018, 3, 2))

    valid_stock = create_stock_with_thing_offer(offerer, venue_with_valid_thing, valid_thing)
    expired_stock = create_stock_with_thing_offer(offerer, venue_with_expired_thing, expired_thing, available=0)
    soft_deleted_thing_stock = create_stock_with_thing_offer(offerer, venue_with_soft_deleted_thing, soft_deleted_thing,
                                                             soft_deleted=True)

    expired_booking_limit_date_event_stock = create_stock_from_event_occurrence(expired_event_occurence,
                                                                                booking_limit_date=datetime(2018, 1, 1))
    valid_booking_limit_date_event_stock = create_stock_from_event_occurrence(valid_event_occurrence,
                                                                              booking_limit_date=datetime.utcnow() + timedelta(
                                                                                  days=3))
    soft_deleted_event_stock = create_stock_from_event_occurrence(valid_event_occurrence_soft_deleted,
                                                                  soft_deleted=True,
                                                                  booking_limit_date=datetime.utcnow() + timedelta(
                                                                      days=3))
    not_available_event_stock = create_stock_from_event_occurrence(valid_event_occurrence_not_available,
                                                                   available=0,
                                                                   booking_limit_date=datetime.utcnow() + timedelta(
                                                                       days=3))

    PcObject.save(venue_without_offer,
                  valid_stock, expired_stock, soft_deleted_thing_stock,
                  expired_booking_limit_date_event_stock,
                  valid_booking_limit_date_event_stock, soft_deleted_event_stock)

    # When
    query_with_all_offer = find_filtered_venues(offer_status='ALL')

    # Then
    assert venue_with_valid_event in query_with_all_offer
    assert venue_without_offer not in query_with_all_offer
    assert venue_with_expired_event in query_with_all_offer
    assert venue_with_valid_thing in query_with_all_offer
    assert venue_with_expired_thing in query_with_all_offer
    assert venue_with_soft_deleted_thing in query_with_all_offer
    assert venue_with_soft_deleted_event in query_with_all_offer
    assert venue_with_not_available_event in query_with_all_offer


@clean_database
def test_find_filtered_venues_with_default_param_return_all_venues(app):
    # Given
    offerer = create_offerer()

    venue_with_valid_offer = create_venue(offerer)
    venue_without_offer = create_venue(offerer, siret='12345678912346')
    venue_with_expired_offer = create_venue(offerer, siret='12345678912347')
    venue_virtual = create_venue(offerer, is_virtual=True, siret=None)

    venue_without_siret = create_venue(offerer, siret=None, comment="comment")
    venue_93000 = create_venue(offerer, postal_code='93000', siret='12345678912348')
    venue_67000 = create_venue(offerer, postal_code='67000', siret='12345678912349')
    venue_34000 = create_venue(offerer, postal_code='34000', siret='12345678912350')
    venue_97000 = create_venue(offerer, postal_code='97000', siret='12345678912351')

    valid_offer = create_offer_with_event_product(venue_with_valid_offer)
    expired_offer = create_offer_with_event_product(venue_with_expired_offer)

    PcObject.save(venue_with_valid_offer, venue_without_offer,
                  venue_virtual, venue_97000, venue_without_siret, venue_93000,
                  venue_67000, venue_34000)

    # When
    default_query = find_filtered_venues()

    # Then
    assert venue_with_valid_offer in default_query
    assert venue_without_offer in default_query
    assert venue_virtual in default_query
    assert venue_97000 in default_query
    assert venue_without_siret in default_query
    assert venue_93000 in default_query
    assert venue_67000 in default_query
    assert venue_34000 in default_query

class FindVenuesByManagingUserTest:
    @clean_database
    def test_returns_venues_that_a_user_manages(self):
        # given
        user = create_user(email='user@example.net')

        managed_offerer = create_offerer(name='Shakespear company', siren='987654321')
        managed_user_offerer = create_user_offerer(user, managed_offerer)
        managed_venue = create_venue(managed_offerer, name='National Shakespear Theater', siret='98765432112345')

        non_managed_offerer = create_offerer(name='Bookshop', siren='123456789')
        other_user = create_user(email='bookshop.pro@example.net')
        non_managed_user_offerer = create_user_offerer(other_user, non_managed_offerer)
        non_managed_venue = create_venue(non_managed_offerer, name='Contes et légendes', siret='12345678912345')

        PcObject.save(managed_user_offerer, managed_venue, non_managed_user_offerer, non_managed_venue)

        # when
        venues = find_by_managing_user(user)

        # then
        assert len(venues) == 1
        assert venues[0] == managed_venue
