from pprint import pprint

from models import PcObject
from repository.offerer_queries import find_all_pending_validation
from routes.serializer import as_dict
from tests.conftest import clean_database
from tests.test_utils import create_user, create_offerer, create_user_offerer, create_product_with_event_type, \
    create_mediation, create_offer_with_event_product, create_venue
from utils.includes import OFFERER_FOR_PENDING_VALIDATION_INCLUDES


@clean_database
def test_serializer_as_dict_do_not_return_excluded_keys(app):
    user = create_user(postal_code=None)

    offerer = create_offerer()
    user_offerer = create_user_offerer(user, offerer)
    PcObject.save(user_offerer)

    USER_INCLUDES = [
        '-culturalSurveyId',
        '-password',
        '-resetPasswordToken',
        '-resetPasswordTokenValidityLimit',
        '-validationToken',
        'hasPhysicalVenues',
        'hasOffers',
        'wallet_balance',
        'wallet_is_activated'
    ]

    json_response = as_dict(user, include=USER_INCLUDES)

    assert 'culturalSurveyId' not in json_response
    assert 'resetPasswordToken' not in json_response
    assert 'resetPasswordTokenValidityLimit' not in json_response
    assert 'validationToken' not in json_response
    assert 'password' not in json_response

@clean_database
def test_serializer_as_dict_return_relationship(app):
    user = create_user()
    offerer = create_offerer()
    user_offerer = create_user_offerer(user, offerer)
    PcObject.save(user_offerer)

    USER_INCLUDES = [
        'offerers'
    ]

    json_response = as_dict(user, include=USER_INCLUDES)

    assert 'offerers' in json_response

@clean_database
def test_ftdc(app):
    mediation = create_mediation(None)
    mediation.firstThumbDominantColor = b'\x8900ff'

    json_response = as_dict(mediation)

    assert json_response['firstThumbDominantColor'] == [137, 48, 48, 102, 102]


@clean_database
def test_serializer_as_dict_with_sub_joins(app):
    offerer = create_offerer()
    venue = create_venue(offerer)
    event_product = create_product_with_event_type(event_name='My Event')
    offer = create_offer_with_event_product(venue, product=event_product)
    mediation = create_mediation(offer)
    PcObject.save(mediation)

    EVENT_INCLUDES = [
        {
            "key": "mediations",
            "sub_joins": ["thumbUrl", "-backText"]
        }
    ]

    json_response = as_dict(offer, include=EVENT_INCLUDES)

    assert 'mediations' in json_response
    assert 'thumbUrl' in json_response['mediations'][0]
    assert 'backText' not in json_response['mediations'][0]


@clean_database
def test_serializer_as_dict_with_one_resolve_in_include(app):
    user = create_user()
    offerer1 = create_offerer(validation_token='toto')
    offerer2 = create_offerer(siren='123456788', validation_token='tata')
    user_offerer1 = create_user_offerer(user, offerer1)
    user_offerer2 = create_user_offerer(user, offerer2)
    venue1 = create_venue(offerer1, validation_token='tototo')
    venue2 = create_venue(offerer2, siret='12345678812345', validation_token='totota')
    PcObject.save(user_offerer1, user_offerer2, venue1, venue2)

    RESOLVE_INCLUDES = [{
        "key": "managedVenues",
        "sub_joins":
            [
                'id', 'name', 'siret', 'managingOffererId', 'bookingEmail',
                'address', 'postalCode', 'city', 'departementCode', 'comment', 'validationToken'
            ]
    }]
    offerers = find_all_pending_validation()
    json_response = []
    for offerer in offerers:
        json_response.append(as_dict(offerer, include=RESOLVE_INCLUDES))

    assert isinstance(venue1, PcObject)
    assert 'managedVenues' in json_response[0]
    assert 'managedVenues' in json_response[1]


@clean_database
def test_serializer_as_dict_with_one_resolve_list_in_include(app):
    user1 = create_user()
    user2 = create_user(email='john.doe2@test.com')
    offerer1 = create_offerer(validation_token='toto')
    offerer2 = create_offerer(siren='123456788', validation_token='tata')
    user_offerer1 = create_user_offerer(user1, offerer1)
    user_offerer2 = create_user_offerer(user2, offerer1)
    user_offerer3 = create_user_offerer(user2, offerer2)
    venue1 = create_venue(offerer1, validation_token='tototo')
    venue2 = create_venue(offerer2, siret='12345678812345', validation_token='totota')
    PcObject.save(user_offerer1, user_offerer2, user_offerer3, venue1, venue2)

    RESOLVE_INCLUDES = [{
        "key": "UserOfferers",
        "sub_joins": [{
            "key": "user",
            "sub_joins": [
                'email', 'publicName', 'dateCreated', 'departementCode', 'canBookFreeOffers',
                'isAdmin', 'firstName', 'lastName', 'postalCode', 'phoneNumber', 'validationToken'
            ]
        }]
    }, ]
    offerers = find_all_pending_validation()
    json_response = []
    for offerer in offerers:
        json_response.append(as_dict(offerer, include=RESOLVE_INCLUDES))

    assert 'UserOfferers' in json_response[0]


@clean_database
def test_serializer_as_dict_with_multiple_resolve_in_include(app):
    user = create_user()
    offerer1 = create_offerer(validation_token='toto')
    offerer2 = create_offerer(siren='123456788', validation_token='tata')
    user_offerer1 = create_user_offerer(user, offerer1)
    user_offerer2 = create_user_offerer(user, offerer2)
    venue1 = create_venue(offerer1, validation_token='tototo')
    venue2 = create_venue(offerer2, siret='12345678812345', validation_token='totota')
    PcObject.save(user_offerer1, user_offerer2, venue1, venue2)

    offerers = find_all_pending_validation()
    json_response = []
    for offerer in offerers:
        json_response.append(as_dict(offerer, include=OFFERER_FOR_PENDING_VALIDATION_INCLUDES))

    pprint(json_response)
    assert 'UserOfferers' in json_response[0]
    assert 'managedVenues' in json_response[0]
