from datetime import datetime, timedelta

from sqlalchemy import func

from models import Recommendation, Offer, Mediation, ApiErrors, PcObject
from recommendations_engine import get_offers
from utils.config import BLOB_SIZE
from utils.logger import logger


def pick_random_offers_given_blob_size(recos, limit=BLOB_SIZE):
    return recos.order_by(func.random()) \
        .limit(limit) \
        .all()


def find_or_make_recommendation(user, offer_id,
                                mediation_id, from_user_id=None):
    query = Recommendation.query.join(Offer)
    logger.info('(requested) offer_id=' + str(offer_id)
                + ' mediation_id=' + str(mediation_id))
    if not mediation_id and not offer_id:
        return None
    if mediation_id:
        query = query.filter(Recommendation.mediationId == mediation_id)
    if offer_id:
        query = query.filter(Offer.id == offer_id)
    requested_recommendation = query.first()
    if requested_recommendation is None:
        if mediation_id:
            return None
        offer = Offer.query.filter_by(id=offer_id).first()
        mediation = Mediation.query.filter_by(id=mediation_id).first()
        requested_recommendation = create_recommendation(user, offer, mediation=mediation)

    if requested_recommendation is None:
        raise ApiErrors()

    return requested_recommendation


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
