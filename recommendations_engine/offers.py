from typing import Dict, List

from domain.departments import get_departement_codes_from_user
from models import Offer, User
from models.feature import FeatureToggle
from repository import feature_queries
from repository.offer_queries import get_active_offers, \
    get_offers_for_recommendation, order_by_with_criteria, get_active_offers_with_digital_first
from utils.feature import get_feature_end_of_quarantine_date


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

    if feature_queries.is_active(FeatureToggle.RECOMMENDATIONS_WITH_DIGITAL_FIRST):
        end_of_quarantine_date = get_feature_end_of_quarantine_date()
        offers = get_active_offers_with_digital_first(departement_codes=departement_codes,
                                                      limit=limit,
                                                      pagination_params=pagination_params,
                                                      user=user,
                                                      end_of_quarantine_date=end_of_quarantine_date)
    else:
        offers = get_active_offers(departement_codes=departement_codes,
                                   limit=limit,
                                   order_by=order_by_with_criteria,
                                   pagination_params=pagination_params,
                                   user=user)

    return offers
