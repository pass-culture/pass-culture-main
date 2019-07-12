import random

from local_providers.openagenda_events import OpenAgendaEvents
from models.db import db

from local_providers.local_provider import ProvidableInfo
from models.stock import Stock

class OpenAgendaStocks(OpenAgendaEvents):
    name = "Open Agenda Stocks"
    objectType = Stock

    def __next__(self):
        p_info_event = super().__next__

        p_info_stock = ProvidableInfo()
        p_info_stock.type = Stock
        p_info_stock.idAtProviders = p_info_event.idAtProviders
        p_info_stock.dateModifiedAtProvider = p_info_event.dateModifiedAtProvider

        return p_info_event, p_info_stock

        event.venue = self.venue
        stock = Stock()
        stock.idAtProvider = event.idAtProvider
        stock.dateModifiedAtProvider = event.dateModifiedAtProvider
        stock.event = event
        return stock

    def getDeactivatedObjectIds(self):
        return db.session.query(Stock.idAtProvider)\
                             .filter(Stock.provider == self.venue.provider,
                                     Stock.venue == self.venue,
                                     ~Stock.idAtProvider.in_(self.seen_uids))

    def updateObject(self, eventOrStock):
        if isinstance(eventOrStock, Event):
            super().updateObject(eventOrStock)
        else:
            stock = eventOrStock
            stock.event = self.providables[0]
            stock.price = random.randint(0, 10)*5

    def getObjectThumb(self, eventOrStock, index):
        if isinstance(eventOrStock, Event):
            return super().getObjectThumb(eventOrStock, index)
        else:
            return None

    def getObjectThumbDates(self, eventOrStock):
        if isinstance(eventOrStock, Event):
            return super().getObjectThumbDates(eventOrStock)
        else:
            return []
