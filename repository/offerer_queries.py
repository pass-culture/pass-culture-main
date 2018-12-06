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

    result = query.all()
    return result