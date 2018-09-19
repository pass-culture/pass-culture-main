""" routes offerer """
from datetime import timedelta, datetime

import pytest

from domain.reimbursement import ReimbursementRules
from models import PcObject
from tests.conftest import clean_database
from utils.human_ids import dehumanize, humanize
from utils.test_utils import API_URL, \
                             create_booking, \
                             create_deposit, \
                             create_offerer, \
                             create_stock_with_event_offer, \
                             create_stock_with_thing_offer, \
                             create_user, \
                             create_user_offerer, \
                             create_venue, \
                             req, \
                             req_with_auth

@pytest.mark.standalone
def test_get_offerers_should_work_only_when_logged_in():
    # when
    response = req.get(API_URL + '/offerers')

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
    assert len(offerers) > 0
    names = [offerer['name'] for offerer in offerers]
    assert names == ['offreur A', 'offreur B', 'offreur C']


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
    virtual_venues = list(filter(lambda v: v['isVirtual'],
                                 response.json()['managedVenues']))
    assert len(virtual_venues) == 1


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
    response = auth_request.get(API_URL + '/offerers/%s/bookings?order_by=booking.id desc' % humanize(offerer.id))

    # then
    assert response.status_code == 200
    elements = response.json()
    assert dehumanize(elements[0]['id']) == booking3.id
    assert dehumanize(elements[1]['id']) == booking2.id
    assert dehumanize(elements[2]['id']) == booking1.id


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
    booking = create_booking(user, stock, venue, recommendation=None, quantity=2, date_modified=now - timedelta(days=5))

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
    assert response.status_code == 400


@clean_database
@pytest.mark.standalone
def test_get_offerer_bookings_should_work_only_when_logged_in(app):
    # when
    offerer = create_offerer()
    PcObject.check_and_save(offerer)
    response = req.get(API_URL + '/offerers/%s/bookings' % humanize(offerer.id))

    # then
    assert response.status_code == 401
