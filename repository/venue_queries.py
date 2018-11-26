from datetime import datetime

from models import PcObject, ApiErrors
from models import Venue, Offer, EventOccurrence, Event, Thing, Stock, Offerer
from models.db import db
from models.venue import TooManyVirtualVenuesException
from models.activity import load_activity
from repository.offer_queries import with_active_and_validated_offerer


def save_venue(venue):
    try:
        PcObject.check_and_save(venue)
    except TooManyVirtualVenuesException:
        errors = ApiErrors()
        errors.addError('isVirtual', 'Un lieu pour les offres numériques existe déjà pour cette structure')
        raise errors


def find_by_id(venue_id):
    return Venue.query.filter_by(id=venue_id).first()


def find_venues(has_validated_offerer=None,
                dpt=None,
                zip_codes=None,
                from_date=None,
                to_date=None,
                has_siret=None,
                venue_type=None,
                has_offer=None, 
                is_validated=None):

    query = db.session.query(Venue) 

    if venue_type:
        if venue_type == 'NOT_VIRTUAL':
            query = query.filter(Venue.isVirtual == False)
        elif venue_type == 'VIRTUAL':
            dpt = None
            zip_codes = None
            query = query.filter(Venue.isVirtual == True)

    if has_validated_offerer:
        query = query.join(Offerer)
        if has_validated_offerer == 'YES':
            query = query.filter(Offerer.validationToken == None)
        elif has_validated_offerer == 'NO':
            query = query.filter(Offerer.validationToken != None)
    
    if dpt:
        zip_codes = None
        if len(dpt) == 1:
            query = query.filter(Venue.departementCode == dpt[0])
        else:
            query = query.filter(Venue.departementCode.in_(dpt))
    
    if zip_codes:
        if len(zip_codes) == 1:
            query = query.filter(Venue.postalCode == zip_codes[0])
        else:
            query = query.filter(Venue.postalCode.in_(zip_codes))
 
    if from_date or to_date:
        Activity = load_activity()
        query = query.join(Activity, Activity.table_name == 'venue') \
            .filter(Activity.verb == 'insert', Activity.data['id'].astext.cast(db.Integer)
               == Venue.id)
        if from_date:
            query = query.filter(Activity.issued_at >= from_date)
        if to_date:
            query = query.filter(Activity.issued_at <= to_date)
    
    if has_siret:
        if has_siret == 'NO':
            query = query.filter(Venue.siret == None)
        elif has_siret == 'YES':
            query = query.filter(Venue.siret != None)

    if is_validated:
        if is_validated == 'YES':
            query = query.filter(Venue.validationToken == None)
        elif is_validated == 'NO':
            query = query.filter(Venue.validationToken != None)
    
    if has_offer:
        if has_offer == 'ALL':
            query = query.join(Offer)

        elif has_offer == "VALID":
            query = query.join(Offer)

            query_with_valid_event = query.join(EventOccurrence) \
                         .filter(EventOccurrence.beginningDatetime > datetime.utcnow())

            query_with_valid_thing = query.join(Stock) \
                          .filter((Stock.isSoftDeleted == False)
                    & ((Stock.bookingLimitDatetime == None) 
                        | (Stock.bookingLimitDatetime > datetime.utcnow()))
                    & ((Stock.available == None) | (Stock.available > 0)))
    
            query = query_with_valid_event.union_all(query_with_valid_thing)
        elif has_offer == "WITHOUT":
            query = query.filter(~Venue.offers.any())
        elif has_offer == "EXPIRED":
            query = query.join(Offer)

            query_with_expired_event = query.join(EventOccurrence) \
                         .filter(EventOccurrence.beginningDatetime <= datetime.utcnow())

            query_with_expired_thing = query.join(Stock) \
                          .filter((Stock.isSoftDeleted == True)
                    | (Stock.bookingLimitDatetime <=
                       datetime.utcnow())
                    | (Stock.available == 0))
    
            query = query_with_expired_event.union_all(query_with_expired_thing)


    result = query.all()
    return result
