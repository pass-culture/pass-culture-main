from pcapi.core.users.models import User
from pcapi.domain.ts_vector import create_filter_matching_all_keywords_in_any_model
from pcapi.domain.ts_vector import create_get_filter_matching_ts_query_in_any_model
from pcapi.models import Offer
from pcapi.models import Offerer
from pcapi.models import UserOfferer
from pcapi.models import Venue


get_filter_matching_ts_query_for_offerer = create_get_filter_matching_ts_query_in_any_model(Offerer, Venue)


def find_by_id(id):  # pylint: disable=redefined-builtin
    return Offerer.query.filter_by(id=id).first()


def find_by_siren(siren) -> Offerer:
    return Offerer.query.filter_by(siren=siren).first()


def get_by_offer_id(offer_id):
    return Offerer.query.join(Venue).join(Offer).filter_by(id=offer_id).first()


def find_new_offerer_user_email(offerer_id):
    return UserOfferer.query.filter_by(offererId=offerer_id).join(User).with_entities(User.email).first()[0]


def find_first_by_user_offerer_id(user_offerer_id):
    return Offerer.query.join(UserOfferer).filter_by(id=user_offerer_id).first()


def filter_offerers_with_keywords_string(query, keywords_string):
    keywords_filter = create_filter_matching_all_keywords_in_any_model(
        get_filter_matching_ts_query_for_offerer, keywords_string
    )
    query = query.filter(keywords_filter)
    return query


def check_if_siren_already_exists(siren):
    return Offerer.query.filter_by(siren=siren).count() > 0


def keep_offerers_with_at_least_one_physical_venue(query):
    return query.filter(Offerer.managedVenues.any(Venue.isVirtual == False))


def keep_offerers_with_no_physical_venue(query):
    is_not_virtual = Venue.isVirtual == False
    return query.filter(~Offerer.managedVenues.any(is_not_virtual))
