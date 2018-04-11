""" recommendations """
from flask import current_app as app
from datetime import datetime, timedelta
from random import randint
from sqlalchemy.sql.expression import func

from utils.attr_dict import AttrDict
from utils.content import get_source

Event = app.model.Event
EventOccurence = app.model.EventOccurence
Mediation = app.model.Mediation
Thing = app.model.Thing
UserMediation = app.model.UserMediation
UserMediationOffer = app.model.UserMediationOffer

app.recommendations = AttrDict()

from recommendations.offers import get_offers


def create_recommendations(user, limit=3):
    if user.is_authenticated:
        um_count = UserMediation.query.filter_by(user=user)\
                                .count()

    offers = get_offers(user, limit)

    tuto_mediations = {}

    for to in Mediation.query.filter(Mediation.tutoIndex!=None).all():
        tuto_mediations[to.tutoIndex] = to

    inserted_tuto_mediations = 0
    for (index, offer) in enumerate(offers):

        while um_count+index+inserted_tuto_mediations in tuto_mediations:
            insert_tuto_mediation(user,
                                  tuto_mediations[um_count + index
                                                  + inserted_tuto_mediations])
            inserted_tuto_mediations += 1
        # CREATE
        um = UserMediation()
        um.user = user
        um.validUntilDate = datetime.now() + timedelta(days=2) # TODO: make this smart based on event dates, etc.

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
            um.mediation = mediation

        # SAVE AND DO THE UM OFFER JOIN
        app.model.PcObject.check_and_save(um)
        umo = UserMediationOffer()
        umo.offer = offer
        umo.userMediation = um
        app.model.PcObject.check_and_save(umo)


def insert_tuto_mediation(user, tuto_mediation):
    um = UserMediation()
    um.user = user
    um.mediation = tuto_mediation
    um.validUntilDate = datetime.now() + timedelta(weeks=2)
    # ADD A TAG FOR THE FIRST UM
    if tuto_mediation.tutoIndex == 0:
        um.isFirst = True
    app.model.PcObject.check_and_save(um)
