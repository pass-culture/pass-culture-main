from typing import Dict, List

from domain.departments import get_departement_codes_from_user
from models import Offer, User
from repository.offer_queries import get_active_offers, \
    get_offers_for_recommendation, order_by_with_criteria


def get_offers_for_recommendations_discovery_v2(user: User,
                                                seen_recommendation_ids: List[int] = [],
                                                limit: int = 3) -> List[Offer]:
    departement_codes = get_departement_codes_from_user(user)

    offers = get_offers_for_recommendation(user=user,
                                           departement_codes=departement_codes,
                                           limit=limit,
                                           seen_recommendation_ids=seen_recommendation_ids)

    return offers


def get_offers_for_recommendations_discovery(user: User,
                                             pagination_params: Dict,
                                             limit: int = 3) -> List[Offer]:
    departement_codes = get_departement_codes_from_user(user)

    offers = get_active_offers(departement_codes=departement_codes,
                               limit=limit,
                               order_by=order_by_with_criteria,
                               pagination_params=pagination_params,
                               user=user)

    return offers
