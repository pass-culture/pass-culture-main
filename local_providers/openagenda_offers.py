import random

from flask import current_app as app

from models.event import Event
from models.offer import Offer

Event = Event
Offer = Offer


class OpenAgendaOffers(app.local_providers.OpenAgendaEvents):
    name = "Open Agenda Offers"
    objectType = Offer

    def __next__(self):
        p_info_event = super().__next__()

        p_info_offer = ProvidableInfo()
        p_info_offer.type = Offer
        p_info_offer.idAtProviders = p_info_event.idAtProviders
        p_info_offer.dateModifiedAtProvider = p_info_event.dateModifiedAtProvider

        return p_info_event, p_info_offer

        event.venue = self.venue
        offer = Offer()
        offer.idAtProvider = event.idAtProvider
        offer.dateModifiedAtProvider = event.dateModifiedAtProvider
        offer.event = event
        return offer

    def getDeactivatedObjectIds(self):
        return app.db.session.query(Offer.idAtProvider)\
                             .filter(Offer.provider == self.venue.provider,
                                     Offer.venue == self.venue,
                                     ~Offer.idAtProvider.in_(self.seen_uids))

    def updateObject(self, eventOrOffer):
        if isinstance(eventOrOffer, Event):
            super().updateObject(eventOrOffer)
        else:
            offer = eventOrOffer
            offer.event = self.providables[0]
            offer.price = random.randint(0, 10)*5

    def getObjectThumb(self, eventOrOffer, index):
        if isinstance(eventOrOffer, Event):
            return super().getObjectThumb(eventOrOffer, index)
        else:
            return None

    def getObjectThumbDates(self, eventOrOffer):
        if isinstance(eventOrOffer, Event):
            return super().getObjectThumbDates(eventOrOffer)
        else:
            return []


app.local_providers.OpenAgendaOffers = OpenAgendaOffers
