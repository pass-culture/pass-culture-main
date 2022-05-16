import factory

from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.testing import BaseFactory

from . import models


class AllocinePivotFactory(BaseFactory):
    class Meta:
        model = models.AllocinePivot

    venue = factory.SubFactory(VenueFactory)
    theaterId = "XXXXXXXXXXXXXXXXXX=="
    internalId = "PXXXXX"


class ProviderFactory(BaseFactory):
    class Meta:
        model = models.Provider
        sqlalchemy_get_or_create = ["localClass", "apiUrl"]

    name = factory.Sequence("Provider {}".format)
    localClass = factory.Sequence("{}Stocks".format)
    apiUrl = None
    enabledForPro = True
    isActive = True


class APIProviderFactory(BaseFactory):
    class Meta:
        model = models.Provider

    name = factory.Sequence("Provider {}".format)
    apiUrl = factory.Sequence("https://{}.example.org/stocks".format)
    enabledForPro = True
    isActive = True


class VenueProviderFactory(BaseFactory):
    class Meta:
        model = models.VenueProvider

    venue = factory.SubFactory(VenueFactory)
    provider = factory.SubFactory(APIProviderFactory)

    venueIdAtOfferProvider = factory.SelfAttribute("venue.siret")


class AllocineProviderFactory(BaseFactory):
    class Meta:
        model = models.Provider
        sqlalchemy_get_or_create = ["localClass"]

    name = factory.Sequence("Provider {}".format)
    localClass = "AllocineStocks"
    enabledForPro = True
    isActive = True


class AllocineVenueProviderFactory(BaseFactory):
    class Meta:
        model = models.AllocineVenueProvider

    venue = factory.SubFactory(VenueFactory)
    provider = factory.SubFactory(AllocineProviderFactory)
    venueIdAtOfferProvider = factory.SelfAttribute("venue.siret")
    internalId = factory.Sequence("P{}".format)
    isDuo = True
    quantity = 1000


class AllocineVenueProviderPriceRuleFactory(BaseFactory):
    class Meta:
        model = models.AllocineVenueProviderPriceRule

    allocineVenueProvider = factory.SubFactory(AllocineVenueProviderFactory)
    priceRule = "default"
    price = 5.5
