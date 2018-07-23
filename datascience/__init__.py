""" recommendations """
from datetime import datetime, timedelta
from sqlalchemy import desc
from sqlalchemy.sql.expression import func

from datascience.occasions import get_occasions, get_occasions_by_type
from models.event_occurence import EventOccurence
from models.mediation import Mediation
from models.offer import Offer
from models import Occasion
from models.pc_object import PcObject
from models.recommendation import Recommendation
from models.thing import Thing

__all__ = (
            'get_occasions',
            'get_occasions_by_type',
          )



def create_recommendation(user, thing_or_event, mediation=None):
    if thing_or_event is None:
        return None

    recommendation = Recommendation()
    recommendation.user = user

    occasion = Occasion.query \
        .filter((Occasion.thing == thing_or_event) | (Occasion.event == thing_or_event)) \
        .order_by(func.random()) \
        .first()
    recommendation.occasion = occasion

    if mediation:
        recommendation.mediation = mediation
    else:
        mediation = Mediation.query\
            .filter(Mediation.occasion == occasion)\
            .order_by(func.random())\
            .first()
        recommendation.mediation = mediation

    if isinstance(thing_or_event, Thing):
        last_offer = Offer.query \
            .filter(Offer.occasion == occasion) \
            .order_by(desc(Offer.bookingLimitDatetime)) \
            .first()
    else:
        last_offer = Offer.query\
            .join(EventOccurence) \
            .filter(EventOccurence.occasion == occasion) \
            .order_by(desc(Offer.bookingLimitDatetime)) \
            .first()

    if recommendation.mediation:
        recommendation.validUntilDate = datetime.utcnow() + timedelta(days=3)
    else:
        recommendation.validUntilDate = datetime.utcnow() + timedelta(days=1)

    if last_offer.bookingLimitDatetime:
        recommendation.validUntilDate = min(
            recommendation.validUntilDate,
            last_offer.bookingLimitDatetime - timedelta(minutes=1)
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
    for (index, occasion) in enumerate(get_occasions(limit, user=user, coords=coords)):

        while recommendation_count + index + inserted_tuto_mediations \
                in tuto_mediations:
            insert_tuto_mediation(user,
                                  tuto_mediations[recommendation_count + index
                                                  + inserted_tuto_mediations])
            inserted_tuto_mediations += 1
        recommendations.append(create_recommendation(user, occasion))
    return recommendations


def insert_tuto_mediation(user, tuto_mediation):
    recommendation = Recommendation()
    recommendation.user = user
    recommendation.mediation = tuto_mediation
    recommendation.validUntilDate = datetime.utcnow() + timedelta(weeks=2)
    PcObject.check_and_save(recommendation)
