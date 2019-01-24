from datetime import datetime
from pprint import pformat

from sqlalchemy.exc import InternalError
from sqlalchemy.orm import aliased

from models import Stock, Offerer, User, ApiErrors, PcObject, EventOccurrence, Offer, Thing, ThingType, Venue
from utils.human_ids import dehumanize


def _check_offerer_user(query, user):
    return query.filter(
        Offerer.users.any(User.id == user.id)
    ).first_or_404()


def find_stocks_with_possible_filters(filters, user):
    query = Stock.queryNotSoftDeleted()
    if 'offererId' in filters:
        query = query.filter(Stock.offererId == dehumanize(filters['offererId']))
        _check_offerer_user(query.first_or_404().offerer.query, user)
    if 'hasPrice' in filters and filters['hasPrice'].lower() == 'true':
        query = query.filter(Stock.price != None)
    return query


def set_booking_recap_sent_and_save(stock):
    stock.bookingRecapSent = datetime.utcnow()
    PcObject.check_and_save(stock)


def save_stock(stock):
    try:
        PcObject.check_and_save(stock)
    except InternalError as ie:
        if 'check_stock' in str(ie.orig):
            api_errors = ApiErrors()

            if 'available_too_low' in str(ie.orig):
                api_errors.addError('available', 'la quantité pour cette offre'
                                    + ' ne peut pas être inférieure'
                                    + ' au nombre de réservations existantes.')
            elif 'bookingLimitDatetime_too_late' in str(ie.orig):
                api_errors.addError('bookingLimitDatetime',
                                    'la date limite de réservation pour cette offre est postérieure à la date de début de l\'évènement')
            else:
                app.log.error("Unexpected error in patch stocks: " + pformat(ie))

            raise api_errors
        else:
            raise ie


def find_stocks_of_finished_events_when_no_recap_sent():
    return Stock.queryNotSoftDeleted().join(EventOccurrence) \
        .filter((Stock.bookingLimitDatetime < datetime.utcnow()) &
                (EventOccurrence.beginningDatetime < datetime.utcnow()) &
                (Stock.bookingRecapSent == None))


def find_online_activation_stock():
    return Stock.query \
        .join(Offer) \
        .join(Venue) \
        .filter_by(isVirtual=True) \
        .reset_joinpoint() \
        .join(aliased(Offer)) \
        .join(Thing) \
        .filter_by(type=str(ThingType.ACTIVATION)) \
        .first()
