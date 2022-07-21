import base64
import random
import secrets

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


class AllocineTheaterFactory(BaseFactory):
    class Meta:
        model = models.AllocineTheater

    siret = "12345678912345"

    internalId = factory.LazyFunction(lambda: random.choice(["B", "C", "P", "W"]) + str(random.randrange(1000, 9999)))

    theaterId = factory.LazyAttribute(
        lambda o: (base64.urlsafe_b64encode(bytearray(f"Theater:{o.internalId}", "utf-8"))).decode("utf-8")
    )


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


class CinemaProviderPivotFactory(BaseFactory):
    class Meta:
        model = models.CinemaProviderPivot

    venue = factory.SubFactory(VenueFactory)
    provider = factory.SubFactory(ProviderFactory)
    idAtProvider = factory.Sequence("idProvider{}".format)


class CDSCinemaDetailsFactory(BaseFactory):
    class Meta:
        model = models.CDSCinemaDetails

    cinemaProviderPivot = factory.SubFactory(CinemaProviderPivotFactory)
    cinemaApiToken = factory.LazyFunction(secrets.token_urlsafe)
    accountId = factory.Sequence("account{}".format)


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
