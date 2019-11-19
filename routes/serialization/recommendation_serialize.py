from typing import List

from models import Recommendation
from routes.serialization import as_dict
from utils.includes import RECOMMENDATION_INCLUDES


def serialize_recommendations(recommendations: List[Recommendation]) -> List[dict]:
    serialized_recommendations = [serialize_recommendation(recommendation)
                                  for recommendation in recommendations]
    return serialized_recommendations


def serialize_recommendation(recommendation: Recommendation) -> dict:
    serialized_recommendation = as_dict(recommendation, includes=RECOMMENDATION_INCLUDES)
    return serialized_recommendation
