from datetime import timedelta, datetime

import pytest

from domain.reimbursement import ReimbursementRule
from models import PcObject
from tests.conftest import clean_database
from utils.human_ids import humanize
from utils.test_utils import API_URL, req, req_with_auth, create_user, create_offerer, create_booking, create_venue, \
    create_stock_with_event_offer, create_stock_with_thing_offer, create_deposit, create_user_offerer


@pytest.mark.standalone
def test_get_offerers_should_work_only_when_logged_in():
    # when
    response = req.get(API_URL + '/offerers')

    # then
    assert response.status_code == 401


@pytest.mark.standalone
@clean_database
def test_get_offerers_should_return_a_list_of_offerers(app):
    # given
    offerer = create_offerer()
    PcObject.check_and_save(offerer)

    user = create_user(password='p@55sw0rd')
    user.offerers = [offerer]
    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    # when
    response = auth_request.get(API_URL + '/offerers')

    # then
    assert response.status_code == 200
    assert len(response.json()) > 0


@pytest.mark.standalone
@clean_database
def test_post_offerers_create_an_offerer(app):
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


@pytest.mark.standalone
@clean_database
def test_get_offerer_bookings_returns_bookings_with_their_reimbursements_ordered_newest_to_oldest(app):
    # given
    now = datetime.utcnow()
    user_pro = create_user(password='p@55sw0rd', can_book_free_offers=False)
    user = create_user(email='test@email.com')
    deposit = create_deposit(user, now, amount='500')
    deposit.save()
    offerer = create_offerer()
    user_offerer = create_user_offerer(user_pro, offerer)
    user_offerer.save()

    venue = create_venue(offerer)
    stock1 = create_stock_with_event_offer(offerer, venue, price=20)
    stock2 = create_stock_with_thing_offer(offerer, venue, thing_offer=None, price=30)
    stock3 = create_stock_with_thing_offer(offerer, venue, thing_offer=None, price=40)
    booking1 = create_booking(user, stock1, recommendation=None, quantity=2, date_modified=now - timedelta(days=5))
    booking2 = create_booking(user, stock2, recommendation=None, quantity=1, date_modified=now - timedelta(days=10))
    booking3 = create_booking(user, stock3, recommendation=None, quantity=2, date_modified=now - timedelta(days=1))

    PcObject.check_and_save(booking1, booking2, booking3)
    auth_request = req_with_auth(email=user_pro.email, password='p@55sw0rd')

    # when
    response = auth_request.get(API_URL + '/offerers/%s/bookings' % humanize(offerer.id))

    # then
    assert response.status_code == 200
    assert response.json()[0]['booking']['id'] == humanize(booking3.id)
    assert response.json()[0]['reimbursement']['name'] == ReimbursementRule.FULL_REIMBURSEMENT_OF_PHYSICAL_OFFERS.name
    assert response.json()[1]['booking']['id'] == humanize(booking1.id)
    assert response.json()[1]['reimbursement']['name'] == ReimbursementRule.FULL_REIMBURSEMENT_OF_PHYSICAL_OFFERS.name
    assert response.json()[2]['booking']['id'] == humanize(booking2.id)
    assert response.json()[2]['reimbursement']['name'] == ReimbursementRule.FULL_REIMBURSEMENT_OF_PHYSICAL_OFFERS.name


@pytest.mark.standalone
@clean_database
def test_get_offerer_bookings_returns_bad_request_if_user_has_no_rights_on_offerer(app):
    # given
    now = datetime.utcnow()
    user = create_user(email='test@email.com', password='p@55sw0rd!')
    deposit = create_deposit(user, now, amount='500')
    deposit.save()
    offerer = create_offerer()
    offerer.save()

    venue = create_venue(offerer)
    stock1 = create_stock_with_event_offer(offerer, venue, price=20)
    stock2 = create_stock_with_thing_offer(offerer, venue, thing_offer=None, price=30)
    stock3 = create_stock_with_thing_offer(offerer, venue, thing_offer=None, price=40)
    booking1 = create_booking(user, stock1, recommendation=None, quantity=2, date_modified=now - timedelta(days=5))
    booking2 = create_booking(user, stock2, recommendation=None, quantity=1, date_modified=now - timedelta(days=10))
    booking3 = create_booking(user, stock3, recommendation=None, quantity=2, date_modified=now - timedelta(days=1))

    PcObject.check_and_save(booking1, booking2, booking3)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd!')

    # when
    response = auth_request.get(API_URL + '/offerers/%s/bookings' % humanize(offerer.id))

    # then
    assert response.status_code == 400


@clean_database
@pytest.mark.standalone
def test_get_offerer_bookings_should_work_only_when_logged_in(app):
    # when
    offerer = create_offerer()
    offerer.save()
    response = req.get(API_URL + '/offerers/%s/bookings' % humanize(offerer.id))

    # then
    assert response.status_code == 401
