from repository.features import feature_paid_offers_enabled
from repository.recommendation_queries import find_unseen_tutorials_for_user
from utils.config import BLOB_SIZE, BLOB_UNREAD_NUMBER
from utils.logger import logger


def build_mixed_recommendations(created_recommendations, read_recommendations, unread_recommendations):
    recommendations = created_recommendations.copy()
    remaining_read = read_recommendations.copy()
    remaining_unread = unread_recommendations.copy()

    while _can_populate_with_read_or_unread_recommendations(recommendations, remaining_read, remaining_unread):
        recommendations, remaining_unread = _populate_recommendations(recommendations, remaining_unread)
        recommendations, remaining_read = _populate_recommendations(recommendations, remaining_read)

    if not feature_paid_offers_enabled():
        recommendations = _remove_recommendations_on_paid_offers(recommendations)

    return recommendations


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
        if reco.id == requested_recommendation.id:
            recos = recos[:i] + recos[i + 1:]
            break
    recos = [requested_recommendation] + recos
    return recos


def _can_populate_with_read_or_unread_recommendations(recommendations, read_recommendations, unread_recommendations):
    return len(recommendations) < BLOB_SIZE and (len(unread_recommendations) > 0 or len(read_recommendations) > 0)


def _compute_quantity_to_add(recommendations, potential_recommendations, max_to_add):
    return min(max_to_add, len(potential_recommendations), BLOB_SIZE - len(recommendations))


def _populate_recommendations(recommendations, potential_recommendations):
    quantity_to_add = _compute_quantity_to_add(recommendations, potential_recommendations, BLOB_UNREAD_NUMBER)
    populated_recommendations = recommendations + potential_recommendations[:quantity_to_add]
    remaining_potential = potential_recommendations[quantity_to_add:]
    return populated_recommendations, remaining_potential


def _remove_recommendations_on_paid_offers(recommendations):
    recommendations_on_free_offers = []
    for reco in recommendations:
        if all(stock.price == 0 for stock in reco.offer.stocks):
            recommendations_on_free_offers.append(reco)
    return recommendations_on_free_offers
