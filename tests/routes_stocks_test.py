from datetime import timedelta

import pytest

from models.db import db
from models.pc_object import PcObject
from tests.conftest import clean_database
from utils.human_ids import humanize
from utils.test_utils import req_with_auth, API_URL, create_user, create_offerer, create_venue, \
    create_stock_with_event_offer, create_booking, create_event_offer, create_user_offerer, create_event_occurrence, \
    create_recommendation, create_stock_from_event_occurrence


@clean_database
@pytest.mark.standalone
def test_get_stocks_should_return_a_list_of_stocks(app):
    # Given
    user = create_user(email='test@email.com', can_book_free_offers=False, password='P@55w0rd', is_admin=True)
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock_1 = create_stock_with_event_offer(offerer, venue, price=10, available=10)
    stock_2 = create_stock_with_event_offer(offerer, venue, price=20, available=5)
    stock_3 = create_stock_with_event_offer(offerer, venue, price=15, available=1)
    PcObject.check_and_save(user, stock_1, stock_2, stock_3)

    # When
    request = req_with_auth('test@email.com', 'P@55w0rd').get(API_URL + '/stocks')

    # Then
    assert request.status_code == 200
    stocks = request.json()
    assert len(stocks) == 3


@clean_database
@pytest.mark.standalone
def test_getting_stocks_with_admin(app):
    # Given
    user = create_user(email='test@email.com', can_book_free_offers=False, password='P@55w0rd', is_admin=True)
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_with_event_offer(offerer, venue, price=10, available=10)
    PcObject.check_and_save(user, stock)
    humanized_stock_id = humanize(stock.id)

    # When
    request = req_with_auth('test@email.com', 'P@55w0rd').get(API_URL + '/stocks/' + humanized_stock_id)

    # Then
    assert request.status_code == 200
    assert request.json()['available'] == 10
    assert request.json()['price'] == 10


@clean_database
@pytest.mark.standalone
def test_patching_stocks_with_admin(app):
    # Given
    user = create_user(email='test@email.com', can_book_free_offers=False, password='P@55w0rd', is_admin=True)
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_with_event_offer(offerer, venue, price=10, available=10)
    PcObject.check_and_save(user, stock)
    humanized_stock_id = humanize(stock.id)

    # When
    request_update = req_with_auth('test@email.com', 'P@55w0rd').patch(API_URL + '/stocks/' + humanized_stock_id,
                                                                       json={'available': 5, 'price': 20})

    # Then
    assert request_update.status_code == 200
    request_after_update = req_with_auth('test@email.com', 'P@55w0rd').get(API_URL + '/stocks/' + humanized_stock_id)
    assert request_after_update.json()['available'] == 5
    assert request_after_update.json()['price'] == 20


# TODO: check stock modification with missing items or incorrect values


@clean_database
@pytest.mark.standalone
def test_patching_stocks_with_editor_rights(app):
    # Given
    user = create_user(email='test@email.com', password='P@55w0rd')
    offerer = create_offerer()
    user_offerer = create_user_offerer(user, offerer)
    venue = create_venue(offerer)
    stock = create_stock_with_event_offer(offerer, venue, price=10, available=10)
    PcObject.check_and_save(user, user_offerer, stock)
    humanized_stock_id = humanize(stock.id)

    # When
    request_update = req_with_auth('test@email.com', 'P@55w0rd').patch(API_URL + '/stocks/' + humanized_stock_id,
                                                                       json={'available': 5, 'price': 20})

    # Then
    assert request_update.status_code == 200
    request_after_update = req_with_auth('test@email.com', 'P@55w0rd').get(API_URL + '/stocks/' + humanized_stock_id)
    assert request_after_update.json()['available'] == 5
    assert request_after_update.json()['price'] == 20


@clean_database
@pytest.mark.standalone
def test_user_having_rights_can_create_stock(app):
    # Given
    user = create_user(email='test@email.fr', password='P@55w0rd')
    offerer = create_offerer()
    user_offerer = create_user_offerer(user, offerer)
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    PcObject.check_and_save(user_offerer, offer)

    stock_data = {'price': 1222, 'offerId': humanize(offer.id)}
    PcObject.check_and_save(user)

    # When
    r_create = req_with_auth('test@email.fr', 'P@55w0rd').post(API_URL + '/stocks/', json=stock_data)

    # Then
    assert r_create.status_code == 201
    id = r_create.json()['id']
    r_check = req_with_auth('test@email.fr', 'P@55w0rd').get(API_URL + '/stocks/' + id)
    assert r_check.status_code == 200
    created_stock_data = r_check.json()
    for (key, value) in stock_data.items():
        assert created_stock_data[key] == stock_data[key]


@clean_database
@pytest.mark.standalone
def test_user_with_no_rights_cannot_create_stock_from_offer(app):
    # Given
    user = create_user(email='test@email.fr', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    PcObject.check_and_save(user, offer)

    stock_data = {'price': 1222, 'offerId': humanize(offer.id)}
    PcObject.check_and_save(user)

    # When
    response = req_with_auth('test@email.fr', 'P@55w0rd').post(API_URL + '/stocks/', json=stock_data)

    # Then
    assert response.status_code == 403
    assert response.json()["global"] == ["Cette structure n'est pas enregistrée chez cet utilisateur."]


@clean_database
@pytest.mark.standalone
def test_user_with_no_rights_cannot_create_stock_from_event_occurrence(app):
    # Given
    user = create_user(email='test@email.fr', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    event_occurrence = create_event_occurrence(offer)
    PcObject.check_and_save(user, event_occurrence)

    stock_data = {'price': 1222, 'eventOccurrenceId': humanize(event_occurrence.id)}
    PcObject.check_and_save(user)

    # When
    response = req_with_auth('test@email.fr', 'P@55w0rd').post(API_URL + '/stocks/', json=stock_data)

    # Then
    assert response.status_code == 403
    assert response.json()["global"] == ["Cette structure n'est pas enregistrée chez cet utilisateur."]


@clean_database
@pytest.mark.standalone
def test_if_no_event_occurrence_id_or_offer(app):
    # Given
    user = create_user(email='test@email.fr', can_book_free_offers=False, password='P@55w0rd', is_admin=True)
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    event_occurrence = create_event_occurrence(offer)
    PcObject.check_and_save(user, event_occurrence)

    stock_data = {'price': 1222}
    PcObject.check_and_save(user)

    # When
    response = req_with_auth('test@email.fr', 'P@55w0rd').post(API_URL + '/stocks/', json=stock_data)

    # Then
    assert response.status_code == 400
    r_create_json = response.json()
    assert r_create_json["offerId"] == ["cette entrée est obligatoire en absence de eventOccurrenceId"]
    assert r_create_json["eventOccurrenceId"] == ["cette entrée est obligatoire en absence de offerId"]


@clean_database
@pytest.mark.standalone
def test_number_of_available_stocks_cannot_be_updated_below_number_of_already_existing_bookings(app):
    # Given
    user = create_user()
    user_admin = create_user(email='email@test.com', can_book_free_offers=False, password='P@55w0rd', is_admin=True)
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_with_event_offer(offerer, venue, price=0)
    stock.available = 1
    booking = create_booking(user, stock, venue, recommendation=None)
    PcObject.check_and_save(booking, user_admin)

    # When
    response = req_with_auth('email@test.com', 'P@55w0rd').patch(API_URL + '/stocks/' + humanize(stock.id),
                                                                 json={'available': 0})

    # Then
    assert response.status_code == 400
    assert 'available' in response.json()


@clean_database
@pytest.mark.standalone
def test_patch_stock_putting_wrong_type_on_available_returns_status_code_400_and_available_in_error(app):
    # Given
    user = create_user()
    user_admin = create_user(email='email@test.com', can_book_free_offers=False, password='P@55w0rd', is_admin=True)
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_with_event_offer(offerer, venue, price=0)
    stock.available = 1
    booking = create_booking(user, stock, venue, recommendation=None)
    PcObject.check_and_save(booking, user_admin)

    # When
    response = req_with_auth('email@test.com', 'P@55w0rd').patch(API_URL + '/stocks/' + humanize(stock.id),
                                                                 json={'available': ' '})

    # Then
    assert response.status_code == 400
    assert response.json()['available'] == ['Saisissez un nombre valide']


@clean_database
@pytest.mark.standalone
def test_should_not_create_stock_if_booking_limit_datetime_after_event_occurrence(app):
    # Given
    from models.pc_object import serialize
    user = create_user(email='email@test.com', can_book_free_offers=False, password='P@55w0rd', is_admin=True)
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    event_occurrence = create_event_occurrence(offer)
    PcObject.check_and_save(user, event_occurrence)
    data = {
        'price': 1222,
        'eventOccurrenceId': humanize(event_occurrence.id),
        'bookingLimitDatetime': serialize(event_occurrence.beginningDatetime + timedelta(days=1))
    }

    # When
    response = req_with_auth('email@test.com', 'P@55w0rd').post(API_URL + '/stocks/', json=data)

    # Then
    assert response.status_code == 400
    assert response.json()['bookingLimitDatetime'] == [
        'la date limite de réservation pour cette offre est postérieure à la date de début de l\'évènement'
    ]


@clean_database
@pytest.mark.standalone
def test_should_not_update_stock_if_booking_limit_datetime_after_event_occurrence(app):
    # Given
    from models.pc_object import serialize
    user = create_user(email='email@test.com', can_book_free_offers=False, password='P@55w0rd', is_admin=True)
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_with_event_offer(offerer, venue)
    PcObject.check_and_save(stock, user)

    stockId = stock.id

    serialized_date = serialize(stock.eventOccurrence.beginningDatetime + timedelta(days=1))
    print(serialized_date)
    # When
    response = req_with_auth('email@test.com', 'P@55w0rd').patch(API_URL + '/stocks/' + humanize(stockId),
                                                                 json={'bookingLimitDatetime': serialized_date})

    # Then
    assert response.status_code == 400
    assert response.json()['bookingLimitDatetime'] == [
        'la date limite de réservation pour cette offre est postérieure à la date de début de l\'évènement'
    ]


@clean_database
@pytest.mark.standalone
def test_user_with_no_rights_should_not_be_able_to_patch_stocks(app):
    # Given
    user = create_user(email='test@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_with_event_offer(offerer, venue)
    PcObject.check_and_save(user, stock)

    # When
    response = req_with_auth('test@email.com', 'P@55w0rd').patch(API_URL + '/stocks/' + humanize(stock.id),
                                                                 json={'available': 5})

    # Then
    assert response.status_code == 403
    assert 'Cette structure n\'est pas enregistrée chez cet utilisateur.' in response.json()['global']


@clean_database
@pytest.mark.standalone
def test_delete_should_keep_stock_in_base_with_is_soft_deleted_true(app):
    # Given
    user = create_user(email='email@test.fr', can_book_free_offers=False, password='P@55w0rd', is_admin=True)
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_with_event_offer(offerer, venue)
    PcObject.check_and_save(user, stock)

    # When
    r_delete = req_with_auth('email@test.fr', 'P@55w0rd').delete(API_URL + '/stocks/' + humanize(stock.id))

    # Then
    assert r_delete.status_code == 200
    assert r_delete.json()['isSoftDeleted'] is True
    request = req_with_auth('email@test.fr', 'P@55w0rd').get(API_URL + '/stocks/' + humanize(stock.id))
    assert request.status_code == 404
    db.session.refresh(stock)
    assert stock.isSoftDeleted is True


@clean_database
@pytest.mark.standalone
def test_user_should_not_be_able_to_delete_stock_if_does_not_have_rights(app):
    # Given
    user = create_user(email='email@test.fr', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_with_event_offer(offerer, venue)
    PcObject.check_and_save(user, stock)

    # When
    response = req_with_auth('email@test.fr', 'P@55w0rd').delete(API_URL + '/stocks/' + humanize(stock.id))

    # Then
    assert response.status_code == 403
    assert 'Cette structure n\'est pas enregistrée chez cet utilisateur.' in response.json()['global']


@clean_database
@pytest.mark.standalone
def test_when_deleted_stock_only_all_bookings_related_to_soft_deleted_stock_are_cancelled(app):
    # Given
    user1 = create_user(email='user1@test.fr')
    user2 = create_user(email='user2@test.fr')
    user_admin = create_user(email='email@test.fr', password='P@55w0rd')
    offerer = create_offerer()
    user_offerer = create_user_offerer(user_admin, offerer)
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    event_occurrence = create_event_occurrence(offer)
    stock1 = create_stock_from_event_occurrence(event_occurrence, price=0, available=10)
    stock2 = create_stock_from_event_occurrence(event_occurrence, price=0, available=10)
    recommendation1 = create_recommendation(offer, user1)
    recommendation2 = create_recommendation(offer, user2)
    booking1 = create_booking(user1, stock1, venue, recommendation=recommendation1)
    booking2 = create_booking(user1, stock2, venue, recommendation=recommendation1)
    booking3 = create_booking(user2, stock1, venue, recommendation=recommendation2)

    PcObject.check_and_save(booking1, booking2, booking3, user_offerer)

    # When
    req_with_auth('email@test.fr', 'P@55w0rd').delete(API_URL + '/stocks/' + humanize(stock1.id))

    # Then
    db.session.refresh(booking1)
    db.session.refresh(booking2)
    db.session.refresh(booking3)
    assert booking1.isCancelled == True
    assert booking2.isCancelled == False
    assert booking3.isCancelled == True
