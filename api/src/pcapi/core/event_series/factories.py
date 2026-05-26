import factory

from pcapi.core.factories import BaseFactory
from pcapi.core.offers import factories as offers_factories

from . import models


class EventSeriesFactory(BaseFactory[models.EventSeries]):
    class Meta:
        model = models.EventSeries

    name = factory.Sequence("Event Series {}".format)
    description = factory.Faker("text")
    mediation_uuid = None


class EventSeriesOfferLinkFactory(BaseFactory[models.EventSeriesOfferLink]):
    class Meta:
        model = models.EventSeriesOfferLink
        exclude = ["event_series", "offer"]

    event_series = factory.SubFactory(EventSeriesFactory)
    offer = factory.SubFactory(offers_factories.OfferFactory)
    event_series_id = factory.LazyAttribute(lambda o: o.event_series.id)
    offer_id = factory.LazyAttribute(lambda o: o.offer.id)
