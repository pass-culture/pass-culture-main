""" repository venue queries """
from datetime import datetime
import pytest

from models import PcObject
from models.db import db

from repository.venue_queries import find_venues
from tests.conftest import clean_database
from utils.test_utils import create_venue, create_event_offer, create_venue_activity, \
    create_event_occurrence, create_offerer, create_thing_offer, create_stock_with_thing_offer


 
@pytest.mark.standalone
@clean_database
def test_find_venues_with_has_validated_offerer_param_return_filtered_venues(app):
    # Given
    offerer_valid = create_offerer()
    offerer_not_valid = create_offerer(siren='123456798', validation_token='abc')
    venue_with_offerer_valid = create_venue(offerer_valid)
    venue_with_offerer_not_valid = create_venue(offerer_not_valid, siret='12345679812345')
    PcObject.check_and_save(venue_with_offerer_valid, venue_with_offerer_not_valid)

    # When
    query_with_not_valid_offerer_only = find_venues(has_validated_offerer=False)

    # Then
    assert venue_with_offerer_valid not in query_with_not_valid_offerer_only 
    assert venue_with_offerer_not_valid in query_with_not_valid_offerer_only


@pytest.mark.standalone
@clean_database
def test_find_venues_with_dpt_param_return_filtered_venues(app):
    # Given
    offerer = create_offerer()
    venue_93 = create_venue(offerer, departement_code='93', postal_code='93000')
    venue_67 = create_venue(offerer, departement_code='67', postal_code='67000',
       siret='12345678912346')
    venue_34 = create_venue(offerer, departement_code='34', postal_code='34000',
       siret='12345678912347')
    venue_virtual = create_venue(offerer, is_virtual=True, siret=None, postal_code=None)
    PcObject.check_and_save(venue_93, venue_67, venue_34, venue_virtual)

    # When
    query_with_dpt = find_venues(dpt=['93','67'])

    # Then
    assert venue_93 in query_with_dpt
    assert venue_67 in query_with_dpt
    assert venue_34 not in query_with_dpt
    assert venue_virtual not in query_with_dpt 
    

@pytest.mark.standalone
@clean_database
def test_find_venues_with_zipcodes_param_return_filtered_venues(app):
    # Given
    offerer = create_offerer()
    venue_93000 = create_venue(offerer, postal_code='93000')
    venue_67000 = create_venue(offerer, postal_code='67000', siret='12345678912346')
    venue_34000 = create_venue(offerer, postal_code='34000', siret='12345678912347')
    venue_virtual = create_venue(offerer, is_virtual=True, siret=None)
    PcObject.check_and_save(venue_virtual, venue_93000, venue_67000, venue_34000)

    # When
    query_with_zipcodes = find_venues(zip_codes=['93000', '34000'])

    # Then
    assert venue_93000 in query_with_zipcodes
    assert venue_34000 in query_with_zipcodes
    assert venue_virtual not in query_with_zipcodes
    assert venue_67000 not in query_with_zipcodes


@pytest.mark.standalone
@clean_database
def test_find_venues_with_date_params_return_filtered_venues(app):
    # Given
    offerer = create_offerer()
    venue_20180630 = create_venue(offerer)
    venue_20180730 = create_venue(offerer, siret='12345678912346')
    venue_20180830 = create_venue(offerer, siret='12345678912347')
    PcObject.check_and_save(venue_20180630, venue_20180730, venue_20180830)

    activity1 = create_venue_activity(venue_20180630, 'venue', 'insert', issued_at=datetime(2018,
        6, 30))
    activity2 = create_venue_activity(venue_20180730, 'venue', 'insert', issued_at=datetime(2018,
        7, 30))
    activity3 = create_venue_activity(venue_20180830, 'venue', 'insert', issued_at=datetime(2018,
        8, 30))
    _save_all_activities(activity1, activity2, activity3)

    # When
    query_with_date = find_venues(from_date='2018-07-01',
        to_date='2018-08-01')

    # Then
    assert venue_20180630 not in query_with_date
    assert venue_20180830 not in query_with_date
    assert venue_20180730 in query_with_date


@pytest.mark.standalone
@clean_database
def test_find_venues_with_is_virtual_param_return_filtered_venues(app):
    # Given
    offerer = create_offerer()
    venue_virtual = create_venue(offerer, is_virtual=True, siret=None)
    venue_not_virtual = create_venue(offerer, is_virtual=False, postal_code='34000')
    PcObject.check_and_save(venue_virtual, venue_not_virtual)

    # When
    query_only_virtual = find_venues(is_virtual=True)
    
    # Then
    assert venue_virtual in query_only_virtual 
    assert venue_not_virtual not in query_only_virtual


@pytest.mark.standalone
@clean_database
def test_find_venues_with_has_siret_param_return_filtered_venues(app):
    # Given
    offerer = create_offerer()
    venue_virtual = create_venue(offerer, is_virtual=True, siret=None)
    venue_with_siret = create_venue(offerer)
    venue_without_siret = create_venue(offerer, siret=None, comment="comment", is_virtual=False)
    PcObject.check_and_save(venue_virtual, venue_with_siret, venue_without_siret)
    
    # When
    query_no_siret = find_venues(has_siret=False)

    # Then
    assert venue_without_siret in query_no_siret
    assert venue_virtual in query_no_siret
    assert venue_with_siret not in query_no_siret


@pytest.mark.standalone
@clean_database
def test_find_venues_with_is_validated_param_return_filtered_venues(app):
    # Given
    offerer = create_offerer()
    venue_not_validated = create_venue(offerer, validation_token="there is a token here")
    venue_validated = create_venue(offerer, siret='12345678912346')
    PcObject.check_and_save(venue_not_validated, venue_validated)
    
    # When
    query_only_validated = find_venues(is_validated=True)

    # Then
    assert venue_not_validated not in query_only_validated 
    assert venue_validated in query_only_validated 


@pytest.mark.standalone
@clean_database
def test_find_venues_with_has_offer_with_VALID_param_return_filtered_venues(app):
    # Given
    offerer = create_offerer()

    venue_without_offer = create_venue(offerer)
    venue_with_valid_event = create_venue(offerer, siret='12345678912346')
    venue_with_expired_event = create_venue(offerer, siret='12345678912347')
    venue_with_valid_thing = create_venue(offerer, siret='12345678912348')
    venue_with_expired_thing = create_venue(offerer, siret='12345678912349')

    valid_event = create_event_offer(venue_with_valid_event)
    expired_event = create_event_offer(venue_with_expired_event)
    valid_thing = create_thing_offer(venue_with_valid_thing)
    expired_thing = create_thing_offer(venue_with_expired_thing)

    valid_event_occurrence = create_event_occurrence(valid_event)
    expired_event_occurence = create_event_occurrence(expired_event,
       beginning_datetime=datetime(2018,1,1), end_datetime=datetime(2018,2,2))
    valid_stock = create_stock_with_thing_offer(offerer, venue_with_valid_thing, valid_thing)
    expired_stock = create_stock_with_thing_offer(offerer, venue_with_expired_thing, expired_thing,
       available=0)

    PcObject.check_and_save(venue_without_offer, valid_event_occurrence, expired_event_occurence,
        valid_stock, expired_stock)
   
    # When
    query_has_valid_offer = find_venues(has_offer='VALID')
   
    # Then
    assert venue_with_valid_event in query_has_valid_offer
    assert venue_without_offer not in query_has_valid_offer
    assert venue_with_expired_event not in query_has_valid_offer 
    assert venue_with_valid_thing in query_has_valid_offer
    assert venue_with_expired_thing not in query_has_valid_offer


@pytest.mark.standalone
@clean_database
def test_find_venues_with_has_offer_with_EXPIRED_param_return_filtered_venues(app):
    # Given
    offerer = create_offerer()

    venue_without_offer = create_venue(offerer)
    venue_with_valid_event = create_venue(offerer, siret='12345678912346')
    venue_with_expired_event = create_venue(offerer, siret='12345678912347')
    venue_with_valid_thing = create_venue(offerer, siret='12345678912348')
    venue_with_expired_thing = create_venue(offerer, siret='12345678912349')

    valid_event = create_event_offer(venue_with_valid_event)
    expired_event = create_event_offer(venue_with_expired_event)
    valid_thing = create_thing_offer(venue_with_valid_thing)
    expired_thing = create_thing_offer(venue_with_expired_thing)

    valid_event_occurrence = create_event_occurrence(valid_event)
    expired_event_occurence = create_event_occurrence(expired_event,
       beginning_datetime=datetime(2018,1,1), end_datetime=datetime(2018,2,2))
    valid_stock = create_stock_with_thing_offer(offerer, venue_with_valid_thing, valid_thing)
    expired_stock = create_stock_with_thing_offer(offerer, venue_with_expired_thing, expired_thing,
       available=0)

    PcObject.check_and_save(venue_without_offer, valid_event_occurrence, expired_event_occurence,
        valid_stock, expired_stock)
   
    # When
    query_has_expired_offer = find_venues(has_offer='EXPIRED')
   
    # Then
    assert venue_with_valid_event not in query_has_expired_offer
    assert venue_without_offer not in query_has_expired_offer
    assert venue_with_expired_event in query_has_expired_offer
    assert venue_with_valid_thing not in query_has_expired_offer
    assert venue_with_expired_thing in query_has_expired_offer


@pytest.mark.standalone
@clean_database
def test_find_venues_with_has_offer_with_WITHOUT_param_return_filtered_venues(app):
    # Given
    offerer = create_offerer()

    venue_without_offer = create_venue(offerer)
    venue_with_valid_event = create_venue(offerer, siret='12345678912346')
    venue_with_expired_event = create_venue(offerer, siret='12345678912347')
    venue_with_valid_thing = create_venue(offerer, siret='12345678912348')
    venue_with_expired_thing = create_venue(offerer, siret='12345678912349')

    valid_event = create_event_offer(venue_with_valid_event)
    expired_event = create_event_offer(venue_with_expired_event)
    valid_thing = create_thing_offer(venue_with_valid_thing)
    expired_thing = create_thing_offer(venue_with_expired_thing)

    valid_event_occurrence = create_event_occurrence(valid_event)
    expired_event_occurence = create_event_occurrence(expired_event,
       beginning_datetime=datetime(2018,1,1), end_datetime=datetime(2018,2,2))
    valid_stock = create_stock_with_thing_offer(offerer, venue_with_valid_thing, valid_thing)
    expired_stock = create_stock_with_thing_offer(offerer, venue_with_expired_thing, expired_thing,
       available=0)

    PcObject.check_and_save(venue_without_offer, valid_event_occurrence, expired_event_occurence,
        valid_stock, expired_stock)
   
    # When
    query_without_offer = find_venues(has_offer='WITHOUT')
   
    # Then
    assert venue_with_valid_event not in query_without_offer
    assert venue_without_offer in query_without_offer
    assert venue_with_expired_event not in query_without_offer
    assert venue_with_valid_thing not in query_without_offer
    assert venue_with_expired_thing not in query_without_offer


@pytest.mark.standalone
@clean_database
def test_find_venues_with_has_offer_with_ALL_param_return_filtered_venues(app):
    # Given
    offerer = create_offerer()

    venue_without_offer = create_venue(offerer)
    venue_with_valid_event = create_venue(offerer, siret='12345678912346')
    venue_with_expired_event = create_venue(offerer, siret='12345678912347')
    venue_with_valid_thing = create_venue(offerer, siret='12345678912348')
    venue_with_expired_thing = create_venue(offerer, siret='12345678912349')

    valid_event = create_event_offer(venue_with_valid_event)
    expired_event = create_event_offer(venue_with_expired_event)
    valid_thing = create_thing_offer(venue_with_valid_thing)
    expired_thing = create_thing_offer(venue_with_expired_thing)

    valid_event_occurrence = create_event_occurrence(valid_event)
    expired_event_occurence = create_event_occurrence(expired_event,
       beginning_datetime=datetime(2018,1,1), end_datetime=datetime(2018,2,2))
    valid_stock = create_stock_with_thing_offer(offerer, venue_with_valid_thing, valid_thing)
    expired_stock = create_stock_with_thing_offer(offerer, venue_with_expired_thing, expired_thing,
       available=0)

    PcObject.check_and_save(venue_without_offer, valid_event_occurrence, expired_event_occurence,
        valid_stock, expired_stock)
   
    # When
    query_all = find_venues(has_offer='ALL')
   
    # Then
    assert venue_with_valid_event in query_all 
    assert venue_without_offer not in query_all 
    assert venue_with_expired_event in query_all 
    assert venue_with_valid_thing in query_all
    assert venue_with_expired_thing in query_all



@pytest.mark.standalone
@clean_database
def test_find_venues_with_default_param_return_all_venues(app):
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

    valid_offer = create_event_offer(venue_with_valid_offer)
    expired_offer = create_event_offer(venue_with_expired_offer)
    valid_event_occurrence = create_event_occurrence(valid_offer)
    expired_event_occurence = create_event_occurrence(expired_offer,
       beginning_datetime=datetime(2018,1,1), end_datetime=datetime(2018,2,2))

    PcObject.check_and_save(venue_with_valid_offer, venue_without_offer, valid_event_occurrence,
        expired_event_occurence, venue_virtual, venue_97000, venue_without_siret, venue_93000,
        venue_67000, venue_34000)
   
    # When
    default_query = find_venues()

    # Then
    assert venue_with_valid_offer in default_query
    assert venue_without_offer in default_query
    assert venue_virtual in default_query
    assert venue_97000 in default_query
    assert venue_without_siret in default_query
    assert venue_93000 in default_query
    assert venue_67000 in default_query
    assert venue_34000 in default_query


def _save_all_activities(*objects):
    for obj in objects:
        db.session.add(obj)
    db.session.commit()
