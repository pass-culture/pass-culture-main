""" recommendations """
from flask import current_app as app
from datetime import datetime, timedelta
from random import randint
from sqlalchemy.sql.expression import func

from utils.attr_dict import AttrDict
from utils.content import get_source
from utils.includes import offers_includes

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
        first_um = UserMediation.query.filter_by(user=user)\
                                .first()
    offers = get_offers(user, limit)
    for (index, offer) in enumerate(offers):

        # CREATE
        um = UserMediation()
        um.user = user
        um.validUntilDate = datetime.now() + timedelta(days=2) # TODO: make this smart based on event dates, etc.

        # LOOK IF OFFER HAS (THING OR EVENT)(IE SOURCE) WITH MEDIATIONS
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
        # ADD A TAG FOR THE FIRST UM
        if first_um is None and index == 0:
            um.isFirst = True

        # SAVE AND DO THE UM OFFER JOIN
        app.model.PcObject.check_and_save(um)
        umo = UserMediationOffer()
        umo.offer = offer
        umo.userMediation = um
        app.model.PcObject.check_and_save(umo)
