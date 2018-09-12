from datetime import datetime

from sqlalchemy.exc import InternalError
from sqlalchemy.orm import aliased

from models import Booking, Stock, EventOccurrence, Offer, Venue, User, PcObject, ApiErrors


class BookingNotFound(ApiErrors):
    pass
from models import Booking, Stock, EventOccurrence, Offer, Venue, Offerer, User
from sqlalchemy import func, distinct, text, union
from models.db import db
from models import Booking, Stock, EventOccurrence, User, Venue
from postgresql_audit.flask import versioning_manager

def load_activity():
    return versioning_manager.activity_cls


def find_all_by_user_id(user_id):
    return Booking.query.filter_by(userId=user_id).all()


def find_all_by_stock_id(stock):
    return Booking.query.filter_by(stockId=stock.id).all()


def find_all_by_offerer_sorted_by_date_modified_asc(offerer_id):
    query_event = Booking.query \
        .join(Stock) \
        .join(EventOccurrence) \
        .join(Offer) \
        .join(Venue) \
        .filter(Venue.managingOffererId == offerer_id) \
        .all()

    query_thing = Booking.query \
        .join(Stock) \
        .join(Offer) \
        .join(Venue) \
        .filter(Venue.managingOffererId == offerer_id) \
        .all()

    return sorted(query_event + query_thing, key=lambda b: b.dateModified)


def find_bookings_from_recommendation(reco, user):
    booking_query = Booking.query.join(Stock)
    if reco.offer.eventId:
        booking_query = booking_query.join(EventOccurrence)
    booking_query = booking_query.join(Offer) \
        .filter(Booking.user == user) \
        .filter(Offer.id == reco.offerId)
    return booking_query.all()


def find_all_with_soft_deleted_stocks():
    return Booking.query.join(Stock).filter_by(isSoftDeleted=True).all()


def find_by_token(token, email=None, offer_id=None):
    query = Booking.query.filter_by(token=token)
    if email:
        query = query.join(User).filter_by(email=email)
    if offer_id:
        query_offer_1 = Booking.query.join(Stock).join(Offer).filter_by(id=offer_id)
        query_offer_2 = Booking.query.join(Stock).join(EventOccurrence).join(aliased(Offer)).filter_by(id=offer_id)
        query_offer = query_offer_1.union_all(query_offer_2)
        query = query.intersect_all(query_offer)

    booking = query.first()

    if booking is None:
        errors = BookingNotFound()
        errors.addError(
            'global',
            "Ce coupon n'a pas été trouvé"
        )
        raise errors

    return booking


def save_booking(booking):
    try:
        PcObject.check_and_save(booking)
    except InternalError as internal_error:
        api_errors = ApiErrors()

        if 'tooManyBookings' in str(internal_error.orig):
            api_errors.addError('global', 'la quantité disponible pour cette offre est atteinte')
        elif 'insufficientFunds' in str(internal_error.orig):
            api_errors.addError('insufficientFunds', 'l\'utilisateur ne dispose pas de fonds suffisants pour '
                                                     'effectuer une réservation.')
        raise api_errors


def find_bookings_stats_per_department(time_intervall):
    return db.engine.execute('''
    SELECT
        booking_departement.department_code,
        date_trunc('{time_intervall}', activity.issued_at) AS intervall,
        COUNT(booking_departement.booking_id) AS bookings,
        COUNT(DISTINCT(booking_departement.user_id)) AS unique_bookings
    FROM
        (SELECT
            booking.id AS booking_id,
            COALESCE(thing_venue."departementCode", event_venue."departementCode") AS department_code,
            booking."userId" AS user_id,
            booking."isCancelled" AS cancelled_booking
        FROM booking
            LEFT JOIN stock ON booking."stockId" = stock.id
            LEFT OUTER JOIN event_occurrence ON stock."eventOccurrenceId" = event_occurrence.id
            LEFT OUTER JOIN offer AS event_offer ON event_occurrence."offerId"=event_offer.id
            LEFT OUTER JOIN offer AS thing_offer ON stock."offerId"=thing_offer.id
            LEFT OUTER JOIN venue AS thing_venue ON thing_offer."venueId"=thing_venue.id
            LEFT OUTER JOIN venue AS event_venue ON event_offer."venueId"=event_venue.id
        ) AS booking_departement
    LEFT JOIN activity ON booking_id = CAST(activity.changed_data->>'id' AS INT)
    LEFT JOIN "user" ON "user".id = user_id
    WHERE
        "user"."canBookFreeOffers"
        AND NOT cancelled_booking
        AND activity.verb = 'insert'
        AND activity.table_name = 'booking'
    GROUP BY date_trunc('{time_intervall}', activity.issued_at), department_code
    ORDER BY date_trunc('{time_intervall}', activity.issued_at), department_code
    '''.format(time_intervall=time_intervall)
    )
