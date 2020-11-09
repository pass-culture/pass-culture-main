from typing import List

from pcapi.models import Recommendation


def move_requested_recommendation_first(recommendations: List[Recommendation],
                                        requested_recommendation: Recommendation) -> List[Recommendation]:
    for index, recommendation in enumerate(recommendations):
        if recommendation == requested_recommendation \
                or recommendation.offer == requested_recommendation.offer:
            recommendations = recommendations[:index] + recommendations[index + 1:]
            break
    recommendations = [requested_recommendation] + recommendations
    return recommendations
