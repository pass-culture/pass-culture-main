import factory

from pcapi.core.offers.factories import VenueFactory
import pcapi.core.providers.models
from pcapi.core.testing import BaseFactory


class ProviderFactory(BaseFactory):
    class Meta:
        model = pcapi.core.providers.models.Provider
        sqlalchemy_get_or_create = ["localClass"]

    name = factory.Sequence("Provider {}".format)
    localClass = factory.Sequence("{}Stocks".format)


class APIProviderFactory(BaseFactory):
    class Meta:
        model = pcapi.core.providers.models.Provider

    name = factory.Sequence("Provider {}".format)
    apiUrl = factory.Sequence("https://{}.example.org/stocks".format)


class VenueProviderFactory(BaseFactory):
    class Meta:
        model = pcapi.core.providers.models.VenueProvider

    venue = factory.SubFactory(VenueFactory)
    provider = factory.SubFactory(ProviderFactory)

    venueIdAtOfferProvider = factory.SelfAttribute("venue.siret")


class AllocineVenueProviderFactory(BaseFactory):
    class Meta:
        model = models.AllocineVenueProvider

    venue = factory.SubFactory(VenueFactory)
    provider = factory.SubFactory(ProviderFactory)
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
