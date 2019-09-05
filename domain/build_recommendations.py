from typing import List

from models import Recommendation
from repository.recommendation_queries import find_unseen_tutorials_for_user
from utils.logger import logger


def move_tutorial_recommendations_first(recos, seen_recommendation_ids, user):
    tutorial_recommendations = find_unseen_tutorials_for_user(seen_recommendation_ids, user)

    logger.debug(lambda: '(tuto recos) count %i', len(tutorial_recommendations))

    tutos_read = 0
    for reco in tutorial_recommendations:
        if reco.dateRead is not None:
            tutos_read += 1

        elif len(recos) >= reco.mediation.tutoIndex - tutos_read:
            recos = recos[:reco.mediation.tutoIndex - tutos_read] \
                    + [reco] \
                    + recos[reco.mediation.tutoIndex - tutos_read:]
    return recos


def move_requested_recommendation_first(recommendations: List[Recommendation],
                                        requested_recommendation: Recommendation) -> List[Recommendation]:
    for index, recommendation in enumerate(recommendations):
        if recommendation == requested_recommendation \
                or recommendation.offer == requested_recommendation.offer:
            recommendations = recommendations[:index] + recommendations[index + 1:]
            break
    recommendations = [requested_recommendation] + recommendations
    return recommendations
