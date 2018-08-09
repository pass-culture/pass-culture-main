from datetime import datetime, timedelta

from sqlalchemy import func

from models import Recommendation, Offer, Mediation, ApiErrors, PcObject
from recommendations_engine import get_offers
from utils.config import BLOB_SIZE
from utils.human_ids import dehumanize
from utils.logger import logger


class RecommendationNotFoundException(Exception):
    pass


def give_requested_recommendation_to_user(user, offer_id, mediation_id):
    recommendation = None

    if mediation_id or offer_id:
        recommendation = find_recommendation(dehumanize(offer_id), dehumanize(mediation_id))

        if recommendation is None:
            recommendation = create_recommendation_from_ids(user, offer_id, mediation_id=mediation_id)
            logger.info('Creating Recommendation with offer_id=%s mediation_id=%s' % (offer_id, mediation_id))

    return recommendation


def pick_random_offers_given_blob_size(recos, limit=BLOB_SIZE):
    return recos.order_by(func.random()) \
        .limit(limit) \
        .all()


def find_recommendation(offer_id, mediation_id):
    logger.info('Requested Recommendation with offer_id=%s mediation_id=%s' % (offer_id, mediation_id))
    query = Recommendation.query.join(Offer)
    mediation = Mediation.query.filter_by(id=mediation_id).first()
    offer = Offer.query.filter_by(id=offer_id).first()

    if mediation_id:
        if _no_mediation_or_mediation_does_not_match_offer(mediation, offer_id):
            logger.info('Mediation not found or found but not matching offer for offer_id=%s mediation_id=%s'
                        % (offer.id, mediation.id))
            raise RecommendationNotFoundException()

        query = query.filter(Recommendation.mediationId == mediation_id)

    if offer_id:
        if offer is None:
            logger.info('Offer not found for offer_id=%s' % (offer_id, ))
            raise RecommendationNotFoundException()

        query = query.filter(Offer.id == offer_id)

    return query.first()


def create_recommendation_from_ids(user, offer_id, mediation_id=None):
    mediation = Mediation.query.filter_by(id=mediation_id).first()
    offer = Offer.query.filter_by(id=offer_id).first()
    return create_recommendation(user, offer, mediation=mediation)


def create_recommendation(user, offer, mediation=None):
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

    if offer.lastStock.bookingLimitDatetime:
        recommendation.validUntilDate = min(
            recommendation.validUntilDate,
            offer.lastStock.bookingLimitDatetime - timedelta(minutes=1)
        )

    PcObject.check_and_save(recommendation)
    return recommendation


def create_recommendations(limit=3, user=None, coords=None):
    if user and user.is_authenticated:
        recommendation_count = Recommendation.query.filter_by(user=user) \
            .count()

    recommendations = []
    tuto_mediations = {}

    for to in Mediation.query.filter(Mediation.tutoIndex != None).all():
        tuto_mediations[to.tutoIndex] = to

    inserted_tuto_mediations = 0
    for (index, offer) in enumerate(get_offers(limit, user=user, coords=coords)):

        while recommendation_count + index + inserted_tuto_mediations \
                in tuto_mediations:
            insert_tuto_mediation(user,
                                  tuto_mediations[recommendation_count + index
                                                  + inserted_tuto_mediations])
            inserted_tuto_mediations += 1
        recommendations.append(create_recommendation(user, offer))
    return recommendations


def insert_tuto_mediation(user, tuto_mediation):
    recommendation = Recommendation()
    recommendation.user = user
    recommendation.mediation = tuto_mediation
    recommendation.validUntilDate = datetime.utcnow() + timedelta(weeks=2)
    PcObject.check_and_save(recommendation)


def _no_mediation_or_mediation_does_not_match_offer(mediation, offer_id):
    return mediation is None or (offer_id and (mediation.offerId != offer_id))
