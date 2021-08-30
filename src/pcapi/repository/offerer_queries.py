from datetime import date
from datetime import datetime

from pcapi.core.offerers.models import Offerer
from pcapi.core.users.models import User
from pcapi.domain.ts_vector import create_filter_matching_all_keywords_in_any_model
from pcapi.domain.ts_vector import create_get_filter_matching_ts_query_in_any_model
from pcapi.models import Offer
from pcapi.models import UserOfferer
from pcapi.models import Venue


get_filter_matching_ts_query_for_offerer = create_get_filter_matching_ts_query_in_any_model(Offerer, Venue)


def find_by_id(id):  # pylint: disable=redefined-builtin
    return Offerer.query.filter_by(id=id).one_or_none()


def get_by_offer_id(offer_id):
    return Offerer.query.join(Venue).join(Offer).filter_by(id=offer_id).one_or_none()


def find_new_offerer_user_email(offerer_id):
    return UserOfferer.query.filter_by(offererId=offerer_id).join(User).with_entities(User.email).first()[0]


def filter_offerers_with_keywords_string(query, keywords_string):
    keywords_filter = create_filter_matching_all_keywords_in_any_model(
        get_filter_matching_ts_query_for_offerer, keywords_string
    )
    query = query.filter(keywords_filter)
    return query


def check_if_siren_already_exists(siren):
    return Offerer.query.filter_by(siren=siren).count() > 0


def get_offerers_by_date_validated(date_validated: date) -> list[Offerer]:
    from_date = datetime.combine(date_validated, datetime.min.time())
    to = datetime.combine(date_validated, datetime.max.time())

    return Offerer.query.filter(Offerer.dateValidated.between(from_date, to)).all()
