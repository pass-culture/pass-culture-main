from datetime import datetime, timedelta

from postgresql_audit.flask import versioning_manager
from sqlalchemy import and_, text
from sqlalchemy.exc import InternalError
from sqlalchemy.orm import aliased

from domain.keywords import create_ts_filter_finding_ts_query_in_at_least_one_of_the_models, \
                            create_filter_finding_all_keywords_in_at_least_one_of_the_models
from models import ApiErrors, \
    Booking, \
    Event, \
    EventOccurrence, \
    PcObject, \
    Offer, \
    Stock, \
    Thing, \
    User, \
    Venue, Offerer
from models.api_errors import ResourceNotFound
from utils.rest import query_with_order_by

booking_ts_filter = create_ts_filter_finding_ts_query_in_at_least_one_of_the_models(
    Event,
    Thing,
    Venue,
)

def find_all_by_user_id(user_id):
    return Booking.query.filter_by(userId=user_id).all()


def find_all_by_stock_id(stock):
    return Booking.query.filter_by(stockId=stock.id).all()

def filter_bookings_with_keywords_chain(query, keywords_chain):
    keywords_filter = create_filter_finding_all_keywords_in_at_least_one_of_the_models(
        booking_ts_filter,
        search
    )
    query = query.outerjoin(Event) \
                 .outerjoin(Thing) \
                 .outerjoin(Venue) \
                 .filter(keywords_filter) \
                 .reset_joinpoint()
    return query

def find_offerer_bookings(offerer_id, search=None, order_by=None, page=1):
    query = Booking.query.join(Stock) \
        .outerjoin(EventOccurrence) \
        .join(Offer,
              ((Stock.offerId == Offer.id) | \
               (EventOccurrence.offerId == Offer.id))) \
        .join(Venue) \
        .outerjoin(Thing, and_(Offer.thingId == Thing.id)) \
        .outerjoin(Event, and_(Offer.eventId == Event.id)) \
        .filter(Venue.managingOffererId == offerer_id) \
        .reset_joinpoint()

    if search:
        query = filter_bookings_with_keywords_chain(query, search)

    if order_by:
        query = query_with_order_by(query, order_by)

    bookings = query.paginate(int(page), per_page=10, error_out=False) \
                    .items

    return bookings


def find_bookings_from_recommendation(reco, user):
    booking_query = Booking.query.join(Stock)
    if reco.offer.eventId:
        booking_query = booking_query.join(EventOccurrence)
    booking_query = booking_query.join(Offer) \
        .filter(Booking.user == user) \
        .filter(Offer.id == reco.offerId)
    return booking_query.all()


def find_all_bookings_for_stock(stock):
    return Booking.query.join(Stock).filter_by(id=stock.id).all()


def find_by(token, email=None, offer_id=None):
    query = Booking.query.filter_by(token=token)

    if email:
        query = query.join(User).filter_by(email=email)

    if offer_id:
        query_offer_1 = Booking.query.join(Stock) \
            .join(Offer) \
            .filter_by(id=offer_id)
        query_offer_2 = Booking.query.join(Stock) \
            .join(EventOccurrence) \
            .join(aliased(Offer)) \
            .filter_by(id=offer_id)
        query_offer = query_offer_1.union_all(query_offer_2)
        query = query.intersect_all(query_offer)

    booking = query.first()

    if booking is None:
        errors = ResourceNotFound()
        errors.addError(
            'global',
            "Cette contremarque n'a pas été trouvée"
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
            api_errors.addError('insufficientFunds', "Le solde de votre pass n'est pas suffisant pour effectuer cette réservation.")
        raise api_errors


def find_by_id(booking_id):
    return Booking.query.filter_by(id=booking_id).first_or_404()


def find_all_ongoing_bookings_by_stock(stock):
    return Booking.query.filter_by(stockId=stock.id, isCancelled=False, isUsed=False).all()


def find_all_bookings_for_event_occurrence(event_occurrence):
    return Booking.query.join(Stock).join(EventOccurrence).filter_by(id=event_occurrence.id).all()


def find_final_offerer_bookings(offerer_id):
    join_on_offer_or_event_occurrence = (Stock.offerId == Offer.id) | (EventOccurrence.offerId == Offer.id)
    booking_on_event_older_than_two_days = (datetime.utcnow() > EventOccurrence.beginningDatetime + timedelta(hours=48))

    return Booking.query \
        .join(Stock) \
        .outerjoin(EventOccurrence) \
        .join(Offer, join_on_offer_or_event_occurrence) \
        .join(Venue) \
        .join(Offerer) \
        .filter(Offerer.id == offerer_id) \
        .filter(Booking.isCancelled == False) \
        .filter((Booking.isUsed == True) | booking_on_event_older_than_two_days) \
        .all()


def find_date_used(booking: Booking) -> datetime:
    Activity = versioning_manager.activity_cls
    find_by_id_and_is_used = "table_name='booking' " \
                             "AND verb='update' " \
                             "AND cast(old_data->>'id' AS INT) = %s " \
                             "AND cast(changed_data->>'isUsed' as boolean) = true" % booking.id

    activity = Activity.query.filter(text(find_by_id_and_is_used)).first()
    return activity.issued_at if activity else None
