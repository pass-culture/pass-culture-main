from datetime import datetime

import pytest

from models import PcObject
from models.db import db
from repository.booking_queries import find_bookings_stats_per_department, \
    find_bookings_in_date_range_for_given_user_or_venue_departement
from repository.user_queries import find_users_by_department_and_date_range, \
    find_users_stats_per_department
from tests.conftest import clean_database
from utils.test_utils import create_user, create_booking, create_stock_with_event_offer, create_offerer, create_venue, \
    create_stock_with_thing_offer, create_booking_activity, create_thing_offer, create_user_activity


@pytest.mark.standalone
@clean_database
def test_find_user_by_department_and_date_range(app):
    # given
    date_max = '2018-06-06'
    date_min = '2018-05-05'
    department = '34'
    user1 = create_user(departement_code='34', email='a@a.f', date_created=datetime(2018, 5, 10))
    user2 = create_user(departement_code='93', email='a@b.f', date_created=datetime(2018, 5, 10))
    user3 = create_user(departement_code='34', email='a@c.f', date_created=datetime(2018, 4, 10))
    user4 = create_user(departement_code='34', email='a@d.f', date_created=datetime(2018, 9, 10))
    PcObject.check_and_save(user1, user2, user3, user4)

    # when
    users = find_users_by_department_and_date_range(date_max, date_min, department)

    # then
    assert (user1.id, user1.dateCreated, user1.departementCode) in users
    assert (user2.id, user2.dateCreated, user2.departementCode) not in users
    assert (user3.id, user3.dateCreated, user3.departementCode) not in users
    assert (user4.id, user4.dateCreated, user4.departementCode) not in users


@pytest.mark.standalone
@clean_database
def test_find_users_stats_per_department(app):
    # given
    time_intervall = 'month'
    user1 = create_user(departement_code='34', email='a@1.f', date_created=datetime(2018, 4, 10))
    user2 = create_user(departement_code='93', email='a@2.f', date_created=datetime(2018, 5, 10))
    user3 = create_user(departement_code='34', email='a@3.f', date_created=datetime(2018, 4, 10))
    user4 = create_user(departement_code='34', email='a@4.f', date_created=datetime(2018, 9, 10))
    user5 = create_user(departement_code='29', email='a@5.f', date_created=datetime(2018, 3, 10))
    user6 = create_user(departement_code='93', email='a@6.f', date_created=datetime(2018, 5, 10))
    user7 = create_user(departement_code='34', email='a@7.f', date_created=datetime(2018, 5, 10))
    user8 = create_user(departement_code='97', email='a@8.f', date_created=datetime(2018, 10, 10))
    PcObject.check_and_save(user1, user2, user3, user4, user5, user6, user7, user8)

    # when
    users_stats = find_users_stats_per_department(time_intervall)

    # then
    assert ('34', datetime(2018, 4, 1), 2) in users_stats
    assert ('34', datetime(2018, 9, 1), 1) in users_stats
    assert ('34', datetime(2018, 5, 1), 1) in users_stats
    assert ('93', datetime(2018, 5, 1), 2) in users_stats
    assert ('97', datetime(2018, 10, 1), 1) in users_stats
    assert ('29', datetime(2018, 3, 1), 1) in users_stats


@pytest.mark.standalone
@pytest.mark.statstests
@clean_database
def test_find_bookings_stats_per_department(app):
    # given
    time_intervall = 'month'
    user1 = create_user(departement_code='34', email='a@1.f', date_created=datetime(2018, 4, 10))
    user2 = create_user(departement_code='93', email='a@2.f', date_created=datetime(2018, 5, 10))
    user3 = create_user(departement_code='34', email='a@3.f', date_created=datetime(2018, 4, 10))
    user4 = create_user(departement_code='34', email='a@4.f', date_created=datetime(2018, 9, 10))
    user5 = create_user(departement_code='93', email='admin@test.com', can_book_free_offers=False, is_admin=True,
                        date_created=datetime(2018, 6, 10))

    offerer = create_offerer()
    venue34 = create_venue(offerer, departement_code='34', postal_code='34000', siret=offerer.siren + '12345')
    venue93 = create_venue(offerer, departement_code='93', postal_code='93100', siret=offerer.siren + '54321')
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

    cancelled_booking = create_booking(user1, stock1, venue34)
    cancelled_booking.isCancelled = True

    booking_cant_book_free_offers = create_booking(user5, stock1, venue34)

    PcObject.check_and_save(booking1, booking2, booking3, booking4, booking5, booking6, cancelled_booking,
                            booking_cant_book_free_offers)

    activity1 = create_booking_activity(booking1, 'booking', 'insert', issued_at=datetime(2018, 5, 4))
    activity2 = create_booking_activity(booking2, 'booking', 'insert', issued_at=datetime(2018, 5, 4))
    activity3 = create_booking_activity(booking3, 'booking', 'insert', issued_at=datetime(2018, 5, 4))
    activity4 = create_booking_activity(booking4, 'booking', 'insert', issued_at=datetime(2018, 6, 4))
    activity5 = create_booking_activity(booking5, 'booking', 'insert', issued_at=datetime(2018, 6, 4))
    activity6 = create_booking_activity(booking6, 'booking', 'insert', issued_at=datetime(2018, 6, 4))
    activity_not_insert = create_booking_activity(booking6, 'booking', 'update', issued_at=datetime(2018, 6, 4))
    activity_not_booking = create_user_activity(user1, 'user', 'insert', issued_at=datetime(2018, 6, 4))
    activity_cancelled_booking = create_booking_activity(cancelled_booking, 'booking', 'insert',
                                                         issued_at=datetime(2018, 5, 4))
    activity_booking_cant_book_free_offers = create_booking_activity(booking_cant_book_free_offers, 'booking', 'insert',
                                                                     datetime(2018, 5, 4))

    _save_all_activities(activity1, activity2, activity3, activity4, activity5, activity6, activity_not_insert,
                         activity_not_booking, activity_cancelled_booking, activity_booking_cant_book_free_offers)

    # when
    bookings_stats = find_bookings_stats_per_department(time_intervall)

    # then
    assert ('34', datetime(2018, 5, 1), 1, 1) in bookings_stats
    assert ('93', datetime(2018, 5, 1), 2, 1) in bookings_stats
    assert ('34', datetime(2018, 6, 1), 1, 1) in bookings_stats
    assert ('93', datetime(2018, 6, 1), 2, 2) in bookings_stats


@pytest.mark.standalone
@pytest.mark.statstests
@clean_database
def test_find_bookings_in_date_range_for_given_user_or_venue_departement(app):
    # Given
    booking_date_max = '2018-05-01'
    booking_date_min = '2018-03-01'
    event_date_max = '2018-06-01'
    event_date_min = '2018-04-01'
    user_department = '93'
    venue_department = '75'

    user_93 = create_user(email='user@email.com')

    (
        booking_activity_out_of_date,
        booking_event_OK,
        booking_event_out_of_date,
        booking_thing_OK,
        booking_thing_stock_34,
        booking_user_34,
        booking_user_cant_book_free_offers
    ) = _create_bookings_for_test()

    PcObject.check_and_save(booking_event_OK, booking_thing_stock_34, booking_event_out_of_date, booking_user_34,
                            booking_user_cant_book_free_offers, user_93)

    (
        booking_activity_delete,
        booking_activity_out_of_date_activity,
        booking_event_OK_activity,
        booking_event_out_of_date_activity,
        booking_thing_OK_activity,
        booking_thing_stock_34_activity,
        booking_user_34_activity,
        booking_user_cant_book_free_offers_activity,
        user_activity
    ) = _create_activities_for_test(booking_activity_out_of_date, booking_event_OK, booking_event_out_of_date,
                                    booking_thing_OK, booking_thing_stock_34, booking_user_34,
                                    booking_user_cant_book_free_offers, user_93)

    _save_all_activities(booking_activity_delete, booking_activity_out_of_date_activity, booking_event_OK_activity,
                         booking_event_out_of_date_activity, booking_thing_OK_activity, booking_thing_stock_34_activity,
                         booking_user_34_activity, booking_user_cant_book_free_offers_activity, user_activity)

    event_OK_offerer_id = booking_event_OK.stock.eventOccurrence.offer.venue.managingOffererId
    event_id = booking_event_OK.stock.eventOccurrence.offer.eventId
    event_beginning_datetime = booking_event_OK.stock.eventOccurrence.beginningDatetime
    event_name = booking_event_OK.stock.eventOccurrence.offer.event.name
    thing_offerer_id = booking_thing_OK.stock.offer.venue.managingOffererId
    event_offer_id = booking_event_OK.stock.eventOccurrence.offer.id
    event_occurrence_id = booking_event_OK.stock.eventOccurrenceId
    thing_id = booking_thing_OK.stock.offer.thing.id
    thing_name = booking_thing_OK.stock.offer.thing.name

    # When
    booking_information = find_bookings_in_date_range_for_given_user_or_venue_departement(booking_date_max,
                                                                                          booking_date_min,
                                                                                          event_date_max,
                                                                                          event_date_min,
                                                                                          user_department,
                                                                                          venue_department)

    # Then
    booked_during_date_range = list(
        map(lambda x: _is_in_date_range(x[4], booking_date_min, booking_date_max), booking_information))
    event_date_in_date_range = list(
        map(lambda x: _is_in_date_range(x[10], event_date_min, event_date_max), booking_information))
    in_specified_user_department = list(map(lambda x: x[2] == user_department, booking_information))
    in_specified_venue_department = list(map(lambda x: x[5] == venue_department, booking_information))
    assert all(booked_during_date_range)
    assert all(event_date_in_date_range)
    assert all(in_specified_user_department)
    assert all(in_specified_venue_department)
    assert (booking_event_OK.id, booking_event_OK.user.id, '93', booking_event_OK_activity.id, datetime(2018, 4, 12), '75',
            event_OK_offerer_id, 'Librairies et événements', event_offer_id, event_occurrence_id,
            event_beginning_datetime, event_id, event_name, None, None) in booking_information
    assert (booking_thing_OK.id, booking_event_OK.user.id, '93', booking_thing_OK_activity.id, datetime(2018, 4, 11), '75',
            thing_offerer_id, 'Librairies et événements', booking_thing_OK.stock.offer.id, None, None, None, None,
            thing_id, thing_name) in booking_information
    assert len(booking_information) == 2


def _create_activities_for_test(booking_activity_out_of_date, booking_event_OK, booking_event_out_of_date,
                                booking_thing_OK, booking_thing_stock_34, booking_user_34,
                                booking_user_cant_book_free_offers, user_93):
    booking_thing_OK_activity = create_booking_activity(booking_thing_OK, 'booking', verb='insert',
                                                        issued_at=datetime(2018, 4, 11))
    booking_event_OK_activity = create_booking_activity(booking_event_OK, 'booking', verb='insert',
                                                        issued_at=datetime(2018, 4, 12))
    booking_thing_stock_34_activity = create_booking_activity(booking_thing_stock_34, 'booking', verb='insert',
                                                              issued_at=datetime(2018, 4, 12))
    booking_event_out_of_date_activity = create_booking_activity(booking_event_out_of_date, 'booking', verb='insert',
                                                                 issued_at=datetime(2018, 4, 12))
    booking_user_34_activity = create_booking_activity(booking_user_34, 'booking', verb='insert',
                                                       issued_at=datetime(2018, 4, 12))
    booking_user_cant_book_free_offers_activity = create_booking_activity(booking_user_cant_book_free_offers, 'booking',
                                                                          verb='insert',
                                                                          issued_at=datetime(2018, 4, 13))
    booking_activity_out_of_date_activity = create_booking_activity(booking_activity_out_of_date, 'booking', 'insert',
                                                                    issued_at=datetime(2018, 1, 1))
    user_activity = create_user_activity(user_93, 'user', 'insert', issued_at=datetime(2018, 4, 12))
    booking_activity_delete = create_booking_activity(booking_event_OK, 'booking', 'delete',
                                                      issued_at=datetime(2018, 4, 12))
    return booking_activity_delete, booking_activity_out_of_date_activity, booking_event_OK_activity, booking_event_out_of_date_activity, booking_thing_OK_activity, booking_thing_stock_34_activity, booking_user_34_activity, booking_user_cant_book_free_offers_activity, user_activity


def _create_bookings_for_test():
    user_93 = create_user(departement_code='93', email='93@email.com')
    user_93_2 = create_user(departement_code='93', email='93_2@email.com')
    user_cant_book_free_offers = create_user(departement_code='93', email='cnbfo@email.com', can_book_free_offers=False)
    user_34 = create_user(departement_code='34', email='34@email.com')
    offerer = create_offerer(name='Librairies et événements')
    venue_75 = create_venue(offerer, postal_code='75001', city='Paris', departement_code='75', siret=offerer.siren + '12345')
    venue_34 = create_venue(offerer, postal_code='34500', city='Béziers', departement_code='34', siret=offerer.siren + '54321')
    stock_thing = create_stock_with_thing_offer(offerer, venue_75, thing_offer=None, price=0)
    stock_event = create_stock_with_event_offer(offerer, venue_75, price=0)
    stock_event.eventOccurrence.beginningDatetime = datetime(2018, 4, 21)
    stock_event.bookingLimitDatetime = datetime(2018, 4, 20)
    stock_thing_34 = create_stock_with_thing_offer(offerer, venue_34, thing_offer=None, price=0)
    stock_event_out_of_date = create_stock_with_event_offer(offerer, venue_75, price=0)
    stock_event_out_of_date.eventOccurrence.beginningDatetime = datetime(2018, 6, 21)
    stock_event_out_of_date.bookingLimitDatetime = datetime(2018, 6, 20)
    booking_thing_OK = create_booking(user_93, stock_thing, venue_75)
    booking_event_OK = create_booking(user_93, stock_event, venue_75)
    booking_thing_stock_34 = create_booking(user_93, stock_thing_34, venue_34)
    booking_event_out_of_date = create_booking(user_93, stock_event_out_of_date, venue_75)
    booking_user_34 = create_booking(user_34, stock_event, venue_75)
    booking_user_cant_book_free_offers = create_booking(user_cant_book_free_offers, stock_thing, venue_75)
    booking_activity_out_of_date = create_booking(user_93_2, stock_thing, venue_75)
    return booking_activity_out_of_date, booking_event_OK, booking_event_out_of_date, booking_thing_OK, booking_thing_stock_34, booking_user_34, booking_user_cant_book_free_offers


def _save_all_activities(*objects):
    for obj in objects:
        db.session.add(obj)
    db.session.commit()


def _is_in_date_range(date, date_min, date_max):
    if date is None:
        return True
    dt_date_min = datetime.strptime(date_min, '%Y-%m-%d')
    dt_date_max = datetime.strptime(date_max, '%Y-%m-%d')
    return dt_date_min <= date <= dt_date_max
