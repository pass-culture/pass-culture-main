from datetime import datetime
from unittest.mock import patch

import pytest

from pcapi.model_creators.activity_creators import create_venue_activity
from pcapi.model_creators.activity_creators import save_all_activities
from pcapi.model_creators.generic_creators import create_bank_information
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_event_occurrence
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_stock_from_event_occurrence
from pcapi.model_creators.specific_creators import create_stock_with_event_offer
from pcapi.model_creators.specific_creators import create_stock_with_thing_offer
from pcapi.models import Offerer
from pcapi.models import VenueSQLEntity
from pcapi.repository import repository
from pcapi.routes.serialization import serialize
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


fake_export_token = 'fake'

@pytest.mark.usefixtures("db_session")
@patch.dict('os.environ', {'EXPORT_TOKEN': fake_export_token})
def test_export_model_returns_200_when_given_model_is_known(app):
    # given
    user = create_user()
    repository.save(user)
    auth_request = TestClient(app.test_client()).with_auth(email=user.email)

    # when
    response = auth_request.get('/exports/models/%s?token=%s' % ('VenueSQLEntity', fake_export_token))

    # then
    assert response.status_code == 200


@pytest.mark.usefixtures("db_session")
@patch.dict('os.environ', {'EXPORT_TOKEN': fake_export_token})
def test_export_model_returns_400_when_given_model_is_not_exportable(app):
    # given
    user = create_user()
    repository.save(user)
    auth_request = TestClient(app.test_client()).with_auth(email=user.email)

    # when
    response = auth_request.get('/exports/models/%s?token=%s' % ('VersionedMixin', fake_export_token))

    # then
    assert response.status_code == 400
    assert response.json['global'] == ['Classe non exportable : VersionedMixin']


@pytest.mark.usefixtures("db_session")
@patch.dict('os.environ', {'EXPORT_TOKEN': fake_export_token})
def test_export_model_returns_bad_request_if_no_token_provided(app):
    # when
    response = TestClient(app.test_client()).get('/exports/models/%s' % ('Venue'), headers={'origin':
                                                                                                'http://localhost:3000'})

    # then
    assert response.status_code == 400


@pytest.mark.usefixtures("db_session")
@patch.dict('os.environ', {'EXPORT_TOKEN': fake_export_token})
def test_export_model_returns_400_when_given_model_is_unknown(app):
    # given
    user = create_user()
    repository.save(user)
    auth_request = TestClient(app.test_client()).with_auth(email=user.email)

    # when
    response = auth_request.get('/exports/models/%s?token=%s' % ('RandomStuff', fake_export_token))

    # then
    assert response.status_code == 400
    assert response.json['global'] == ['Classe inconnue : RandomStuff']


@pytest.mark.usefixtures("db_session")
def test_pending_validation_returns_403_when_user_is_not_admin(app):
    # given
    user = create_user(is_admin=False)
    repository.save(user)
    auth_request = TestClient(app.test_client()).with_auth(email=user.email)

    # when
    response = auth_request.get('/exports/pending_validation')

    # then
    assert response.status_code == 403


@pytest.mark.usefixtures("db_session")
def test_pending_validation_returns_200_when_user_is_admin(app):
    # given
    user = create_user(can_book_free_offers=False, is_admin=True)
    repository.save(user)
    auth_request = TestClient(app.test_client()).with_auth(email=user.email)

    # when
    response = auth_request.get('/exports/pending_validation')

    # then
    assert response.status_code == 200


@pytest.mark.usefixtures("db_session")
def test_pending_validation_returns_403_when_user_is_structure_admin_but_not_admin(app):
    # given
    user = create_user(can_book_free_offers=False, is_admin=False)
    offerer = create_offerer()
    user_offerer = create_user_offerer(user, offerer, is_admin=True)
    repository.save(user_offerer)
    auth_request = TestClient(app.test_client()).with_auth(email=user.email)

    # when
    response = auth_request.get('/exports/pending_validation')

    # then
    assert response.status_code == 403


@pytest.mark.usefixtures("db_session")
def test_pending_validation_return_200_and_validation_token(app):
    # given
    user = create_user(can_book_free_offers=False, is_admin=True)
    user_pro = create_user(can_book_free_offers=False, email='user0@test.com', is_admin=False)
    offerer = create_offerer(validation_token="first_token")
    user_offerer = create_user_offerer(user_pro, offerer, is_admin=True, validation_token="a_token")
    venue = create_venue(offerer, siret=None, comment="comment because no siret",
                         validation_token="venue_validation_token")

    repository.save(user_offerer, user, venue)
    auth_request = TestClient(app.test_client()).with_auth(email=user.email)

    # when
    response = auth_request.get('/exports/pending_validation')

    # then
    assert response.status_code == 200
    assert response.json[0]["validationToken"] == "first_token"
    assert response.json[0]["UserOfferers"][0]["validationToken"] == "a_token"


@pytest.mark.usefixtures("db_session")
def test_pending_validation_return_only_requested_data(app):
    # given
    user = create_user(can_book_free_offers=False, is_admin=True)
    user_pro = create_user(can_book_free_offers=False, email='user0@test.com', is_admin=False, first_name='John', last_name='Doe', phone_number='0612345678', postal_code='93100')
    offerer = create_offerer(validation_token='first_token', address='123 rue de Paris')
    user_offerer = create_user_offerer(user_pro, offerer, is_admin=True)
    venue = create_venue(offerer, siret=None, comment='comment because no siret',
                         validation_token='venue_validation_token', booking_email='john.doe@test.com')
    repository.save(user, user_pro, offerer)

    expected_result = {
        'isActive': True,
        'dateModifiedAtLastProvider': serialize(offerer.dateModifiedAtLastProvider),
        'fieldsUpdated': [],
        'address': '123 rue de Paris',
        'postalCode': '93100',
        'city': 'Montreuil',
        'validationToken': 'first_token',
        'id': humanize(offerer.id),
        'dateCreated': serialize(offerer.dateCreated),
        'name': 'Test Offerer',
        'siren': '123456789',
        'lastProviderId': None,
        'UserOfferers':
            [{'id': humanize(user_offerer.id),
              'validationToken': None,
              'userId': humanize(user_pro.id),
              'offererId': humanize(offerer.id),
              'rights': 'admin',
              'user':
                  {'canBookFreeOffers': False,
                   'activity': None,
                   'address': None,
                   'city': None,
                   'civility': None,
                   'dateCreated': serialize(user_pro.dateCreated),
                   'departementCode': '93',
                   'email': 'user0@test.com',
                   'firstName': 'John',
                   'isAdmin': False,
                   'lastName': 'Doe',
                   'lastConnectionDate': None,
                   'phoneNumber': '0612345678',
                   'postalCode': '93100',
                   'publicName': 'John Doe',
                   'validationToken': None,
                   'culturalSurveyId': None,
                   'culturalSurveyFilledDate': None,
                   'needsToFillCulturalSurvey': False,
                   'hasSeenTutorials': None
                   }}],
        'managedVenues':
            [{'address': '123 rue de Paris',
              'bookingEmail': 'john.doe@test.com',
              'city': 'Montreuil',
              'comment': 'comment because no siret',
              'dateCreated': serialize(venue.dateCreated),
              'departementCode': '93',
              'fieldsUpdated': [],
              'id': humanize(venue.id),
              'managingOffererId': humanize(offerer.id),
              'name': 'La petite librairie',
              'postalCode': '93100',
              'siret': None,
              'validationToken': 'venue_validation_token',
              'venueTypeId': None,
              'venueLabelId': None,
              }]
    }

    auth_request = TestClient(app.test_client()).with_auth(email=user.email)
    # when
    response = auth_request.get('/exports/pending_validation')

    # then
    assert response.status_code == 200
    assert response.json[0] == expected_result


@pytest.mark.usefixtures("db_session")
def test_pending_validation_returns_offerers_venues_user_and_user_offerer_with_requested_data(app):
    # given
    connexion_user = create_user(can_book_free_offers=False, is_admin=True)
    offerer1 = create_offerer(name='offerer1', validation_token="a_token")
    offerer2 = create_offerer(name='offerer2', siren='789456123', validation_token="some_token")
    offerer3 = create_offerer(name='offerer3', siren='789456124')
    offerer4 = create_offerer(name='offerer4', siren='789456125')
    user1 = create_user(email='1@offerer.com')
    user2 = create_user(email='2@offerer.com')
    user3 = create_user(email='3@offerer.com')
    user4 = create_user(email='4@offerer.com')
    user5 = create_user(email='5@offerer.com')
    user_offerer1 = create_user_offerer(user1, offerer1, validation_token="nice_token")
    user_offerer2 = create_user_offerer(user2, offerer2)
    user_offerer3 = create_user_offerer(user3, offerer3, validation_token="another_token")
    user_offerer4 = create_user_offerer(user4, offerer4)
    user_offerer5 = create_user_offerer(user5, offerer3, validation_token="what_a_token")
    venue1 = create_venue(offerer1, siret=None, comment="nice_comment", validation_token="venue_token")
    venue2 = create_venue(offerer2, siret="12345678212345")
    venue3 = create_venue(offerer3, siret="12345678312345")
    venue4 = create_venue(offerer4, siret="12345678412345")

    repository.save(connexion_user, user_offerer1, user_offerer2, user_offerer3, user_offerer4, venue1, venue2, venue3,
                  venue4)

    auth_request = TestClient(app.test_client()).with_auth(email=connexion_user.email)
    # when
    response = auth_request.get('/exports/pending_validation')

    # then
    assert response.status_code == 200
    response_json = response.json
    assert len(response_json) == 3
    assert response_json[0]['validationToken'] == offerer1.validationToken
    assert response_json[0]['UserOfferers'][0]['validationToken'] == user_offerer1.validationToken
    assert response_json[0]['managedVenues'][0]['validationToken'] == venue1.validationToken
    assert response_json[0]['managedVenues'][0]['comment'] == venue1.comment
    assert response_json[1]['validationToken'] == offerer2.validationToken
    assert response_json[1]['UserOfferers'][0]['validationToken'] is None
    assert response_json[2]['validationToken'] is None
    user_offerers_validation_token = [user_offerer_dict['validationToken'] for user_offerer_dict in
                                      response_json[2]['UserOfferers']]
    assert user_offerer3.validationToken in user_offerers_validation_token
    assert user_offerer5.validationToken in user_offerers_validation_token


@pytest.mark.usefixtures("db_session")
def test_get_venues_returns_403_when_user_is_not_admin(app):
    # given
    data = {}
    user = create_user(is_admin=False)
    repository.save(user)
    auth_request = TestClient(app.test_client()).with_auth(email=user.email)

    # when
    response = auth_request.post('/exports/venues', json=data)

    # then
    assert response.status_code == 403


@pytest.mark.usefixtures("db_session")
def test_get_venues_returns_403_when_user_is_structure_admin_but_not_admin(app):
    # given
    data = {}
    user = create_user(can_book_free_offers=False, is_admin=False)
    offerer = create_offerer()
    user_offerer = create_user_offerer(user, offerer, is_admin=True)
    venue = create_venue(offerer)
    repository.save(user_offerer, venue)
    auth_request = TestClient(app.test_client()).with_auth(email=user.email)

    # when
    response = auth_request.post('/exports/venues', json=data)

    # then
    assert response.status_code == 403


@pytest.mark.usefixtures("db_session")
def test_get_venues_return_200_and_filtered_venues(app):
    # given
    data = {
        "has_validated_offerer": True,
        "dpts": ["93", "67"],
        "has_siret": True,
        "is_virtual": False,
        "is_validated": True,
        "from_date": "2018-10-02",
        "to_date": "2018-12-31",
        "offer_status": "ALL"
    }

    user = create_user(can_book_free_offers=False, is_admin=True)
    validated_offerer = create_offerer()
    not_validated_offerer = create_offerer(validation_token="here is a token", siren="123456798")

    venue93_with_offer_before_date_range = create_venue(validated_offerer,
                                                        name='venue93_with_offer_before_date_range',
                                                        postal_code='93100', siret="12345678912310")
    venue93_with_offer_after_date_range = create_venue(validated_offerer,
                                                       name='venue93_with_offer_after_date_range', postal_code='93100',
                                                       siret="12345678912311")
    venue93_with_offer_in_date_range = create_venue(validated_offerer,
                                                    name='venue93_with_offer_in_date_range', postal_code='93100',
                                                    siret="12345678912312")
    venue67_with_offer_before_date_range = create_venue(validated_offerer,
                                                        name='venue67_with_offer_before_date_range',
                                                        postal_code='67100', siret="12345678912313")
    venue67_with_offer_in_date_range = create_venue(validated_offerer, name='venue67_with_offer_in_date_range',
                                                    postal_code='67100', siret="12345678912314")
    venue67_without_offer_in_date_range = create_venue(validated_offerer,
                                                       name='venue67_without_offer_in_date_range', postal_code='67100',
                                                       siret="12345678912315")
    venue34_with_offer_in_date_range = create_venue(validated_offerer,
                                                    name='venue34_with_offer_in_date_range', postal_code='34100',
                                                    siret="12345678912316")
    venue_without_siret_with_offer_in_date_range = create_venue(validated_offerer,
                                                                name='venue_without_siret_with_offer_in_date_range',
                                                                comment="here is a comment", siret=None)
    venue_virtual_with_offer_in_date_range = create_venue(validated_offerer,
                                                          name='venue_virtual_with_offer_in_date_range', siret=None,
                                                          is_virtual=True)
    venue_not_validated_with_offer_in_date_range = create_venue(validated_offerer,
                                                                name='venue_not_validated_with_offer_in_date_range',
                                                                validation_token="here is a validation_token",
                                                                siret="12345678912317")
    venue_with_not_validated_offerer_in_date_range = create_venue(not_validated_offerer,
                                                                  name='venue_with_not_validated_offerer_in_date_range',
                                                                  siret="12345678912318")

    offer1 = create_offer_with_event_product(venue93_with_offer_before_date_range)
    offer2 = create_offer_with_event_product(venue93_with_offer_after_date_range)
    offer3 = create_offer_with_event_product(venue93_with_offer_in_date_range)
    offer4 = create_offer_with_event_product(venue67_with_offer_before_date_range)
    offer5 = create_offer_with_event_product(venue67_with_offer_in_date_range)
    offer6 = create_offer_with_event_product(venue34_with_offer_in_date_range)
    offer7 = create_offer_with_event_product(venue_without_siret_with_offer_in_date_range)
    offer8 = create_offer_with_event_product(venue_virtual_with_offer_in_date_range)
    offer9 = create_offer_with_event_product(venue_not_validated_with_offer_in_date_range)

    stocks = [
        create_stock_from_event_occurrence(create_event_occurrence(offer1)),
        create_stock_from_event_occurrence(create_event_occurrence(offer2)),
        create_stock_from_event_occurrence(create_event_occurrence(offer3)),
        create_stock_from_event_occurrence(create_event_occurrence(offer4)),
        create_stock_from_event_occurrence(create_event_occurrence(offer5)),
        create_stock_from_event_occurrence(create_event_occurrence(offer6)),
        create_stock_from_event_occurrence(create_event_occurrence(offer7)),
        create_stock_from_event_occurrence(create_event_occurrence(offer8)),
        create_stock_from_event_occurrence(create_event_occurrence(offer9))
    ]
    repository.save(
        user, venue_with_not_validated_offerer_in_date_range,
        venue67_without_offer_in_date_range, *stocks
    )

    venue67_with_offer_in_date_range_id = venue67_with_offer_in_date_range.id
    venue93_with_offer_in_date_range_id = venue93_with_offer_in_date_range.id

    activity_in_date_range1 = create_venue_activity(venue93_with_offer_in_date_range, 'insert',
                                                    issued_at=datetime(2018, 11, 30))
    activity_in_date_range2 = create_venue_activity(venue67_with_offer_in_date_range, 'insert',
                                                    issued_at=datetime(2018, 11, 30))
    activity_in_date_range3 = create_venue_activity(venue67_without_offer_in_date_range, 'insert',
                                                    issued_at=datetime(2018, 11, 30))
    activity_in_date_range4 = create_venue_activity(venue34_with_offer_in_date_range, 'insert',
                                                    issued_at=datetime(2018, 11, 30))
    activity_in_date_range5 = create_venue_activity(venue_virtual_with_offer_in_date_range, 'insert',
                                                    issued_at=datetime(2018, 11, 30))
    activity_in_date_range6 = create_venue_activity(venue_not_validated_with_offer_in_date_range, 'insert',
                                                    issued_at=datetime(2018, 11, 30))
    activity_in_date_range7 = create_venue_activity(venue_with_not_validated_offerer_in_date_range, 'insert',
                                                    issued_at=datetime(2018, 11, 30))
    activity_before_date_range1 = create_venue_activity(venue93_with_offer_before_date_range, 'insert',
                                                        issued_at=datetime(2018, 6, 30))
    activity_before_date_range2 = create_venue_activity(venue67_with_offer_before_date_range, 'insert',
                                                        issued_at=datetime(2018, 6, 30))
    activity_after_date_range = create_venue_activity(venue93_with_offer_after_date_range, 'insert',
                                                      issued_at=datetime(2019, 8, 30))

    save_all_activities(activity_in_date_range1, activity_in_date_range2, activity_in_date_range3,
                        activity_in_date_range4, activity_in_date_range5, activity_in_date_range6,
                        activity_in_date_range7, activity_before_date_range1, activity_before_date_range2,
                        activity_after_date_range)

    auth_request = TestClient(app.test_client()).with_auth(email=user.email)

    # when
    response = auth_request.post('/exports/venues', json=data)

    # then
    venue_names = list(map(lambda x: x['name'], response.json))

    assert response.status_code == 200
    assert len(venue_names) == 2
    assert VenueSQLEntity.query.get(venue67_with_offer_in_date_range_id).name in venue_names
    assert VenueSQLEntity.query.get(venue93_with_offer_in_date_range_id).name in venue_names


@pytest.mark.usefixtures("db_session")
def test_get_venues_with_params_for_pc_reporting_return_200_and_filtered_venues(app):
    # given
    data = {
        "has_validated_offerer": True,
        "has_offerer_with_siren": True,
        "has_validated_user_offerer": True,
        "has_validated_user": True
    }
    query_user = create_user(can_book_free_offers=False, is_admin=True)

    validated_user = create_user(can_book_free_offers=False, email="another@mail.com")
    validated_user_2 = create_user(can_book_free_offers=False, email="another2@mail.com")
    not_validated_user = create_user(can_book_free_offers=False, email="a@mail.com", validation_token="a_token")

    validated_offerer_with_siren1 = create_offerer(siren='123456789')
    validated_offerer_with_siren2 = create_offerer(siren='123456782')
    validated_offerer_with_siren3 = create_offerer(siren='123456783')
    validated_offerer_without_siren = create_offerer(siren=None)
    not_validated_offerer_with_siren = create_offerer(siren='123456781', validation_token="token")

    validated_user_offerer_with_validated_user_with_validated_offerer_with_siren = create_user_offerer(validated_user,
                                                                                                       validated_offerer_with_siren1)
    validated_user_offerer_with_not_validated_user_with_validated_offerer_with_siren = create_user_offerer(
        not_validated_user,
        validated_offerer_with_siren3)
    validated_user_offerer_with_validated_user_with_not_validated_offerer_with_siren = create_user_offerer(
        validated_user,
        not_validated_offerer_with_siren)
    validated_user_offerer_with_validated_user_with_validated_offerer_without_siren = create_user_offerer(
        validated_user_2,
        validated_offerer_without_siren)
    not_validated_user_offerer_with_validated_user_with_validated_offerer_with_siren = create_user_offerer(
        validated_user,
        validated_offerer_with_siren2, validation_token="another_token")

    venue_with_validated_offerer_with_siren_with_user_offerer_with_user = create_venue(validated_offerer_with_siren1,
                                                                                       name="venue_with_validated_offerer_with_siren_with_user_offerer_with_user",
                                                                                       siret="12345678912341")
    venue_without_validated_offerer_with_siren_with_user_offerer_with_user = create_venue(
        not_validated_offerer_with_siren,
        name="venue_without_validated_offerer_with_siren_with_user_offerer_with_user", siret="12345678912342")
    venue_with_validated_offerer_without_siren_with_user_offerer_with_user = create_venue(
        validated_offerer_without_siren,
        name="venue_with_validated_offerer_without_siren_with_user_offerer_with_user", siret="12345678912343")
    venue_with_validated_offerer_with_siren_without_user_offerer_with_user = create_venue(validated_offerer_with_siren2,
                                                                                          name="venue_with_validated_offerer_with_siren_without_user_offerer_with_user",
                                                                                          siret="12345678912344")
    venue_with_validated_offerer_with_siren_with_user_offerer_without_user = create_venue(validated_offerer_with_siren3,
                                                                                          name="venue_with_validated_offerer_with_siren_with_user_offerer_without_user",
                                                                                          siret="12345678912345")

    repository.save(query_user,
                  venue_with_validated_offerer_with_siren_with_user_offerer_with_user,
                  venue_without_validated_offerer_with_siren_with_user_offerer_with_user,
                  venue_with_validated_offerer_without_siren_with_user_offerer_with_user,
                  venue_with_validated_offerer_with_siren_without_user_offerer_with_user,
                  venue_with_validated_offerer_with_siren_with_user_offerer_without_user,
                  validated_user_offerer_with_validated_user_with_validated_offerer_with_siren,
                  validated_user_offerer_with_not_validated_user_with_validated_offerer_with_siren,
                  validated_user_offerer_with_validated_user_with_not_validated_offerer_with_siren,
                  validated_user_offerer_with_validated_user_with_validated_offerer_without_siren,
                  not_validated_user_offerer_with_validated_user_with_validated_offerer_with_siren)
    expected_venue_id = venue_with_validated_offerer_with_siren_with_user_offerer_with_user.id
    auth_request = TestClient(app.test_client()).with_auth(email=query_user.email)

    # when
    response = auth_request.post('/exports/venues', json=data)

    # then
    venue_names = list(map(lambda x: x['name'], response.json))

    assert response.status_code == 200
    assert len(venue_names) == 1
    assert VenueSQLEntity.query.get(expected_venue_id).name in venue_names


@pytest.mark.usefixtures("db_session")
def test_get_venues_with_sirens_params_return_200_and_filtered_venues(app):
    # given
    data = {
        "sirens": ["123456781", "123456782", "123456783"]
    }

    query_user = create_user(can_book_free_offers=False, is_admin=True)

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

    repository.save(query_user, venue_123456789, venue_123456781, venue_123456782, venue_123456783,
                  venue_123456784)
    venue_123456781_id = venue_123456781.id
    venue_123456782_id = venue_123456782.id
    venue_123456783_id = venue_123456783.id
    auth_request = TestClient(app.test_client()).with_auth(email=query_user.email)

    # when
    response = auth_request.post('/exports/venues', json=data)

    # then
    venue_names = list(map(lambda x: x['name'], response.json))

    assert response.status_code == 200
    assert len(venue_names) == 3
    assert VenueSQLEntity.query.get(venue_123456781_id).name in venue_names
    assert VenueSQLEntity.query.get(venue_123456782_id).name in venue_names
    assert VenueSQLEntity.query.get(venue_123456783_id).name in venue_names


@pytest.mark.usefixtures("db_session")
def test_get_venues_return_error_when_date_param_is_wrong(app):
    # given
    wrong_date = "I\'m not a valid date"
    data = {'from_date': wrong_date}
    user = create_user(can_book_free_offers=False, is_admin=True)

    repository.save(user)
    auth_request = TestClient(app.test_client()).with_auth(email=user.email)

    # when
    response = auth_request.post('/exports/venues', json=data)

    # then
    assert response.status_code == 400
    assert response.json['date_format'] == ['to_date and from_date are of type yyyy-mm-dd']


@pytest.mark.usefixtures("db_session")
def test_get_offerers_returns_403_when_user_is_not_admin(app):
    # given
    data = {}
    user = create_user(is_admin=False)
    repository.save(user)
    auth_request = TestClient(app.test_client()).with_auth(email=user.email)

    # when
    response = auth_request.post('/exports/offerers', json=data)

    # then
    assert response.status_code == 403


@pytest.mark.usefixtures("db_session")
def test_get_offerers_returns_403_when_user_is_structure_admin_but_not_admin(app):
    # given
    data = {}
    user = create_user(can_book_free_offers=False, is_admin=False)
    offerer = create_offerer()
    user_offerer = create_user_offerer(user, offerer, is_admin=True)
    repository.save(user_offerer)
    auth_request = TestClient(app.test_client()).with_auth(email=user.email)

    # when
    response = auth_request.post('/exports/offerers', json=data)

    # then
    assert response.status_code == 403


@pytest.mark.usefixtures("db_session")
def test_get_offerers_return_200_and_filtered_offerers(app):
    # given
    data = {
        "zip_codes": ["93100", "2A450"],
        "from_date": "2018-10-02",
        "to_date": "2018-12-31",
        "has_not_virtual_venue": True,
        "has_validated_venue": True,
        "has_venue_with_siret": True,
        "offer_status": "ALL"
    }

    query_user = create_user(can_book_free_offers=False, is_admin=True)

    offerer_93100_in_date_range_with_validated_venue_with_siret_with_offer = create_offerer(
        name="offerer_93100_in_date_range_with_validated_venue_with_siret_with_offer",
        postal_code="93100", siren="123456781", date_created=datetime(2018, 11, 2))
    offerer_93100_in_date_range_with_validated_venue_with_siret_and_venue_without_siret_with_offer = create_offerer(
        name="offerer_93100_in_date_range_with_validated_venue_with_siret_and_venue_without_siret_with_offer",
        postal_code="93100", siren="123456782", date_created=datetime(2018, 11, 2))
    not_validated_offerer_93100_in_date_range_with_validated_venue_with_siret_with_offer = create_offerer(
        name="not_validated_offerer_93100_in_date_range_with_validated_venue_with_siret_with_offer",
        postal_code="93100", siren="123456770", validation_token="token", date_created=datetime(2018, 11, 2))
    offerer_93100_in_date_range_with_validated_venue_with_siret_with_offer_without_siren = create_offerer(
        name="offerer_93100_in_date_range_with_validated_venue_with_siret_with_offer_without_siren",
        postal_code="93100", siren=None, date_created=datetime(2018, 11, 2))
    offerer_2A450_in_date_range_with_validated_venue_with_siret_with_active_offer_thing = create_offerer(
        name="offerer_2A450_in_date_range_with_validated_venue_with_siret_with_active_offer_thing",
        postal_code="2A450", siren="123456783", date_created=datetime(2018, 11, 2))
    offerer_2A450_in_date_range_with_validated_venue_with_siret_with_expired_offer_thing = create_offerer(
        name="offerer_2A450_in_date_range_with_validated_venue_with_siret_with_expired_offer_thing",
        postal_code="2A450", siren="123456784", date_created=datetime(2018, 11, 2))
    offerer_66666_in_date_range_with_validated_venue_with_siret_with_offer = create_offerer(
        name="offerer_66666_in_date_range_with_validated_venue_with_siret_with_offer",
        postal_code="66666", siren="123456785", date_created=datetime(2018, 11, 2))
    offerer_2A450_in_date_range_with_validated_venue_without_siret_with_offer = create_offerer(
        name="offerer_2A450_in_date_range_with_validated_venue_without_siret_with_offer",
        postal_code="2A450", siren="123456788", date_created=datetime(2018, 11, 2))
    offerer_2A450_in_date_range_with_validated_venue_with_siret_without_offer = create_offerer(
        name="offerer_2A450_in_date_range_with_validated_venue_with_siret_without_offer",
        postal_code="2A450", siren="123456780", date_created=datetime(2018, 11, 2))
    offerer_93100_in_date_range_with_virtual_venue_with_offer = create_offerer(
        name="offerer_93100_in_date_range_with_virtual_venue_with_offer",
        postal_code="93100", siren="123456771", date_created=datetime(2018, 11, 2))
    offerer_2A450_in_date_range_without_validated_venue_with_siret_with_offer = create_offerer(
        name="offerer_2A450_in_date_range_without_validated_venue_with_siret_with_offer",
        postal_code="2A450", siren="123456789", date_created=datetime(2018, 11, 2))
    offerer_93100_before_date_range_with_validated_venue_with_siret_with_offer = create_offerer(
        name="offerer_93100_before_date_range_with_validated_venue_with_siret_with_offer",
        postal_code="93100", siren="123456786", date_created=datetime(2018, 1, 2))
    offerer_93100_after_date_range_with_validated_venue_with_siret_with_offer = create_offerer(
        name="offerer_93100_after_date_range_with_validated_venue_with_siret_with_offer",
        postal_code="93100", siren="123456787", date_created=datetime(2019, 12, 2))

    validated_venue_with_siret_with_offer_1 = create_venue(
        offerer_93100_in_date_range_with_validated_venue_with_siret_with_offer, siret="12345678912341")
    validated_venue_with_siret_and_venue_without_siret_with_offer = create_venue(
        offerer_93100_in_date_range_with_validated_venue_with_siret_and_venue_without_siret_with_offer,
        siret="12345678912342")
    validated_venue_with_siret_with_offer_2 = create_venue(
        not_validated_offerer_93100_in_date_range_with_validated_venue_with_siret_with_offer, siret="12345678912343")
    validated_venue_with_siret_with_offer_without_siren = create_venue(
        offerer_93100_in_date_range_with_validated_venue_with_siret_with_offer_without_siren, siret="12345678912344")
    validated_venue_with_siret_with_active_offer_thing = create_venue(
        offerer_2A450_in_date_range_with_validated_venue_with_siret_with_active_offer_thing, siret="12345678912345")
    validated_venue_with_siret_with_expired_offer_thing = create_venue(
        offerer_2A450_in_date_range_with_validated_venue_with_siret_with_expired_offer_thing, siret="12345678912346")
    validated_venue_with_siret_with_offer_3 = create_venue(
        offerer_66666_in_date_range_with_validated_venue_with_siret_with_offer, siret="12345678912347")
    validated_venue_with_siret_with_offer_4 = create_venue(
        offerer_93100_before_date_range_with_validated_venue_with_siret_with_offer, siret="12345678912348")
    validated_venue_with_siret_with_offer_5 = create_venue(
        offerer_93100_after_date_range_with_validated_venue_with_siret_with_offer, siret="12345678912349")
    validated_venue_without_siret_with_offer = create_venue(
        offerer_2A450_in_date_range_with_validated_venue_without_siret_with_offer, siret=None,
        comment="i've no siret because that life")
    not_validated_venue_with_siret_with_offer = create_venue(
        offerer_2A450_in_date_range_without_validated_venue_with_siret_with_offer, siret="12345678912331",
        validation_token="token")
    validated_venue_with_siret_without_offer = create_venue(
        offerer_2A450_in_date_range_with_validated_venue_with_siret_without_offer, siret="12345678912332")
    virtual_venue_with_offer = create_venue(
        offerer_93100_in_date_range_with_virtual_venue_with_offer, siret=None, is_virtual=True)

    stock_offer_1 = create_stock_with_event_offer(
        offerer_93100_in_date_range_with_validated_venue_with_siret_with_offer, validated_venue_with_siret_with_offer_1)
    stock_offer_2 = create_stock_with_event_offer(
        offerer_93100_in_date_range_with_validated_venue_with_siret_and_venue_without_siret_with_offer,
        validated_venue_with_siret_and_venue_without_siret_with_offer)
    stock_offer_3 = create_stock_with_event_offer(
        not_validated_offerer_93100_in_date_range_with_validated_venue_with_siret_with_offer,
        validated_venue_with_siret_with_offer_2)
    stock_offer_4 = create_stock_with_event_offer(
        offerer_93100_in_date_range_with_validated_venue_with_siret_with_offer_without_siren,
        validated_venue_with_siret_with_offer_without_siren)
    stock_offer_5 = create_stock_with_event_offer(
        offerer_66666_in_date_range_with_validated_venue_with_siret_with_offer, validated_venue_with_siret_with_offer_3)
    stock_offer_6 = create_stock_with_event_offer(
        offerer_93100_before_date_range_with_validated_venue_with_siret_with_offer,
        validated_venue_with_siret_with_offer_4)
    stock_offer_7 = create_stock_with_event_offer(
        offerer_93100_after_date_range_with_validated_venue_with_siret_with_offer,
        validated_venue_with_siret_with_offer_5)
    stock_offer_8 = create_stock_with_event_offer(
        offerer_2A450_in_date_range_with_validated_venue_without_siret_with_offer,
        validated_venue_without_siret_with_offer)
    stock_offer_9 = create_stock_with_event_offer(
        offerer_2A450_in_date_range_without_validated_venue_with_siret_with_offer,
        not_validated_venue_with_siret_with_offer)
    stock_offer_10 = create_stock_with_event_offer(offerer_93100_in_date_range_with_virtual_venue_with_offer,
                                                   virtual_venue_with_offer)
    stock_active_offer_thing = create_stock_with_thing_offer(
        offerer_2A450_in_date_range_with_validated_venue_with_siret_with_active_offer_thing,
        validated_venue_with_siret_with_active_offer_thing)
    stock_expired_offer_thing = create_stock_with_thing_offer(
        offerer_2A450_in_date_range_with_validated_venue_with_siret_with_expired_offer_thing,
        validated_venue_with_siret_with_expired_offer_thing, quantity=0)

    repository.save(query_user, stock_offer_1, stock_offer_2, stock_offer_3, stock_offer_4, stock_offer_5,
                  stock_offer_6, stock_offer_7,
                  stock_offer_8, stock_offer_9, stock_offer_10, stock_active_offer_thing,
                  stock_expired_offer_thing, validated_venue_with_siret_without_offer)

    auth_request = TestClient(app.test_client()).with_auth(email=query_user.email)

    # when
    response = auth_request.post('/exports/offerers', json=data)

    # then
    offerer_names = list(map(lambda x: x['name'], response.json))

    assert response.status_code == 200
    assert len(offerer_names) == 6


@pytest.mark.usefixtures("db_session")
def test_get_offerers_with_params_for_pc_reporting_return_200_and_filtered_offerers(app):
    # given
    data = {
        "has_siren": True,
        "is_validated": True,
        "has_validated_user_offerer": True,
        "has_validated_user": True,
        "has_bank_information": False,
        "is_active": True
    }
    user_querying = create_user(can_book_free_offers=False, is_admin=True)

    offerer_no_siren = create_offerer(siren=None, is_active=True, validation_token=None)
    offerer_not_validated = create_offerer(siren='123456789', is_active=True, validation_token='blabla')
    offerer_not_validated_user_offerer = create_offerer(siren='123456780', is_active=True, validation_token=None)
    offerer_not_validated_user = create_offerer(siren='123456781', is_active=True, validation_token=None)
    offerer_bank_information = create_offerer(siren='123456782', is_active=True, validation_token=None)
    offerer_not_active = create_offerer(siren='123456783', is_active=False, validation_token=None)
    offerer_ok = create_offerer(siren='123456784', is_active=True, validation_token=None)

    user_validated = create_user(email='email1@test.com', validation_token=None)
    user_validated_2 = create_user(email='email3@test.com', validation_token=None)
    user_not_validated = create_user(email='email2@test.com', validation_token='blabla')

    user_offerer_no_siren = create_user_offerer(user_validated, offerer_no_siren, validation_token=None)
    user_offerer_not_validated_offerer = create_user_offerer(user_validated_2, offerer_not_validated,
                                                             validation_token=None)
    user_offerer_not_validated = create_user_offerer(user_validated, offerer_not_validated_user_offerer,
                                                     validation_token='blabla')
    user_offerer_not_validated_user = create_user_offerer(user_not_validated, offerer_not_validated_user,
                                                          validation_token=None)
    user_offerer_bank_information = create_user_offerer(user_validated, offerer_bank_information, validation_token=None)
    user_offerer_not_active = create_user_offerer(user_validated, offerer_not_active)
    user_offerer_ok = create_user_offerer(user_validated, offerer_ok, validation_token=None)

    repository.save(user_querying, user_offerer_no_siren, user_offerer_not_validated_offerer,
                  user_offerer_not_validated, user_offerer_not_validated_user, user_offerer_bank_information,
                  user_offerer_not_active, user_offerer_ok)

    bank_information = create_bank_information(bic="AGRIFRPP", iban='DE89370400440532013000',
                                               offerer=offerer_bank_information)

    repository.save(bank_information)

    auth_request = TestClient(app.test_client()).with_auth(email=user_querying.email)

    # when
    response = auth_request.post('/exports/offerers', json=data)

    # then
    assert response.status_code == 200
    response_json = response.json
    assert len(response_json) == 1
    assert response_json[0]['siren'] == '123456784'


@pytest.mark.usefixtures("db_session")
def test_get_offerers_with_sirens_params_return_200_and_filtered_offerers(app):
    # given
    data = {
        "sirens": ["123456781", "123456782", "123456783"]
    }

    query_user = create_user(can_book_free_offers=False, is_admin=True)

    offerer_123456789 = create_offerer(name="offerer_123456789", siren="123456789")
    offerer_123456781 = create_offerer(name="offerer_123456781", siren="123456781")
    offerer_123456782 = create_offerer(name="offerer_123456782", siren="123456782")
    offerer_123456783 = create_offerer(name="offerer_123456783", siren="123456783")
    offerer_123456784 = create_offerer(name="offerer_123456784", siren="123456784")

    repository.save(query_user, offerer_123456789, offerer_123456781, offerer_123456782, offerer_123456783,
                  offerer_123456784)
    offerer_123456781_id = offerer_123456781.id
    offerer_123456782_id = offerer_123456782.id
    offerer_123456783_id = offerer_123456783.id
    auth_request = TestClient(app.test_client()).with_auth(email=query_user.email)

    # when
    response = auth_request.post('/exports/offerers', json=data)

    # then
    offerer_names = list(map(lambda x: x['name'], response.json))

    assert response.status_code == 200
    assert len(offerer_names) == 3
    assert Offerer.query.get(offerer_123456781_id).name in offerer_names
    assert Offerer.query.get(offerer_123456782_id).name in offerer_names
    assert Offerer.query.get(offerer_123456783_id).name in offerer_names


@pytest.mark.usefixtures("db_session")
def test_get_offerers_return_error_when_date_param_is_wrong(app):
    # given
    wrong_date = "I\'m not a valid date"
    data = {'from_date': wrong_date}
    user = create_user(can_book_free_offers=False, is_admin=True)

    repository.save(user)
    auth_request = TestClient(app.test_client()).with_auth(email=user.email)

    # when
    response = auth_request.post('/exports/offerers', json=data)

    # then
    assert response.status_code == 400
    assert response.json['date_format'] == ['to_date and from_date are of type yyyy-mm-dd']
