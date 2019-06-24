from repository.features import feature_paid_offers_enabled
from repository.recommendation_queries import find_unseen_tutorials_for_user
from utils.config import BLOB_SIZE, BLOB_UNREAD_NUMBER
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


def move_requested_recommendation_first(recos, requested_recommendation):
    for i, reco in enumerate(recos):
        if reco.id == requested_recommendation.id\
           or reco.offer.id == requested_recommendation.offer.id:
            recos = recos[:i] + recos[i + 1:]
            break
    recos = [requested_recommendation] + recos
    return recos
