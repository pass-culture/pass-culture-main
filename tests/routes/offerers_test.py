""" routes offerer """
import pytest
import secrets
from datetime import timedelta, datetime
from pprint import pprint

from domain.reimbursement import ReimbursementRules
from models import PcObject, ThingType, EventType
from models.db import db
from models.pc_object import serialize
from tests.conftest import clean_database
from tests.test_utils import API_URL, \
    create_booking, \
    create_deposit, \
    create_event_offer, \
    create_offerer, \
    create_recommendation, \
    create_stock_from_offer, \
    create_stock_with_event_offer, \
    create_stock_with_thing_offer, \
    create_thing_offer, \
    create_user, \
    create_user_offerer, \
    create_venue, \
    req, \
    req_with_auth, create_thing, create_event, create_stock_from_event_occurrence, create_event_occurrence, \
    create_bank_information
from utils.human_ids import dehumanize, humanize


def _get_offer_type(response_json):
    try:
        return response_json['stock']['resolvedOffer']['thing']['offerType']
    except KeyError:
        return response_json['stock']['resolvedOffer']['event']['offerType']


@pytest.mark.standalone
def test_get_offerers_should_work_only_when_logged_in():
    # when
    response = req.get(API_URL + '/offerers', headers={'origin': 'http://localhost:3000'})

    # then
    assert response.status_code == 401


@pytest.mark.standalone
@clean_database
def test_get_offerers_should_return_a_list_of_offerers_sorted_alphabetically(app):
    # given
    offerer1 = create_offerer(siren='123456781', name='offreur C')
    offerer2 = create_offerer(siren='123456782', name='offreur A')
    offerer3 = create_offerer(siren='123456783', name='offreur B')
    PcObject.check_and_save(offerer1, offerer3, offerer2)

    user = create_user(password='p@55sw0rd')
    user.offerers = [offerer1, offerer2, offerer3]
    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    # when
    response = auth_request.get(API_URL + '/offerers')

    # then
    assert response.status_code == 200
    offerers = response.json()
    assert len(offerers) == 3
    names = [offerer['name'] for offerer in offerers]
    assert names == ['offreur A', 'offreur B', 'offreur C']


@pytest.mark.standalone
@clean_database
def test_get_offerers_should_return_only_user_offerers_if_current_user_is_not_admin(app):
    # given
    offerer1 = create_offerer(siren='123456781', name='offreur C')
    offerer2 = create_offerer(siren='123456782', name='offreur A')
    offerer3 = create_offerer(siren='123456783', name='offreur B')
    PcObject.check_and_save(offerer1, offerer3, offerer2)

    user = create_user(can_book_free_offers=True, password='p@55sw0rd', is_admin=False)
    user.offerers = [offerer1, offerer2]
    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    # when
    response = auth_request.get(API_URL + '/offerers')

    # then
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.standalone
@clean_database
def test_get_offerers_should_return_all_offerers_if_current_user_is_admin(app):
    # given
    offerer1 = create_offerer(siren='123456781', name='offreur C')
    offerer2 = create_offerer(siren='123456782', name='offreur A')
    offerer3 = create_offerer(siren='123456783', name='offreur B')
    PcObject.check_and_save(offerer1, offerer3, offerer2)

    user = create_user(can_book_free_offers=False, password='p@55sw0rd', is_admin=True)
    user.offerers = [offerer1, offerer2]
    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    # when
    response = auth_request.get(API_URL + '/offerers')

    # then
    assert response.status_code == 200
    assert len(response.json()) == 3


@pytest.mark.standalone
@clean_database
def test_get_offerers_should_return_bad_request_if_param_validated_is_not_true_or_false(app):
    # given
    offerer1 = create_offerer(siren='123456781', name='offreur C')
    offerer2 = create_offerer(siren='123456782', name='offreur A')
    offerer3 = create_offerer(siren='123456783', name='offreur B')
    PcObject.check_and_save(offerer1, offerer3, offerer2)

    user = create_user(can_book_free_offers=False, password='p@55sw0rd', is_admin=True)
    user.offerers = [offerer1, offerer2]
    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    # when
    response = auth_request.get(API_URL + '/offerers?validated=blabla')

    # then
    assert response.status_code == 400
    assert response.json()['validated'] == ["Le paramètre 'validated' doit être 'true' ou 'false'"]


@pytest.mark.standalone
@clean_database
def test_get_offerers_should_return_all_info_of_all_offerers_if_current_user_is_admin_and_param_validated_is_false(app):
    # given
    offerer1 = create_offerer(siren='123456781', name='offreur C')
    offerer2 = create_offerer(siren='123456782', name='offreur A')
    offerer3 = create_offerer(siren='123456783', name='offreur B')
    PcObject.check_and_save(offerer1, offerer3, offerer2)
    bank_information1 = create_bank_information(offerer_id=offerer1.id, id_at_providers='123456781')
    bank_information2 = create_bank_information(offerer_id=offerer2.id, id_at_providers='123456782')
    bank_information3 = create_bank_information(offerer_id=offerer3.id, id_at_providers='123456783')

    user = create_user(can_book_free_offers=False, password='p@55sw0rd', is_admin=True)
    user.offerers = [offerer1, offerer2]
    PcObject.check_and_save(user, bank_information1, bank_information2, bank_information3)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    # when
    response = auth_request.get(API_URL + '/offerers?validated=false')

    # then
    assert response.status_code == 200
    assert set(response.json()[0].keys()) == {
        'address', 'bic', 'city', 'dateCreated', 'dateModifiedAtLastProvider',
        'firstThumbDominantColor', 'iban', 'id', 'idAtProviders', 'isActive',
        'isValidated', 'lastProviderId', 'managedVenues', 'modelName', 'nOffers',
        'name', 'postalCode', 'siren', 'thumbCount'
    }


@pytest.mark.standalone
@clean_database
def test_get_offerers_should_return_only_not_validated_offerers_if_param_validated_is_false(app):
    # given
    user = create_user(password='p@55sw0rd')
    offerer1 = create_offerer(siren='123456781', name='offreur C')
    offerer2 = create_offerer(siren='123456782', name='offreur A')
    offerer3 = create_offerer(siren='123456783', name='offreur B')
    user_offerer1 = create_user_offerer(user, offerer1, validation_token=None)
    user_offerer2 = create_user_offerer(user, offerer2, validation_token='AZE123')
    user_offerer3 = create_user_offerer(user, offerer3, validation_token=None)
    PcObject.check_and_save(user_offerer1, user_offerer2, user_offerer3)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    # when
    response = auth_request.get(API_URL + '/offerers?validated=false')

    # then
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.standalone
@clean_database
def test_get_offerers_should_return_only_name_and_siren_of_not_validated_offerers_if_param_validated_is_false(app):
    # given
    user = create_user(password='p@55sw0rd')
    offerer1 = create_offerer(siren='123456781', name='offreur C')
    offerer2 = create_offerer(siren='123456782', name='offreur A')
    offerer3 = create_offerer(siren='123456783', name='offreur B')
    user_offerer1 = create_user_offerer(user, offerer1, validation_token=None)
    user_offerer2 = create_user_offerer(user, offerer2, validation_token='AZE123')
    user_offerer3 = create_user_offerer(user, offerer3, validation_token=None)
    PcObject.check_and_save(user_offerer1, user_offerer2, user_offerer3)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    # when
    response = auth_request.get(API_URL + '/offerers?validated=false')

    # then
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0] == {'modelName': 'Offerer', 'name': 'offreur A', 'siren': '123456782'}


@pytest.mark.standalone
@clean_database
def test_get_offerers_should_return_only_validated_offerers_if_param_validated_is_true(app):
    # given
    user = create_user(password='p@55sw0rd')
    offerer1 = create_offerer(siren='123456781', name='offreur C')
    offerer2 = create_offerer(siren='123456782', name='offreur A')
    offerer3 = create_offerer(siren='123456783', name='offreur B')
    user_offerer1 = create_user_offerer(user, offerer1, validation_token=None)
    user_offerer2 = create_user_offerer(user, offerer2, validation_token='AZE123')
    user_offerer3 = create_user_offerer(user, offerer3, validation_token=None)
    PcObject.check_and_save(user_offerer1, user_offerer2, user_offerer3)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    # when
    response = auth_request.get(API_URL + '/offerers?validated=true')

    # then
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]['name'] == 'offreur B'
    assert response.json()[1]['name'] == 'offreur C'


@pytest.mark.standalone
@clean_database
def test_get_offerers_should_return_all_info_of_validated_offerers_if_param_validated_is_true(app):
    # given
    user = create_user(password='p@55sw0rd')
    offerer1 = create_offerer(siren='123456781', name='offreur C')
    offerer2 = create_offerer(siren='123456782', name='offreur A')
    offerer3 = create_offerer(siren='123456783', name='offreur B')
    user_offerer1 = create_user_offerer(user, offerer1, validation_token=None)
    user_offerer2 = create_user_offerer(user, offerer2, validation_token='AZE123')
    user_offerer3 = create_user_offerer(user, offerer3, validation_token=None)
    PcObject.check_and_save(user_offerer1, user_offerer2, user_offerer3)
    bank_information1 = create_bank_information(offerer_id=offerer1.id, id_at_providers='123456781')
    bank_information2 = create_bank_information(offerer_id=offerer2.id, id_at_providers='123456782')
    bank_information3 = create_bank_information(offerer_id=offerer3.id, id_at_providers='123456783')
    PcObject.check_and_save(bank_information1, bank_information2, bank_information3)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    # when
    response = auth_request.get(API_URL + '/offerers?validated=true')

    # then
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert list(response.json()[0].keys()) == [
        'address', 'bic', 'city', 'dateCreated', 'dateModifiedAtLastProvider',
        'firstThumbDominantColor', 'iban', 'id', 'idAtProviders', 'isActive',
        'isValidated', 'lastProviderId', 'managedVenues', 'modelName', 'nOffers',
        'name', 'postalCode', 'siren', 'thumbCount'
    ]


@pytest.mark.standalone
@clean_database
def test_post_offerers_creates_an_offerer_and_one_virtual_venue(app):
    # given
    user = create_user(password='p@55sw0rd')
    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')
    body = {
        'name': 'Test Offerer',
        'siren': '418166096',
        'address': '123 rue de Paris',
        'postalCode': '93100',
        'city': 'Montreuil'
    }

    # when
    response = auth_request.post(API_URL + '/offerers', json=body)

    # then
    assert response.status_code == 201
    assert response.json()['siren'] == '418166096'
    assert response.json()['name'] == 'Test Offerer'
    virtual_venues = list(filter(lambda v: v['isVirtual'],
                                 response.json()['managedVenues']))
    assert len(virtual_venues) == 1


@pytest.mark.standalone
@clean_database
def test_post_offerers_without_address_creates_an_offerer(app):
    # given
    user = create_user(password='p@55sw0rd')
    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')
    body = {
        'name': 'Test Offerer',
        'siren': '418166096',
        'postalCode': '93100',
        'city': 'Montreuil'
    }

    # when
    response = auth_request.post(API_URL + '/offerers', json=body)

    # then
    assert response.status_code == 201
    assert response.json()['siren'] == '418166096'
    assert response.json()['name'] == 'Test Offerer'


@pytest.mark.standalone
@clean_database
def test_get_offerer_bookings_returns_bookings_with_their_reimbursements_ordered_newest_to_oldest(app):
    # given
    now = datetime.utcnow()
    user_pro = create_user(can_book_free_offers=False, password='p@55sw0rd')
    user = create_user(email='test@email.com')
    deposit = create_deposit(user, now, amount=24000)
    PcObject.check_and_save(deposit)
    offerer = create_offerer()
    user_offerer = create_user_offerer(user_pro, offerer)
    PcObject.check_and_save(user_offerer)

    venue = create_venue(offerer)
    stock1 = create_stock_with_event_offer(offerer, venue, price=20)
    stock2 = create_stock_with_thing_offer(offerer, venue, thing_offer=None, price=40)
    stock3 = create_stock_with_thing_offer(offerer, venue, thing_offer=None, price=22950)
    booking1 = create_booking(user, stock1, venue, recommendation=None, quantity=2)
    booking2 = create_booking(user, stock2, venue, recommendation=None, quantity=2)
    booking3 = create_booking(user, stock3, venue, recommendation=None, quantity=1)
    PcObject.check_and_save(booking1, booking2, booking3)
    auth_request = req_with_auth(email=user_pro.email, password='p@55sw0rd')

    # when
    response = auth_request.get(
        API_URL + '/offerers/%s/bookings?order_by_column=booking_id&order=desc' % humanize(offerer.id))

    # then
    assert response.status_code == 200
    elements = response.json()
    assert dehumanize(elements[0]['id']) == booking3.id
    assert dehumanize(elements[1]['id']) == booking2.id
    assert dehumanize(elements[2]['id']) == booking1.id


@pytest.mark.standalone
@clean_database
def test_get_offerer_bookings_returns_bookings_with_only_public_user_info_and_none_token(app):
    # given
    now = datetime.utcnow()
    user_pro = create_user(can_book_free_offers=False, password='p@55sw0rd')
    user = create_user(first_name='Jean', last_name='Aimarx', email='jean.aimarx@disrupflux.fr')
    deposit = create_deposit(user, now, amount=24000)
    offerer = create_offerer()
    user_offerer = create_user_offerer(user_pro, offerer)
    venue = create_venue(offerer)
    stock = create_stock_with_event_offer(offerer, venue, price=20)
    booking = create_booking(user, stock, venue, recommendation=None, quantity=2)

    PcObject.check_and_save(deposit, user_offerer, booking)

    auth_request = req_with_auth(email=user_pro.email, password='p@55sw0rd')

    # when
    response = auth_request.get(API_URL + '/offerers/%s/bookings' % humanize(offerer.id))

    # then
    response_first_booking_json = response.json()[0]
    assert response.status_code == 200
    assert response_first_booking_json['token'] == None
    assert response_first_booking_json['user'] == {
        'firstName': user.firstName,
        'email': user.email,
        'lastName': user.lastName
    }


@pytest.mark.standalone
@clean_database
def test_get_offerer_bookings_returns_bookings_with_public_user_info_and_token_when_it_is_used(app):
    # given
    now = datetime.utcnow()
    user_pro = create_user(can_book_free_offers=False, password='p@55sw0rd')
    user = create_user(first_name='Jean', last_name='Aimarx', email='jean.aimarx@disrupflux.fr')
    deposit = create_deposit(user, now, amount=24000)
    offerer = create_offerer()
    user_offerer = create_user_offerer(user_pro, offerer)
    venue = create_venue(offerer)
    stock = create_stock_with_event_offer(offerer, venue, price=20)
    booking = create_booking(user, stock, venue, recommendation=None, quantity=2, is_used=True)

    PcObject.check_and_save(deposit, user_offerer, booking)

    auth_request = req_with_auth(email=user_pro.email, password='p@55sw0rd')

    # when
    response = auth_request.get(API_URL + '/offerers/%s/bookings' % humanize(offerer.id))

    # then
    response_first_booking_json = response.json()[0]
    assert response.status_code == 200
    assert response_first_booking_json['token'] == booking.token
    assert response_first_booking_json['user'] == {
        'firstName': user.firstName,
        'email': user.email,
        'lastName': user.lastName
    }


@pytest.mark.standalone
@clean_database
def test_get_offerer_bookings_returns_bookings_with_their_reimbursements_infos(app):
    # given
    now = datetime.utcnow()
    user_pro = create_user(can_book_free_offers=False, password='p@55sw0rd')
    user = create_user(email='test@email.com')
    deposit = create_deposit(user, now, amount=500)
    PcObject.check_and_save(deposit)
    offerer = create_offerer()
    user_offerer = create_user_offerer(user_pro, offerer)
    PcObject.check_and_save(user_offerer)

    venue = create_venue(offerer)
    stock = create_stock_with_event_offer(offerer, venue, price=20)
    booking = create_booking(user, stock, venue, recommendation=None, quantity=2, date_created=now - timedelta(days=5))

    PcObject.check_and_save(booking)
    auth_request = req_with_auth(email=user_pro.email, password='p@55sw0rd')

    # when
    response = auth_request.get(API_URL + '/offerers/%s/bookings' % humanize(offerer.id))

    # then
    assert response.json()[0]['id'] == humanize(booking.id)
    assert response.json()[0]['reimbursement_rule'] == ReimbursementRules.PHYSICAL_OFFERS.value.description
    assert response.json()[0]['reimbursed_amount'] == booking.value


@pytest.mark.standalone
@clean_database
def test_get_offerer_bookings_returns_bookings_with_thing_or_event_offer_type(app):
    # given
    now = datetime.utcnow()
    user_pro = create_user(can_book_free_offers=False, password='p@55sw0rd')
    user = create_user(email='test@email.com')
    offerer = create_offerer()
    user_offerer = create_user_offerer(user_pro, offerer)
    venue = create_venue(offerer)
    thing = create_thing(thing_type=ThingType.AUDIOVISUEL)
    offer_thing = create_thing_offer(venue, thing)
    stock_thing = create_stock_from_offer(offer_thing, price=0)
    booking_thing = create_booking(user, stock_thing, venue, recommendation=None, quantity=2,
                                   date_created=now - timedelta(days=5))
    event = create_event(event_type=EventType.MUSEES_PATRIMOINE)
    offer_event = create_event_offer(venue, event)
    stock_event = create_stock_from_event_occurrence(create_event_occurrence(offer_event), price=0)
    booking_event = create_booking(user, stock_event, venue, recommendation=None, quantity=2,
                                   date_created=now - timedelta(days=5))

    PcObject.check_and_save(booking_thing, booking_event, user_offerer)

    expected_audiovisuel_offer_type = {
        'description': 'Action, science-fiction, documentaire ou comédie sentimentale ? ' \
                       'En salle, en plein air ou bien au chaud chez soi ? ' \
                       'Et si c’était plutôt cette exposition qui allait faire son cinéma ?',
        'label': 'Audiovisuel (Films sur supports physiques et VOD)',
        'offlineOnly': False,
        'onlineOnly': False,
        'sublabel': 'Regarder',
        'type': 'Thing',
        'value': 'ThingType.AUDIOVISUEL'
    }

    expected_musees_patrimoine_offer_type = {
        'description': 'Action, science-fiction, documentaire ou comédie sentimentale ? '
                       'En salle, en plein air ou bien au chaud chez soi ? '
                       'Et si c’était plutôt cette exposition qui allait faire son cinéma ?',
        'label': 'Musées — Patrimoine (Expositions, Visites guidées, Activités spécifiques)',
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': 'Regarder',
        'type': 'Event',
        'value': 'EventType.MUSEES_PATRIMOINE'
    }

    auth_request = req_with_auth(email=user_pro.email, password='p@55sw0rd')

    # when
    response = auth_request.get(API_URL + '/offerers/%s/bookings' % humanize(offerer.id))

    # then
    offer_types = list(map(_get_offer_type, response.json()))
    assert expected_audiovisuel_offer_type in offer_types
    assert expected_musees_patrimoine_offer_type in offer_types


@pytest.mark.standalone
@clean_database
def test_get_offerer_bookings_returns_bad_request_if_user_has_no_rights_on_offerer(app):
    # given
    now = datetime.utcnow()
    user = create_user(email='test@email.com', password='p@55sw0rd!')
    deposit = create_deposit(user, now, amount='500')
    PcObject.check_and_save(deposit)
    offerer = create_offerer()
    PcObject.check_and_save(offerer)

    venue = create_venue(offerer)
    stock1 = create_stock_with_event_offer(offerer, venue, price=20)
    stock2 = create_stock_with_thing_offer(offerer, venue, thing_offer=None, price=30)
    stock3 = create_stock_with_thing_offer(offerer, venue, thing_offer=None, price=40)
    booking1 = create_booking(user, stock1, venue, recommendation=None, quantity=2)
    booking2 = create_booking(user, stock2, venue, recommendation=None, quantity=1)
    booking3 = create_booking(user, stock3, venue, recommendation=None, quantity=2)

    PcObject.check_and_save(booking1, booking2, booking3)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd!')

    # when
    response = auth_request.get(API_URL + '/offerers/%s/bookings' % humanize(offerer.id))

    # then
    assert response.status_code == 403


@clean_database
@pytest.mark.standalone
def test_get_offerer_bookings_should_work_only_when_logged_in(app):
    # when
    offerer = create_offerer()
    PcObject.check_and_save(offerer)
    response = req.get(API_URL + '/offerers/%s/bookings' % humanize(offerer.id),
                       headers={'origin': 'http://localhost:3000'})

    # then
    assert response.status_code == 401


@clean_database
@pytest.mark.standalone
def test_get_offerers_should_not_send_offerer_to_user_offerer_not_validated(app):
    # Given
    offerer = create_offerer()
    user = create_user(password='p@55sw0rd!')
    user_offerer = create_user_offerer(user, offerer, validation_token=secrets.token_urlsafe(20))
    PcObject.check_and_save(user_offerer)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd!')

    # When
    response = auth_request.get(API_URL + '/offerers/')

    # then
    assert response.json() == []


@clean_database
@pytest.mark.standalone
def test_get_offerers_should_not_send_offerer_to_user_offerer_not_validated(app):
    # Given
    user = create_user(password='p@55sw0rd!')
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd!')
    PcObject.check_and_save(user)
    invalid_id = 12

    # When
    response = auth_request.get(API_URL + '/offerers/%s' % invalid_id)

    # then
    assert response.status_code == 404
    assert response.json()['global'] == ['La page que vous recherchez n\'existe pas']


@clean_database
@pytest.mark.standalone
def test_post_offerers_when_admin(app):
    # Given
    user = create_user(can_book_free_offers=False, password='p@55sw0rd!', is_admin=True)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd!')
    PcObject.check_and_save(user)

    # When
    body = {
        'name': 'Test Offerer',
        'siren': '418166096',
        'address': '123 rue de Paris',
        'postalCode': '93100',
        'city': 'Montreuil'
    }
    response = auth_request.post(API_URL + '/offerers', json=body)

    # then
    assert response.status_code == 201


@clean_database
@pytest.mark.standalone
def test_patch_offerer_when_not_admin_status_code_403(app):
    # given
    user = create_user()
    offerer = create_offerer()
    user_offerer = create_user_offerer(user, offerer, is_admin=False)
    PcObject.check_and_save(user_offerer)
    auth_request = req_with_auth(email=user.email, password=user.clearTextPassword)
    body = {'isActive': False}

    # when
    response = auth_request.patch(API_URL + '/offerers/%s' % humanize(offerer.id), json=body)

    # then
    assert response.status_code == 403


@clean_database
@pytest.mark.standalone
def test_patch_offerer_for_non_authorised_fields_status_code_400(app):
    # given
    user = create_user()
    offerer = create_offerer()
    user_offerer = create_user_offerer(user, offerer, is_admin=True)
    PcObject.check_and_save(user_offerer)
    auth_request = req_with_auth(email=user.email, password=user.clearTextPassword)
    body = {'thumbCount': 0, 'idAtProviders': 'zfeej',
            'dateModifiedAtLastProvider': serialize(datetime(2016, 2, 1)), 'address': '123 nouvelle adresse',
            'postalCode': '75001',
            'city': 'Paris', 'validationToken': 'ozieghieof', 'id': humanize(10),
            'dateCreated': serialize(datetime(2015, 2, 1)),
            'name': 'Nouveau Nom', 'siren': '989807829', 'lastProviderId': humanize(1)}

    # when
    response = auth_request.patch(API_URL + '/offerers/%s' % humanize(offerer.id), json=body)

    # then
    assert response.status_code == 400
    for key in body:
        assert response.json()[key] == ['Vous ne pouvez pas modifier ce champ']


@pytest.mark.standalone
@clean_database
def test_get_offerer_bookings_ordered_by_venue_name_desc(app):
    # given
    now = datetime.utcnow()
    user_pro = create_user(can_book_free_offers=False, password='p@55sw0rd')
    user = create_user(email='test@email.com')
    deposit = create_deposit(user, now, amount=500)
    offerer = create_offerer()
    user_offerer = create_user_offerer(user_pro, offerer)

    venue_1 = create_venue(offerer, name='La petite librairie', siret=offerer.siren + '12345')
    venue_2 = create_venue(offerer, name='Atelier expérimental', siret=offerer.siren + '54321')
    offer_1 = create_thing_offer(venue_1)
    offer_2 = create_event_offer(venue_2)
    stock1 = create_stock_from_offer(offer_1)
    stock2 = create_stock_from_offer(offer_2)
    stock3 = create_stock_from_offer(offer_2)
    booking1 = create_booking(user, stock2, venue_2, recommendation=None, quantity=2)
    booking2 = create_booking(user, stock1, venue_1, recommendation=None, quantity=2)
    booking3 = create_booking(user, stock3, venue_2, recommendation=None, quantity=1)
    PcObject.check_and_save(deposit, user_offerer, booking1, booking2, booking3)
    auth_request = req_with_auth(email=user_pro.email, password='p@55sw0rd')

    # when
    response = auth_request.get(
        API_URL + '/offerers/%s/bookings?order_by_column=venue_name&order=desc' % humanize(offerer.id))

    # then
    assert response.status_code == 200
    elements = response.json()
    assert elements[0]['stock']['resolvedOffer']['venueId'] == humanize(venue_1.id)
    assert elements[1]['stock']['resolvedOffer']['venueId'] == humanize(venue_2.id)
    assert elements[2]['stock']['resolvedOffer']['venueId'] == humanize(venue_2.id)


@pytest.mark.standalone
@clean_database
def test_get_offerer_bookings_ordered_by_venue_name_asc(app):
    # given
    now = datetime.utcnow()
    user_pro = create_user(can_book_free_offers=False, password='p@55sw0rd')
    user = create_user(email='test@email.com')
    deposit = create_deposit(user, now, amount=500)
    offerer = create_offerer()
    user_offerer = create_user_offerer(user_pro, offerer)

    venue_1 = create_venue(offerer, name='La petite librairie', siret=offerer.siren + '12345')
    venue_2 = create_venue(offerer, name='Atelier expérimental', siret=offerer.siren + '54321')
    offer_1 = create_thing_offer(venue_1)
    offer_2 = create_event_offer(venue_2)
    stock1 = create_stock_from_offer(offer_1)
    stock2 = create_stock_from_offer(offer_2)
    stock3 = create_stock_from_offer(offer_2)
    booking1 = create_booking(user, stock2, venue_2, recommendation=None, quantity=2)
    booking2 = create_booking(user, stock1, venue_1, recommendation=None, quantity=2)
    booking3 = create_booking(user, stock3, venue_2, recommendation=None, quantity=1)
    PcObject.check_and_save(deposit, user_offerer, booking1, booking2, booking3)
    auth_request = req_with_auth(email=user_pro.email, password='p@55sw0rd')

    # when
    response = auth_request.get(
        API_URL + '/offerers/%s/bookings?order_by_column=venue_name&order=asc' % humanize(offerer.id))

    # then
    assert response.status_code == 200
    elements = response.json()
    assert elements[0]['stock']['resolvedOffer']['venueId'] == humanize(venue_2.id)
    assert elements[1]['stock']['resolvedOffer']['venueId'] == humanize(venue_2.id)
    assert elements[2]['stock']['resolvedOffer']['venueId'] == humanize(venue_1.id)


@pytest.mark.standalone
@clean_database
def test_get_offerer_bookings_ordered_by_date_asc(app):
    # given
    now = datetime.utcnow()
    user_pro = create_user(can_book_free_offers=False, password='p@55sw0rd')
    user = create_user(email='test@email.com')
    deposit = create_deposit(user, now, amount=500)
    offerer = create_offerer()
    user_offerer = create_user_offerer(user_pro, offerer)

    venue = create_venue(offerer, name='La petite librairie')
    offer = create_thing_offer(venue)
    stock1 = create_stock_from_offer(offer)
    stock2 = create_stock_from_offer(offer)
    stock3 = create_stock_from_offer(offer)
    booking1 = create_booking(user, stock2, venue, recommendation=None, date_created=serialize(datetime(2018, 10, 1)))
    booking2 = create_booking(user, stock1, venue, recommendation=None, date_created=serialize(datetime(2018, 10, 5)))
    booking3 = create_booking(user, stock3, venue, recommendation=None, date_created=serialize(datetime(2018, 10, 3)))
    PcObject.check_and_save(deposit, user_offerer, booking1, booking2, booking3)
    auth_request = req_with_auth(email=user_pro.email, password='p@55sw0rd')

    # when
    response = auth_request.get(API_URL + '/offerers/%s/bookings?order_by_column=date&order=asc' % humanize(offerer.id))

    # then
    assert response.status_code == 200
    elements = response.json()
    assert elements[0]['dateCreated'].startswith('2018-10-01')
    assert elements[1]['dateCreated'].startswith('2018-10-03')
    assert elements[2]['dateCreated'].startswith('2018-10-05')


@pytest.mark.standalone
@clean_database
def test_get_offerer_bookings_ordered_by_date_desc(app):
    # given
    now = datetime.utcnow()
    user_pro = create_user(can_book_free_offers=False, password='p@55sw0rd')
    user = create_user(email='test@email.com')
    deposit = create_deposit(user, now, amount=500)
    offerer = create_offerer()
    user_offerer = create_user_offerer(user_pro, offerer)

    venue = create_venue(offerer, name='La petite librairie')
    offer = create_thing_offer(venue)
    stock1 = create_stock_from_offer(offer)
    stock2 = create_stock_from_offer(offer)
    stock3 = create_stock_from_offer(offer)
    booking1 = create_booking(user, stock2, venue, recommendation=None, date_created=serialize(datetime(2018, 10, 1)))
    booking2 = create_booking(user, stock1, venue, recommendation=None, date_created=serialize(datetime(2018, 10, 5)))
    booking3 = create_booking(user, stock3, venue, recommendation=None, date_created=serialize(datetime(2018, 10, 3)))
    PcObject.check_and_save(deposit, user_offerer, booking1, booking2, booking3)
    auth_request = req_with_auth(email=user_pro.email, password='p@55sw0rd')

    # when
    response = auth_request.get(
        API_URL + '/offerers/%s/bookings?order_by_column=date&order=desc' % humanize(offerer.id))

    # then
    assert response.status_code == 200
    elements = response.json()
    assert elements[0]['dateCreated'].startswith('2018-10-05')
    assert elements[1]['dateCreated'].startswith('2018-10-03')
    assert elements[2]['dateCreated'].startswith('2018-10-01')


@pytest.mark.standalone
@clean_database
def test_get_offerer_bookings_ordered_by_category_asc(app):
    # given
    now = datetime.utcnow()
    user_pro = create_user(can_book_free_offers=False, password='p@55sw0rd')
    user = create_user(email='test@email.com')
    deposit = create_deposit(user, now, amount=500)
    offerer = create_offerer()
    user_offerer = create_user_offerer(user_pro, offerer)

    venue_1 = create_venue(offerer, name='La petite librairie', siret=offerer.siren + '12345')
    venue_2 = create_venue(offerer, name='Atelier expérimental', siret=offerer.siren + '54321')
    offer_1 = create_thing_offer(venue_1, thing_type=ThingType.LIVRE_EDITION)
    offer_2 = create_event_offer(venue_2, event_type=EventType.SPECTACLE_VIVANT)
    stock1 = create_stock_from_offer(offer_1)
    stock2 = create_stock_from_offer(offer_2)
    stock3 = create_stock_from_offer(offer_2)
    booking1 = create_booking(user, stock2, venue_2, recommendation=None)
    booking2 = create_booking(user, stock1, venue_1, recommendation=None)
    booking3 = create_booking(user, stock3, venue_2, recommendation=None)
    PcObject.check_and_save(deposit, user_offerer, booking1, booking2, booking3)
    auth_request = req_with_auth(email=user_pro.email, password='p@55sw0rd')

    # when
    response = auth_request.get(
        API_URL + '/offerers/%s/bookings?order_by_column=category&order=asc' % humanize(offerer.id))

    # then
    assert response.status_code == 200
    elements = response.json()
    assert elements[0]['stock']['resolvedOffer']['event']['type'] == 'EventType.SPECTACLE_VIVANT'
    assert elements[1]['stock']['resolvedOffer']['event']['type'] == 'EventType.SPECTACLE_VIVANT'
    assert elements[2]['stock']['resolvedOffer']['thing']['type'] == 'ThingType.LIVRE_EDITION'


@pytest.mark.standalone
@clean_database
def test_get_offerer_bookings_ordered_by_category_desc(app):
    # given
    now = datetime.utcnow()
    user_pro = create_user(can_book_free_offers=False, password='p@55sw0rd')
    user = create_user(email='test@email.com')
    deposit = create_deposit(user, now, amount=500)
    offerer = create_offerer()
    user_offerer = create_user_offerer(user_pro, offerer)

    venue_1 = create_venue(offerer, name='La petite librairie', siret=offerer.siren + '12345')
    venue_2 = create_venue(offerer, name='Atelier expérimental', siret=offerer.siren + '54321')
    offer_1 = create_thing_offer(venue_1, thing_type=ThingType.LIVRE_EDITION)
    offer_2 = create_event_offer(venue_2, event_type=EventType.SPECTACLE_VIVANT)
    stock1 = create_stock_from_offer(offer_1)
    stock2 = create_stock_from_offer(offer_2)
    stock3 = create_stock_from_offer(offer_2)
    booking1 = create_booking(user, stock2, venue_2, recommendation=None)
    booking2 = create_booking(user, stock1, venue_1, recommendation=None)
    booking3 = create_booking(user, stock3, venue_2, recommendation=None)
    PcObject.check_and_save(deposit, user_offerer, booking1, booking2, booking3)
    auth_request = req_with_auth(email=user_pro.email, password='p@55sw0rd')

    # when
    response = auth_request.get(
        API_URL + '/offerers/%s/bookings?order_by_column=category&order=desc' % humanize(offerer.id))

    # then
    assert response.status_code == 200
    elements = response.json()
    assert elements[0]['stock']['resolvedOffer']['thing']['type'] == 'ThingType.LIVRE_EDITION'
    assert elements[1]['stock']['resolvedOffer']['event']['type'] == 'EventType.SPECTACLE_VIVANT'
    assert elements[2]['stock']['resolvedOffer']['event']['type'] == 'EventType.SPECTACLE_VIVANT'


@pytest.mark.standalone
@clean_database
def test_get_offerer_bookings_ordered_by_amount_desc(app):
    # given
    now = datetime.utcnow()
    user_pro = create_user(can_book_free_offers=False, password='p@55sw0rd')
    user = create_user(email='test@email.com')
    deposit = create_deposit(user, now, amount=500)
    offerer = create_offerer()
    user_offerer = create_user_offerer(user_pro, offerer)

    venue_1 = create_venue(offerer, name='La petite librairie', is_virtual=True, siret=None)
    venue_2 = create_venue(offerer, name='Atelier expérimental')
    offer_1 = create_thing_offer(venue_1, thing_type=ThingType.JEUX_VIDEO, url='http://game.fr/jeu')
    offer_2 = create_event_offer(venue_2, event_type=EventType.SPECTACLE_VIVANT)
    stock1 = create_stock_from_offer(offer_1, price=10)
    stock2 = create_stock_from_offer(offer_2, price=20)
    stock3 = create_stock_from_offer(offer_2, price=0)
    booking1 = create_booking(user, stock2, venue_2, recommendation=None)
    booking2 = create_booking(user, stock1, venue_1, recommendation=None)
    booking3 = create_booking(user, stock3, venue_2, recommendation=None)
    PcObject.check_and_save(deposit, user_offerer, booking1, booking2, booking3)
    auth_request = req_with_auth(email=user_pro.email, password='p@55sw0rd')

    # when
    response = auth_request.get(
        API_URL + '/offerers/%s/bookings?order_by_column=amount&order=desc' % humanize(offerer.id))

    # then
    assert response.status_code == 200
    elements = response.json()
    assert elements[0]['amount'] == 20
    assert elements[1]['amount'] == 10
    assert elements[2]['amount'] == 0


@pytest.mark.standalone
@clean_database
def test_get_offerer_bookings_ordered_by_amount_asc(app):
    # given
    now = datetime.utcnow()
    user_pro = create_user(can_book_free_offers=False, password='p@55sw0rd')
    user = create_user(email='test@email.com')
    deposit = create_deposit(user, now, amount=500)
    offerer = create_offerer()
    user_offerer = create_user_offerer(user_pro, offerer)

    venue_1 = create_venue(offerer, name='La petite librairie', is_virtual=True, siret=None)
    venue_2 = create_venue(offerer, name='Atelier expérimental')
    offer_1 = create_thing_offer(venue_1, thing_type=ThingType.JEUX_VIDEO, url='http://game.fr/jeu')
    offer_2 = create_event_offer(venue_2, event_type=EventType.SPECTACLE_VIVANT)
    stock1 = create_stock_from_offer(offer_1, price=10)
    stock2 = create_stock_from_offer(offer_2, price=20)
    stock3 = create_stock_from_offer(offer_2, price=0)
    booking1 = create_booking(user, stock2, venue_2, recommendation=None)
    booking2 = create_booking(user, stock1, venue_1, recommendation=None)
    booking3 = create_booking(user, stock3, venue_2, recommendation=None)
    PcObject.check_and_save(deposit, user_offerer, booking1, booking2, booking3)
    auth_request = req_with_auth(email=user_pro.email, password='p@55sw0rd')

    # when
    response = auth_request.get(
        API_URL + '/offerers/%s/bookings?order_by_column=amount&order=asc' % humanize(offerer.id))

    # then
    assert response.status_code == 200
    elements = response.json()
    pprint(elements)
    assert elements[0]['amount'] == 0
    assert elements[1]['amount'] == 10
    assert elements[2]['amount'] == 20


@pytest.mark.standalone
@clean_database
def test_deactivating_offerer_returns_200_and_expires_recos(app):
    # given
    user = create_user(password='p@55sw0rd')
    other_user = create_user(email='other@email.fr')
    offerer = create_offerer(siren='987654321')
    other_offerer = create_offerer()
    venue1 = create_venue(offerer, siret=offerer.siren + '12345')
    venue2 = create_venue(offerer, siret=offerer.siren + '12346')
    other_venue = create_venue(other_offerer)
    offer_venue1_1 = create_event_offer(venue1)
    offer_venue2_1 = create_event_offer(venue2)
    offer_venue2_2 = create_thing_offer(venue2)
    other_offer = create_event_offer(other_venue)
    user_offerer = create_user_offerer(user, offerer, is_admin=True)
    original_validity_date = datetime.utcnow() + timedelta(days=7)
    recommendation1 = create_recommendation(offer_venue1_1, other_user, valid_until_date=original_validity_date)
    recommendation2 = create_recommendation(offer_venue2_1, other_user, valid_until_date=original_validity_date)
    recommendation3 = create_recommendation(offer_venue2_2, other_user, valid_until_date=original_validity_date)
    recommendation4 = create_recommendation(offer_venue2_2, user, valid_until_date=original_validity_date)
    other_recommendation = create_recommendation(other_offer, user, valid_until_date=original_validity_date)
    PcObject.check_and_save(recommendation1, recommendation2, recommendation3, recommendation4, other_recommendation,
                            user_offerer)

    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')
    data = {'isActive': False}

    # when
    response = auth_request.patch(API_URL + '/offerers/%s' % humanize(offerer.id), json=data)

    # then
    db.session.refresh(offerer)
    assert response.status_code == 200
    assert response.json()['isActive'] == offerer.isActive
    assert offerer.isActive == data['isActive']
    db.session.refresh(recommendation1)
    db.session.refresh(recommendation2)
    db.session.refresh(recommendation3)
    db.session.refresh(recommendation4)
    db.session.refresh(other_recommendation)
    assert recommendation1.validUntilDate < datetime.utcnow()
    assert recommendation2.validUntilDate < datetime.utcnow()
    assert recommendation3.validUntilDate < datetime.utcnow()
    assert recommendation4.validUntilDate < datetime.utcnow()
    assert other_recommendation.validUntilDate == original_validity_date
