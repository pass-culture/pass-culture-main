from datetime import datetime

import pytest

from models import PcObject
from models.db import db
from repository.booking_queries import find_bookings_stats_per_department
from repository.user_queries import find_users_by_department_and_date_range, \
    find_users_stats_per_department
from tests.conftest import clean_database
from utils.test_utils import create_user, create_booking, create_stock_with_event_offer, create_offerer, create_venue, \
    create_stock_with_thing_offer, create_activity, create_thing_offer


@pytest.mark.standalone
@clean_database
def test_find_user_by_department_and_date_range(app):
    #given
    date_max = '2018-06-06'
    date_min = '2018-05-05'
    department = '34'
    user1 = create_user(email='a@a.f', departement_code='34', date_created=datetime(2018, 5, 10))
    user2 = create_user(email='a@b.f', departement_code='93', date_created=datetime(2018, 5, 10))
    user3 = create_user(email='a@c.f', departement_code='34', date_created=datetime(2018, 4, 10))
    user4 = create_user(email='a@d.f', departement_code='34', date_created=datetime(2018, 9, 10))
    PcObject.check_and_save(user1, user2, user3, user4)

    #when
    users = find_users_by_department_and_date_range(date_max, date_min, department)

    #then
    assert (user1.id, user1.dateCreated, user1.departementCode) in users
    assert (user2.id, user2.dateCreated, user2.departementCode) not in users
    assert (user3.id, user3.dateCreated, user3.departementCode) not in users
    assert (user4.id, user4.dateCreated, user4.departementCode) not in users


@pytest.mark.standalone
@clean_database
def test_find_users_stats_per_department(app):
    #given
    time_intervall = 'month'
    user1 = create_user(email='a@1.f', departement_code='34', date_created=datetime(2018, 4, 10))
    user2 = create_user(email='a@2.f', departement_code='93', date_created=datetime(2018, 5, 10))
    user3 = create_user(email='a@3.f', departement_code='34', date_created=datetime(2018, 4, 10))
    user4 = create_user(email='a@4.f', departement_code='34', date_created=datetime(2018, 9, 10))
    user5 = create_user(email='a@5.f', departement_code='29', date_created=datetime(2018, 3, 10))
    user6 = create_user(email='a@6.f', departement_code='93', date_created=datetime(2018, 5, 10))
    user7 = create_user(email='a@7.f', departement_code='34', date_created=datetime(2018, 5, 10))
    user8 = create_user(email='a@8.f', departement_code='97', date_created=datetime(2018, 10, 10))
    PcObject.check_and_save(user1, user2, user3, user4, user5, user6, user7, user8)

    #when
    users_stats = find_users_stats_per_department(time_intervall)

    #then
    assert ('34', datetime(2018, 4, 1), 2) in users_stats
    assert ('34', datetime(2018, 9, 1), 1) in users_stats
    assert ('34', datetime(2018, 5, 1), 1) in users_stats
    assert ('93', datetime(2018, 5, 1), 2) in users_stats
    assert ('97', datetime(2018, 10, 1), 1) in users_stats
    assert ('29', datetime(2018, 3, 1), 1) in users_stats


@pytest.mark.standalone
@clean_database
def test_find_bookings_stats_per_department(app):
    # given
    time_intervall = 'month'
    user1 = create_user(email='a@1.f', departement_code='34', date_created=datetime(2018, 4, 10))
    user2 = create_user(email='a@2.f', departement_code='93', date_created=datetime(2018, 5, 10))
    user3 = create_user(email='a@3.f', departement_code='34', date_created=datetime(2018, 4, 10))
    user4 = create_user(email='a@4.f', departement_code='34', date_created=datetime(2018, 9, 10))

    offerer = create_offerer()
    venue34 = create_venue(offerer, departement_code='34', postal_code='34000')
    venue93 = create_venue(offerer, departement_code='93', postal_code='93100')
    thing_offer = create_thing_offer(venue93)

    stock1 = create_stock_with_event_offer(offerer, venue34, price=0)
    booking1 = create_booking(user1, stock1, venue34, recommendation=None)

    stock2 = create_stock_with_event_offer(offerer, venue93, price=0)
    booking2 = create_booking(user2, stock2, venue93, recommendation=None)

    stock3 = create_stock_with_thing_offer(offerer, venue93, thing_offer, price=0)
    booking3 = create_booking(user2, stock3, venue93, recommendation=None)

    stock4 = create_stock_with_event_offer(offerer, venue34, price=0)
    booking4 = create_booking(user1, stock4, venue34, recommendation=None)

    stock5 = create_stock_with_event_offer(offerer, venue93, price=0)
    booking5 = create_booking(user3, stock5, venue93, recommendation=None)

    stock6 = create_stock_with_thing_offer(offerer, venue93, thing_offer, price=0)
    booking6 = create_booking(user4, stock6, venue93, recommendation=None)

    PcObject.check_and_save(booking1, booking2, booking3, booking4, booking5, booking6)

    activity1 = create_activity(booking1, 'booking', 'insert', issued_at=datetime(2018, 5, 4))
    activity2 = create_activity(booking2, 'booking', 'insert', issued_at=datetime(2018, 5, 4))
    activity3 = create_activity(booking3, 'booking', 'insert', issued_at=datetime(2018, 5, 4))
    activity4 = create_activity(booking4, 'booking', 'insert', issued_at=datetime(2018, 6, 4))
    activity5 = create_activity(booking5, 'booking', 'insert', issued_at=datetime(2018, 6, 4))
    activity6 = create_activity(booking6, 'booking', 'insert', issued_at=datetime(2018, 6, 4))
    db.session.add(activity1)
    db.session.add(activity2)
    db.session.add(activity3)
    db.session.add(activity4)
    db.session.add(activity5)
    db.session.add(activity6)

    db.session.commit()

    # when
    bookings_stats = find_bookings_stats_per_department(time_intervall)

    # then
    assert ('34', datetime(2018, 5, 1), 1, 1) in bookings_stats
    assert ('93', datetime(2018, 5, 1), 2, 1) in bookings_stats
    assert ('34', datetime(2018, 6, 1), 1, 1) in bookings_stats
    assert ('93', datetime(2018, 6, 1), 2, 2) in bookings_stats


