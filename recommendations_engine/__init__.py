""" recommendations """

from recommendations_engine.offers import get_offers_for_recommendations_discovery,\
                                          get_offers_by_type
from recommendations_engine.recommendations import create_recommendations_for_discovery,\
                                                   create_recommendations_for_search,\
                                                   give_requested_recommendation_to_user,\
                                                   RecommendationNotFoundException

__all__ = (
    'create_recommendations_for_discovery',
    'create_recommendations_for_search',
    'get_offers_for_recommendations_discovery',
    'get_offers_by_type',
    'give_requested_recommendation_to_user',
    'RecommendationNotFoundException'
)
