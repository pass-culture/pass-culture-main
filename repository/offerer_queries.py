from sqlalchemy import or_

from models import Offerer, Venue, Offer, EventOccurrence, UserOfferer, User, Event, Booking, Stock, Recommendation
from models import RightsType
from models.activity import load_activity
from models.db import db


def get_by_offer_id(offer_id):
    return Offerer.query.join(Venue).join(Offer).filter_by(id=offer_id).first()


def get_by_event_occurrence_id(event_occurrence_id):
    return Offerer.query.join(Venue).join(Offer).join(EventOccurrence).filter_by(id=event_occurrence_id).first()


def find_all_admin_offerer_emails(offerer_id):
    return [result.email for result in Offerer.query.filter_by(id=offerer_id).join(UserOfferer).filter_by(rights=RightsType.admin).filter_by(validationToken=None).join(
        User).with_entities(User.email)]


def find_all_recommendations_for_offerer(offerer):
    return Recommendation.query.join(Offer).join(Venue).join(Offerer).filter_by(id=offerer.id).all()


def find_all_offerers_with_managing_user_information():
    query = db.session.query(Offerer.id, Offerer.name, Offerer.siren, Offerer.postalCode, Offerer.city, User.firstName,
                             User.lastName, User.email, User.phoneNumber, User.postalCode) \
        .join(UserOfferer) \
        .join(User)

    result = query.order_by(Offerer.name, User.email).all()
    return result


def find_all_offerers_with_managing_user_information_and_venue():
    query = db.session.query(Offerer.id, Offerer.name, Offerer.siren, Offerer.postalCode, Offerer.city, Venue.name,
                             Venue.bookingEmail, Venue.postalCode, User.firstName, User.lastName, User.email,
                             User.phoneNumber, User.postalCode) \
        .join(UserOfferer) \
        .join(User) \
        .join(Venue)

    result = query.order_by(Offerer.name, Venue.name, User.email).all()
    return result


def find_all_offerers_with_managing_user_information_and_not_virtual_venue():
    query = db.session.query(Offerer.id, Offerer.name, Offerer.siren, Offerer.postalCode, Offerer.city, Venue.name,
                             Venue.bookingEmail, Venue.postalCode, User.firstName, User.lastName, User.email,
                             User.phoneNumber, User.postalCode) \
        .join(UserOfferer) \
        .join(User) \
        .join(Venue)

    result = query.filter(Venue.isVirtual == False).order_by(Offerer.name, Venue.name, User.email).all()
    return result


def find_all_offerers_with_venue():
    query = db.session.query(Offerer.id, Offerer.name, Venue.id, Venue.name, Venue.bookingEmail, Venue.postalCode,
                             Venue.isVirtual) \
        .join(Venue)

    result = query.order_by(Offerer.name, Venue.name, Venue.id).all()
    return result


def find_all_pending_validation():
    return Offerer.query.join(UserOfferer) \
        .filter(or_(UserOfferer.validationToken != None, Offerer.validationToken != None)) \
        .order_by(Offerer.id).all()


def find_first_by_user_offerer_id(user_offerer_id):
    return Offerer.query.join(UserOfferer).filter_by(id=user_offerer_id).first()

from pprint import pprint
def find_filtered_offerers(dpt=None,
                           zip_codes=None,
                           from_date=None,
                           to_date=None,
                           has_siren=None,
                           has_not_virtual_venue=None,
                           has_validated_venue=None,
                           offer_status=None,
                           is_validated=None,
                           has_validated_user=None,
                           has_bank_information=None,
                           is_active=None,
                           has_validated_user_offerer=None):
    
    query = db.session.query(Offerer)
    if dpt is not None:
        query = _filter_by_dpt(query, dpt)
    if zip_codes is not None:
        query = _filter_by_zip_codes(query, zip_codes)
    if from_date is not None or to_date is not None:
        query = _filter_by_date(query, from_date, to_date)
    if has_siren is not None:
        query = _filter_by_has_siren(query, has_siren)
    if has_not_virtual_venue is not None:
        query = _filter_by_has_not_virtual_venue(query, has_not_virtual_venue)
    if has_validated_venue is not None:
        query = _filter_by_has_validated_venue(query, has_validated_venue)
    if offer_status is not None:
        query = _filter_by_offer_status(query, offer_status)
    if is_validated is not None:
        query = _filter_by_is_validated(query, is_validated)
    if has_validated_user is not None:
        query = _filter_by_has_validated_user(query, has_validated_user)
    if has_bank_information is not None:
        query = _filter_by_has_bank_information(query, has_bank_information)
    if is_active is not None:
        query = _filter_by_is_active(query, is_active)
    if has_validated_user_offerer is not None:
        query = _filter_by_has_validated_user_offerer(query, has_validated_user_offerer)

    result = query.all()
    return result


def _filter_by_dpt(query, dpt):
    previous_dpt_filter = None
    dpt_filter = None
    final_dpt_filter = None

    # create filter where begins with string from list

    for d in dpt:
        if dpt_filter is not None:
            previous_dpt_filter = dpt_filter
            if final_dpt_filter is not None:
                previous_dpt_filter = final_dpt_filter

        dpt_filter = Offerer.postalCode.op(d + '%')
        
        if previous_dpt_filter is not None:
            final_dpt_filter = previous_dpt_filter | dpt_filter




    for d in dpt:
        if dpt_filter is not None:
            previous_dpt_filter = dpt_filter
            if final_dpt_filter is not None:
                previous_dpt_filter = final_dpt_filter

        dpt_filter = Offerer.postalCode.like(d + '%')
        
        if previous_dpt_filter is not None:
            final_dpt_filter = previous_dpt_filter | dpt_filter

    query = query.filter(final_dpt_filter)

    return query


def _filter_by_zip_codes(query, zip_codes):
    query = query.filter(Offerer.postalCode.in_(zip_codes))
    return query


def _filter_by_date(query, from_date, to_date):
    if to_date:
        query=query
    else:
        query = query
    return query


def _filter_by_has_siren(query, has_siren):
    if has_siren:
        query=query
    else:
        query = query
    return query


def _filter_by_has_not_virtual_venue(query, has_not_virtual_venue):
    if has_not_virtual_venue:
        query=query
    else:
        query = query
    return query


def _filter_by_has_validated_venue(query, has_validated_venue):
    if has_validated_venue:
        query=query
    else:
        query = query
    return query


def _filter_by_offer_status(query, offer_status):
    if offer_status:
        query=query
    else:
        query = query
    return query


def _filter_by_is_validated(query, is_validated):
    if is_validated:
        query=query
    else:
        query = query
    return query


def _filter_by_has_validated_user(query, has_validated_user):
    if has_validated_user:
        query=query
    else:
        query = query
    return query


def _filter_by_has_bank_information(query, has_bank_information):
    if has_bank_information:
        query=query
    else:
        query = query
    return query


def _filter_by_is_active(query, is_active):
    if is_active:
        query=query
    else:
        query = query
    return query


def _filter_by_has_validated_user_offerer(query, has_validated_user_offerer):
    if has_validated_user_offerer:
        query=query
    else:
        query = query
    return query
