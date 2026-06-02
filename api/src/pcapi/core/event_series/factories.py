import factory

from pcapi.core.factories import BaseFactory

from . import models


class EventSeriesFactory(BaseFactory[models.EventSeries]):
    class Meta:
        model = models.EventSeries

    name = factory.Sequence("Event Series {}".format)
    description = factory.Faker("text")
    mediationUuid = None


class EventSeriesOfferLinkFactory(BaseFactory[models.EventSeriesOfferLink]):
    class Meta:
        model = models.EventSeriesOfferLink

    eventSeries = factory.SubFactory(EventSeriesFactory)
