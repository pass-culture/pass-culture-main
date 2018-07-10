""" recommendations """
from datetime import datetime, timedelta
from random import randint
from flask import current_app as app
from sqlalchemy import desc
from sqlalchemy.sql.expression import func

from utils.attr_dict import AttrDict
import utils.logger 

Event = app.model.Event
EventOccurence = app.model.EventOccurence
Mediation = app.model.Mediation
Offer = app.model.Offer
Recommendation = app.model.Recommendation
Thing = app.model.Thing

app.datascience = AttrDict()
from datascience.occasions import get_occasions


def create_recommendation(user, occasion, mediation=None):

    if occasion is None:
        return None

    recommendation = Recommendation()
    recommendation.user = user

    if mediation:
        recommendation.mediation = mediation
    else:
        if isinstance(occasion, Thing):
            query = Mediation.query.filter_by(thing=occasion)
        else:
            query = Mediation.query.filter_by(event=occasion)
        with app.db.session.no_autoflush:
            random_mediation = query.order_by(func.random())\
                                    .first()

        if random_mediation:
            recommendation.mediation = random_mediation
        elif isinstance(occasion, Thing):
            recommendation.thing = occasion
        elif isinstance(occasion, Event):
            recommendation.event = occasion

    if isinstance(occasion, Thing):
        last_offer = Offer.query.filter(Offer.thing == occasion)\
                                .order_by(desc(Offer.bookingLimitDatetime))\
                                .first()
    else:
        last_offer = Offer.query.join(EventOccurence)\
                                .filter(EventOccurence.eventId == occasion.id)\
                                .order_by(desc(Offer.bookingLimitDatetime))\
                                .first()

    if last_offer.bookingLimitDatetime:
        recommendation.validUntilDate = last_offer.bookingLimitDatetime - timedelta(minutes=1)
    else:
        recommendation.validUntilDate = datetime.utcnow() + timedelta(days=2)

    app.model.PcObject.check_and_save(recommendation)
    return recommendation


def create_recommendations(limit=3, user=None, coords=None):
    if user and user.is_authenticated:
        recommendation_count = Recommendation.query.filter_by(user=user)\
                                .count()

    recommendations = []
    tuto_mediations = {}

    for to in Mediation.query.filter(Mediation.tutoIndex != None).all():
        tuto_mediations[to.tutoIndex] = to

    inserted_tuto_mediations = 0
    for (index, occasion) in enumerate(get_occasions(limit, user=user, coords=coords)):

        while recommendation_count + index + inserted_tuto_mediations\
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
    app.model.PcObject.check_and_save(recommendation)
