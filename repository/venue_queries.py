from datetime import datetime

from models import PcObject, ApiErrors
from models import Venue, Offer, EventOccurrence, Event, Thing, Stock, Offerer, UserOfferer, User
from models.db import db
from models.venue import TooManyVirtualVenuesException
from models.activity import load_activity
from sqlalchemy import and_
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
                is_virtual=None,
                offer_status=None, 
                is_validated=None,
                has_offerer_with_siren=None,
                has_validated_user_offerer=None,
                has_validated_user=None):

    query = db.session.query(Venue) 
    if is_virtual is not None:
        if is_virtual:
            query = query.filter(Venue.isVirtual == True)
        else:
            query = query.filter(Venue.isVirtual == False)

    if has_validated_offerer is not None or has_offerer_with_siren is not None or has_validated_user_offerer is not None or has_validated_user is not None:
        query = query.join(Offerer)

        if has_validated_offerer is not None:
            is_valid = Offerer.validationToken == None
            if has_validated_offerer:
                query = query.filter(is_valid)
            else:
                query = query.filter(~is_valid)

        if has_offerer_with_siren is not None:
            has_siren = Offerer.siren != None
            if has_offerer_with_siren:
                query = query.filter(has_siren)
            else:
                query = query.filter(~has_siren)

        if has_validated_user_offerer is not None or has_validated_user is not None:
            query = query.join(UserOfferer)
            if has_validated_user_offerer is not None:
                is_valid = UserOfferer.validationToken == None
                if has_validated_user_offerer:
                    query = query.filter(Offerer.users.any(is_valid))
                else:
                    query = query.filter(~Offerer.users.any(is_valid))

            if has_validated_user is not None:
                is_valid = User.validationToken == None
                query = query.join(User)
                if has_validated_user:
                    query = query.filter(Offerer.users.any(is_valid))
                else:
                    query = query.filter(~Offerer.users.any(is_valid))

    if dpt:
        query = query.filter(Venue.departementCode.in_(dpt))
    
    if zip_codes: 
        query = query.filter(Venue.postalCode.in_(zip_codes))
 
    if from_date or to_date:
        Activity = load_activity()
        is_on_table_venue = Activity.table_name == 'venue'
        is_insert = Activity.verb == 'insert'
        activity_data_id_matches_venue_id = Activity.data['id'].astext.cast(db.Integer) == Venue.id
        query = query.join(Activity, activity_data_id_matches_venue_id).filter(and_(is_on_table_venue, is_insert))

        if from_date:
            query = query.filter(Activity.issued_at >= from_date)
        if to_date:
            query = query.filter(Activity.issued_at <= to_date)
    
    if has_siret is not None:
        if has_siret:
            query = query.filter(Venue.siret != None)
        else:
            query = query.filter(Venue.siret == None)
            
    if is_validated is not None:
        if is_validated:
            query = query.filter(Venue.validationToken == None)
        else:
            query = query.filter(Venue.validationToken != None)
    
    if offer_status:
        if offer_status == 'ALL':
            query = query.join(Offer)
        elif offer_status == "VALID":
            query = query.join(Offer)
            is_on_time_event = EventOccurrence.beginningDatetime > datetime.utcnow()
            is_not_soft_deleted_thing = Stock.isSoftDeleted == False
            is_on_time_thing = ((Stock.bookingLimitDatetime == None) | (Stock.bookingLimitDatetime > datetime.utcnow()))
            is_available_thing = ((Stock.available == None) | (Stock.available > 0))

            query_with_valid_event = query.join(EventOccurrence) \
                         .filter(is_on_time_event)

            query_with_valid_thing = query.join(Stock) \
                          .filter(is_not_soft_deleted_thing & is_on_time_thing & is_available_thing)

            query = query_with_valid_event.union_all(query_with_valid_thing)
        elif offer_status == "WITHOUT":
            query = query.filter(~Venue.offers.any())
        elif offer_status == "EXPIRED":
            query = query.join(Offer)
            is_on_time_event = EventOccurrence.beginningDatetime > datetime.utcnow()
            is_not_soft_deleted_thing = Stock.isSoftDeleted == False
            is_on_time_thing = ((Stock.bookingLimitDatetime == None) | (Stock.bookingLimitDatetime > datetime.utcnow()))
            is_available_thing = ((Stock.available == None) | (Stock.available > 0))

            query_with_valid_event = query.join(EventOccurrence) \
                         .filter(~is_on_time_event)

            query_with_valid_thing = query.join(Stock) \
                          .filter(~(is_not_soft_deleted_thing & is_on_time_thing & is_available_thing))

            query = query_with_valid_event.union_all(query_with_valid_thing)

    result = query.all()
    return result
