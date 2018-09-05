""" recommendations """
from datetime import datetime, timedelta
from sqlalchemy import func

from models import Recommendation, Offer, Mediation, PcObject
from recommendations_engine import get_offers_for_recommendations_discovery,\
                                   get_offers_for_recommendations_search
from utils.logger import logger


class RecommendationNotFoundException(Exception):
    pass


def give_requested_recommendation_to_user(user, offer_id, mediation_id):
    recommendation = None

    if mediation_id or offer_id:
        recommendation = _find_recommendation(offer_id, mediation_id)

        if recommendation is None:
            recommendation = _create_recommendation_from_ids(user, offer_id, mediation_id=mediation_id)
            logger.info('Creating Recommendation with offer_id=%s mediation_id=%s' % (offer_id, mediation_id))

    return recommendation


def create_recommendations_for_discovery(limit=3, user=None, coords=None):
    if user and user.is_authenticated:
        recommendation_count = Recommendation.query.filter_by(user=user) \
            .count()

    recommendations = []
    tuto_mediations = {}

    for to in Mediation.query.filter(Mediation.tutoIndex != None).all():
        tuto_mediations[to.tutoIndex] = to

    inserted_tuto_mediations = 0
    for (index, offer) in enumerate(get_offers_for_recommendations_discovery(limit, user=user, coords=coords)):

        while recommendation_count + index + inserted_tuto_mediations \
                in tuto_mediations:
            insert_tuto_mediation(user,
                                  tuto_mediations[recommendation_count + index
                                                  + inserted_tuto_mediations])
            inserted_tuto_mediations += 1
        recommendations.append(_create_recommendation(user, offer))
    return recommendations


def insert_tuto_mediation(user, tuto_mediation):
    recommendation = Recommendation()
    recommendation.user = user
    recommendation.mediation = tuto_mediation
    recommendation.validUntilDate = datetime.utcnow() + timedelta(weeks=2)
    PcObject.check_and_save(recommendation)


def _no_mediation_or_mediation_does_not_match_offer(mediation, offer_id):
    return mediation is None or (offer_id and (mediation.offerId != offer_id))


def _find_recommendation(offer_id, mediation_id):
    logger.info('Requested Recommendation with offer_id=%s mediation_id=%s' % (offer_id, mediation_id))
    query = Recommendation.query
    if offer_id:
        query=query.join(Offer)
    mediation = Mediation.query.filter_by(id=mediation_id).first()
    offer = Offer.query.filter_by(id=offer_id).first()

    if mediation_id:
        if _no_mediation_or_mediation_does_not_match_offer(mediation, offer_id):
            logger.info('Mediation not found or found but not matching offer for offer_id=%s mediation_id=%s'
                        % (offer_id, mediation_id))
            raise RecommendationNotFoundException()

        query = query.filter(Recommendation.mediationId == mediation_id)

    if offer_id:
        if offer is None:
            logger.info('Offer not found for offer_id=%s' % (offer_id, ))
            raise RecommendationNotFoundException()

        query = query.filter(Offer.id == offer_id)

    return query.first()


def _create_recommendation_from_ids(user, offer_id, mediation_id=None):
    mediation = Mediation.query.filter_by(id=mediation_id).first()
    offer = Offer.query.filter_by(id=offer_id).first()
    return _create_recommendation(user, offer, mediation=mediation)


def _create_recommendation(user, offer, mediation=None):
    recommendation = Recommendation()
    recommendation.user = user
    recommendation.offer = offer

    if mediation:
        recommendation.mediation = mediation
    else:
        mediation = Mediation.query\
            .filter(Mediation.offer == offer)\
            .order_by(func.random())\
            .first()
        recommendation.mediation = mediation

    if recommendation.mediation:
        recommendation.validUntilDate = datetime.utcnow() + timedelta(days=3)
    else:
        recommendation.validUntilDate = datetime.utcnow() + timedelta(days=1)

    if offer.lastStock and offer.lastStock.bookingLimitDatetime:
        recommendation.validUntilDate = min(
            recommendation.validUntilDate,
            offer.lastStock.bookingLimitDatetime - timedelta(minutes=1)
        )

    PcObject.check_and_save(recommendation)
    return recommendation

def create_recommendations_for_search(page=1, user=None, search=None):

    offers = get_offers_for_recommendations_search(page, search)

    # now check that recommendations from these filtered offers
    # match with already built recommendations coming from the same search
    offer_ids = [offer.id for offer in offers]
    already_created_recommendations = Recommendation.query.filter(
        Recommendation.userId == user.id,
        Recommendation.offerId.in_(offer_ids),
        Recommendation.search == search
    )
    offer_ids_with_already_created_recommendations = [
        recommendation.offerId for recommendation in already_created_recommendations
    ]
    recommendations = []
    recommendations_to_save = []
    for offer in offers:
        if offer.id in offer_ids_with_already_created_recommendations:
            # NOTE: these arrays are mapped like:
            # offer_ids_with_already_created_recommendations [<offerId1>, <offerId2>,...]
            # already_created_recommendations [<reco.offerId1>, <reco.offerId2>]
            # so we can find the matching reco given the index in the offer ids array
            recommendation_index = offer_ids_with_already_created_recommendations.index(offer.id)
            recommendation = already_created_recommendations[recommendation_index]
        else:
            recommendation = _create_recommendation(user, offer)
            recommendation.search = search
            recommendations_to_save.append(recommendation)

        recommendations.append(recommendation)

    if recommendations_to_save:
        PcObject.check_and_save(*recommendations_to_save)

    return recommendations
