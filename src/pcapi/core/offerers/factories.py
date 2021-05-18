import factory

from pcapi.core.offerers.models import VenueLabel
from pcapi.core.offerers.models import VenueType
from pcapi.core.offers.factories import VenueFactory
import pcapi.core.providers.models
from pcapi.core.providers.models import AllocineVenueProvider
from pcapi.core.providers.models import AllocineVenueProviderPriceRule
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
        model = AllocineVenueProvider

    venue = factory.SubFactory(VenueFactory)
    provider = factory.SubFactory(ProviderFactory)
    venueIdAtOfferProvider = factory.SelfAttribute("venue.siret")
    internalId = factory.Sequence("P{}".format)
    isDuo = True
    quantity = 1000


class AllocineVenueProviderPriceRuleFactory(BaseFactory):
    class Meta:
        model = AllocineVenueProviderPriceRule

    allocineVenueProvider = factory.SubFactory(AllocineVenueProviderFactory)
    priceRule = "default"
    price = 5.5


class VirtualVenueTypeFactory(BaseFactory):
    class Meta:
        model = VenueType

    label = "Offre numérique"


class VenueTypeFactory(BaseFactory):
    class Meta:
        model = VenueType

    label = "Librairie"


class VenueLabelFactory(BaseFactory):
    class Meta:
        model = VenueLabel

    label = "Cinéma d'art et d'essai"
