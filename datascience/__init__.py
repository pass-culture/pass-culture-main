""" recommendations """
from datetime import datetime, timedelta
from sqlalchemy.sql.expression import func

from datascience.offers import get_offers, get_offers_by_type
from models import Mediation, PcObject, Recommendation

__all__ = (
            'get_offers',
            'get_offers_by_type',
          )


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
