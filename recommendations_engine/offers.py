from typing import List

from domain.departments import get_departement_codes_from_user
from models import OfferSQLEntity, UserSQLEntity
from repository.offer_queries import get_offers_for_recommendation


def get_offers_for_recommendations_discovery(user: UserSQLEntity,
                                             sent_offers_ids: List[int] = [],
                                             limit: int = 3) -> List[OfferSQLEntity]:
    departement_codes = get_departement_codes_from_user(user)

    offers = get_offers_for_recommendation(user=user, departement_codes=departement_codes, limit=limit,
                                           sent_offers_ids=sent_offers_ids)

    return offers
