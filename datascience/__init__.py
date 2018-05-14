""" recommendations """
from datetime import datetime, timedelta
from random import randint
from flask import current_app as app
from sqlalchemy.sql.expression import func

from utils.attr_dict import AttrDict
from utils.content import get_source

Event = app.model.Event
EventOccurence = app.model.EventOccurence
Mediation = app.model.Mediation
Recommendation = app.model.Recommendation
RecommendationOffer = app.model.RecommendationOffer
Thing = app.model.Thing

app.datascience = AttrDict()

from datascience.offers import get_offers


def create_recommendations(limit=3, user=None, coords=None):
    if user and user.is_authenticated:
        recommendation_count = Recommendation.query.filter_by(user=user)\
                                .count()

    offers = get_offers(limit, user=user, coords=coords)

    tuto_mediations = {}

    for to in Mediation.query.filter(Mediation.tutoIndex != None).all():
        tuto_mediations[to.tutoIndex] = to

    inserted_tuto_mediations = 0
    for (index, offer) in enumerate(offers):

        while recommendation_count+index+inserted_tuto_mediations in tuto_mediations:
            insert_tuto_mediation(user,
                                  tuto_mediations[recommendation_count + index
                                                  + inserted_tuto_mediations])
            inserted_tuto_mediations += 1
        # CREATE
        recommendation = Recommendation()
        recommendation.user = user
        recommendation.validUntilDate = datetime.now() + timedelta(days=2) # TODO: make this smart based on event dates, etc.

        # LOOK IF OFFER HAS A THING OR AN EVENT (IE A SOURCE) WITH MEDIATIONS
        # AND PICK ONE OF THEM
        mediation_query = Mediation.query
        mediation_filter = None
        if offer.thingId:
            mediation_filter = offer.thingId and (Thing.id == offer.thingId)
            mediation_query = mediation_query.outerjoin(Thing)
        else:
            event_id = Event.query.filter(
                Event.occurences.any(EventOccurence.id == offer.eventOccurenceId))\
                           .first().id
            mediation_filter = Event.id == event_id
            mediation_query = mediation_query.outerjoin(Event)
        mediation = mediation_query.filter(mediation_filter)\
                                   .order_by(func.random())\
                                   .first()
        if mediation is not None:
            recommendation.mediation = mediation

        # SAVE AND DO THE UM OFFER JOIN
        app.model.PcObject.check_and_save(recommendation)
        recommendation_offer = RecommendationOffer()
        recommendation_offer.offer = offer
        recommendation_offer.recommendation = recommendation
        app.model.PcObject.check_and_save(recommendation_offer)


def insert_tuto_mediation(user, tuto_mediation):
    recommendation = Recommendation()
    recommendation.user = user
    recommendation.mediation = tuto_mediation
    recommendation.validUntilDate = datetime.now() + timedelta(weeks=2)
    # ADD A TAG FOR THE FIRST UM
    if tuto_mediation.tutoIndex == 0:
        recommendation.isFirst = True
    app.model.PcObject.check_and_save(recommendation)
