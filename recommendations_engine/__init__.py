""" recommendations """

from recommendations_engine.offers import get_offers, get_offers_by_type
from recommendations_engine.recommendations import create_recommendations, \
    RecommendationNotFoundException, give_requested_recommendation_to_user

__all__ = (
    'get_offers',
    'get_offers_by_type',
    'create_recommendations',
    'give_requested_recommendation_to_user',
    'RecommendationNotFoundException'
)
