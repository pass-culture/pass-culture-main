import os
from datetime import datetime

import pytest
import requests

from models import PcObject
from tests.conftest import clean_database
from utils.test_utils import API_URL, create_user, req_with_auth, create_user_offerer, \
    create_offerer, create_venue, create_event_occurrence, create_event_offer, create_venue_activity
from tests.repository_venue_queries_test import _save_all_activities

TOKEN = os.environ.get('EXPORT_TOKEN')



@pytest.mark.standalone
@clean_database
def test_export_model_returns_200_when_given_model_is_known(app):
    # given
    user = create_user(password='p@55sw0rd')
    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    # when
    response = auth_request.get(API_URL + '/exports/models/%s?token=%s' % ('Venue', TOKEN))

    # then
    assert response.status_code == 200


@pytest.mark.standalone
@clean_database
def test_export_model_returns_400_when_given_model_is_not_exportable(app):
    # given
    user = create_user(password='p@55sw0rd')
    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    # when
    response = auth_request.get(API_URL + '/exports/models/%s?token=%s' % ('VersionedMixin', TOKEN))

    # then
    assert response.status_code == 400
    assert response.json()['global'] == ['Classe non exportable : VersionedMixin']


@pytest.mark.standalone
@clean_database
def test_export_model_returns_bad_request_if_no_token_provided(app):
    # when
    response = requests.get(API_URL + '/exports/models/%s' % ('Venue'), headers={'origin':
       'http://localhost:3000'})

    # then
    assert response.status_code == 400


@pytest.mark.standalone
@clean_database
def test_export_model_returns_400_when_given_model_is_unknown(app):
    # given
    user = create_user(password='p@55sw0rd')
    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    # when
    response = auth_request.get(API_URL + '/exports/models/%s?token=%s' % ('RandomStuff', TOKEN))

    # then
    assert response.status_code == 400
    assert response.json()['global'] == ['Classe inconnue : RandomStuff']


@pytest.mark.standalone
@clean_database
def test_check_pending_validation_returns_403_when_user_is_not_admin(app):
    #given
    user = create_user(password='p@55sw0rd', is_admin=False)
    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    #when
    response = auth_request.get(API_URL + '/exports/pending_validation')

    #then
    assert response.status_code == 403


@pytest.mark.standalone
@clean_database
def test_check_pending_validation_returns_200_when_user_is_admin(app):
    #given
    user = create_user(can_book_free_offers=False, password='p@55sw0rd', is_admin=True)
    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    #when
    response = auth_request.get(API_URL + '/exports/pending_validation')

    #then
    assert response.status_code == 200


@pytest.mark.standalone
@clean_database
def test_check_pending_validation_returns_403_when_user_is_structure_admin_but_not_admin(app):
    #given
    user = create_user(can_book_free_offers=False, password='p@55sw0rd', is_admin=False)
    offerer = create_offerer()
    user_offerer = create_user_offerer(user, offerer, is_admin=True)
    PcObject.check_and_save(user_offerer)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    #when
    response = auth_request.get(API_URL + '/exports/pending_validation')

    #then
    assert response.status_code == 403


@pytest.mark.standalone
@clean_database
def test_check_pending_validation_return_200_and_validation_token(app):
    #given
    user = create_user(can_book_free_offers=False, password='p@55sw0rd', is_admin=True)
    user_pro = create_user(email='user0@test.com', can_book_free_offers=False, password='p@55sw0rd', is_admin=False)
    offerer = create_offerer(validation_token="first_token")
    user_offerer = create_user_offerer(user_pro, offerer, is_admin=True, validation_token="a_token")

    PcObject.check_and_save(user_offerer,user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    #when
    response = auth_request.get(API_URL + '/exports/pending_validation')

    #then
    assert response.status_code == 200
    assert response.json()[0]["validationToken"] == "first_token"
    assert response.json()[0]["UserOfferers"][0]["validationToken"] == "a_token"


@pytest.mark.standalone
@clean_database
def test_get_venues_returns_403_when_user_is_not_admin(app):
    #given
    data={}
    user = create_user(password='p@55sw0rd', is_admin=False)
    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    #when
    response = auth_request.post(API_URL + '/exports/venues', json=data)

    #then
    assert response.status_code == 403


@pytest.mark.standalone
@clean_database
def test_get_venues_returns_403_when_user_is_structure_admin_but_not_admin(app):
    #given
    data={}
    user = create_user(is_admin=False, can_book_free_offers=False)
    offerer = create_offerer()
    user_offerer = create_user_offerer(user, offerer, is_admin=True)
    venue = create_venue(offerer)
    PcObject.check_and_save(user_offerer, venue)
    auth_request = req_with_auth(email=user.email, password=user.clearTextPassword)

    #when
    response = auth_request.post(API_URL + '/exports/venues', json=data)

    #then
    assert response.status_code == 403


@pytest.mark.standalone
@clean_database
def test_get_venues_return_200_and_filtered_venues(app):
    #given
    data={
        "has_validated_offerer": True,
        "dpt": ["93","67"],
        "has_siret": True,
        "is_virtual": False,
        "is_validated": True, 
        "from_date": "2018-10-02",
        "to_date": "2018-12-31",
        "offer_status": "ALL"
    }

    user = create_user(password='p@55sw0rd', is_admin=True, can_book_free_offers=False)
    validated_offerer = create_offerer()
    not_validated_offerer = create_offerer(validation_token="here is a token", siren="123456798")

    venue93_with_offer_before_date_range = create_venue(validated_offerer,
       name='venue93_with_offer_before_date_range', postal_code='93100', siret="12345678912310")
    venue93_with_offer_after_date_range = create_venue(validated_offerer,
       name='venue93_with_offer_after_date_range', postal_code='93100', siret="12345678912311") 
    venue93_with_offer_in_date_range = create_venue(validated_offerer, 
       name='venue93_with_offer_in_date_range', postal_code='93100', siret="12345678912312")
    venue67_with_offer_before_date_range = create_venue(validated_offerer, 
       name='venue67_with_offer_before_date_range', postal_code='67100', siret="12345678912313")
    venue67_with_offer_in_date_range = create_venue(validated_offerer, name='venue67_with_offer_in_date_range',
       postal_code='67100', siret="12345678912314")
    venue67_without_offer_in_date_range = create_venue(validated_offerer, 
       name='venue67_without_offer_in_date_range', postal_code='67100', siret="12345678912315")
    venue34_with_offer_in_date_range = create_venue(validated_offerer, 
       name='venue34_with_offer_in_date_range', postal_code='34100', siret="12345678912316")
    venue_without_siret_with_offer_in_date_range = create_venue(validated_offerer, 
       name='venue_without_siret_with_offer_in_date_range', comment="here is a comment" , siret=None)
    venue_virtual_with_offer_in_date_range = create_venue(validated_offerer,
       name='venue_virtual_with_offer_in_date_range', siret=None, is_virtual=True)
    venue_not_validated_with_offer_in_date_range = create_venue(validated_offerer, name='venue_not_validated_with_offer_in_date_range', 
       validation_token="here is a validation_token", siret="12345678912317")
    venue_with_not_validated_offerer_in_date_range = create_venue(not_validated_offerer,
       name='venue_with_not_validated_offerer_in_date_range', siret="12345678912318")

    offer1 = create_event_offer(venue93_with_offer_before_date_range)
    offer2 = create_event_offer(venue93_with_offer_after_date_range)
    offer3 = create_event_offer(venue93_with_offer_in_date_range)
    offer4 = create_event_offer(venue67_with_offer_before_date_range)
    offer5 = create_event_offer(venue67_with_offer_in_date_range)
    offer6 = create_event_offer(venue34_with_offer_in_date_range)
    offer7 = create_event_offer(venue_without_siret_with_offer_in_date_range)
    offer8 = create_event_offer(venue_virtual_with_offer_in_date_range)
    offer9 = create_event_offer(venue_not_validated_with_offer_in_date_range)

    valid_event_occurrence1 = create_event_occurrence(offer1)
    valid_event_occurrence2 = create_event_occurrence(offer2)
    valid_event_occurrence3 = create_event_occurrence(offer3)
    valid_event_occurrence4 = create_event_occurrence(offer4)
    valid_event_occurrence5 = create_event_occurrence(offer5)
    valid_event_occurrence6 = create_event_occurrence(offer6)
    valid_event_occurrence7 = create_event_occurrence(offer7)
    valid_event_occurrence8 = create_event_occurrence(offer8)
    valid_event_occurrence9 = create_event_occurrence(offer9)

    PcObject.check_and_save(user, valid_event_occurrence1, valid_event_occurrence2, valid_event_occurrence3,
     valid_event_occurrence4, valid_event_occurrence5, valid_event_occurrence6, valid_event_occurrence7,
     valid_event_occurrence8, valid_event_occurrence9, venue_with_not_validated_offerer_in_date_range,
     venue67_without_offer_in_date_range)

    activity_in_date_range1 = create_venue_activity(venue93_with_offer_in_date_range, 'venue', 'insert',
       issued_at=datetime(2018, 11, 30))
    activity_in_date_range2 = create_venue_activity(venue67_with_offer_in_date_range, 'venue', 'insert',
       issued_at=datetime(2018, 11, 30))
    activity_in_date_range3 = create_venue_activity(venue67_without_offer_in_date_range, 'venue', 'insert',
       issued_at=datetime(2018, 11, 30))
    activity_in_date_range4 = create_venue_activity(venue34_with_offer_in_date_range, 'venue', 'insert',
       issued_at=datetime(2018, 11, 30))
    activity_in_date_range5 = create_venue_activity(venue_virtual_with_offer_in_date_range, 'venue', 'insert',
       issued_at=datetime(2018, 11, 30))
    activity_in_date_range6 = create_venue_activity(venue_not_validated_with_offer_in_date_range, 'venue', 'insert',
       issued_at=datetime(2018, 11, 30))
    activity_in_date_range7 = create_venue_activity(venue_with_not_validated_offerer_in_date_range, 'venue', 'insert',
       issued_at=datetime(2018, 11, 30))
    activity_before_date_range1 = create_venue_activity(venue93_with_offer_before_date_range, 'venue', 'insert',
       issued_at=datetime(2018, 6, 30))
    activity_before_date_range2 = create_venue_activity(venue67_with_offer_before_date_range, 'venue', 'insert',
       issued_at=datetime(2018, 6, 30))
    activity_after_date_range = create_venue_activity(venue93_with_offer_after_date_range, 'venue', 'insert',
       issued_at=datetime(2019, 8, 30))

    _save_all_activities(activity_in_date_range1, activity_in_date_range2, activity_in_date_range3,
      activity_in_date_range4, activity_in_date_range5, activity_in_date_range6,
      activity_in_date_range7, activity_before_date_range1, activity_before_date_range2, 
      activity_after_date_range)


    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    #when
    response = auth_request.post(API_URL + '/exports/venues', json=data)

    #then
    venue_names = list(map(lambda x: x['name'], response.json()))

    assert response.status_code == 200
    assert venue67_with_offer_in_date_range.name in venue_names
    assert venue93_with_offer_in_date_range.name in venue_names
    assert venue93_with_offer_before_date_range.name not in venue_names
    assert venue93_with_offer_after_date_range.name not in venue_names
    assert venue67_with_offer_before_date_range.name not in venue_names
    assert venue67_without_offer_in_date_range.name not in venue_names
    assert venue34_with_offer_in_date_range.name not in venue_names
    assert venue_without_siret_with_offer_in_date_range.name not in venue_names
    assert venue_virtual_with_offer_in_date_range.name not in venue_names
    assert venue_not_validated_with_offer_in_date_range.name not in venue_names
    assert venue_with_not_validated_offerer_in_date_range.name not in venue_names


@pytest.mark.standalone
@clean_database
def test_get_venues_return_error_when_date_param_is_wrong(app):
    #given
    wrong_date = "I\'m not a valid date"
    data = {'from_date': wrong_date}
    user = create_user(password='p@55sw0rd', is_admin=True, can_book_free_offers=False)

    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    #when
    response = auth_request.post(API_URL + '/exports/venues', json=data)

    #then
    assert response.status_code == 400
    assert response.json()['date_format'] == ['to_date and from_date are of type yyyy-mm-dd'] 
    