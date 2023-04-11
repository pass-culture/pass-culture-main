import base64
import datetime
import decimal
import random
import secrets

import factory

from pcapi.core.offerers.factories import VenueFactory
import pcapi.core.providers.repository as providers_repository
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

    name = factory.Sequence("API Provider {}".format)
    apiUrl = factory.Sequence("https://{}.example.org/stocks".format)
    enabledForPro = True
    isActive = True


class VenueProviderFactory(BaseFactory):
    class Meta:
        model = models.VenueProvider

    venue = factory.SubFactory(VenueFactory)
    provider = factory.SubFactory(APIProviderFactory)
    isActive = True

    venueIdAtOfferProvider = factory.SelfAttribute("venue.siret")


class CinemaProviderPivotFactory(BaseFactory):
    class Meta:
        model = models.CinemaProviderPivot

    venue = factory.SubFactory(VenueFactory)
    provider = factory.SubFactory(ProviderFactory)
    idAtProvider = factory.Sequence("idProvider{}".format)


class BoostCinemaProviderPivotFactory(CinemaProviderPivotFactory):
    class Meta:
        sqlalchemy_get_or_create = ["provider"]

    provider = factory.LazyFunction(lambda: providers_repository.get_provider_by_local_class("BoostStocks"))


class CDSCinemaProviderPivotFactory(CinemaProviderPivotFactory):
    class Meta:
        sqlalchemy_get_or_create = ["provider"]

    provider = factory.LazyFunction(lambda: providers_repository.get_provider_by_local_class("CDSStocks"))


class CGRCinemaProviderPivotFactory(CinemaProviderPivotFactory):
    class Meta:
        sqlalchemy_get_or_create = ["provider"]

    provider = factory.LazyFunction(lambda: providers_repository.get_provider_by_local_class("CGRStocks"))


class CDSCinemaDetailsFactory(BaseFactory):
    class Meta:
        model = models.CDSCinemaDetails

    cinemaProviderPivot = factory.SubFactory(CDSCinemaProviderPivotFactory)
    cinemaApiToken = factory.LazyFunction(secrets.token_urlsafe)
    accountId = factory.Sequence("account{}".format)


class BoostCinemaDetailsFactory(BaseFactory):
    class Meta:
        model = models.BoostCinemaDetails

    cinemaProviderPivot = factory.SubFactory(BoostCinemaProviderPivotFactory)
    cinemaUrl = factory.Sequence("https://boost-cinema-{}.example.com/".format)
    username = "pass_culture"
    password = "a great password"
    token = factory.LazyFunction(secrets.token_urlsafe)
    tokenExpirationDate = factory.LazyAttribute(lambda _: datetime.datetime.utcnow() + datetime.timedelta(hours=24))


class CGRCinemaDetailsFactory(BaseFactory):
    class Meta:
        model = models.CGRCinemaDetails

    cinemaProviderPivot = factory.SubFactory(CGRCinemaProviderPivotFactory)
    cinemaUrl = factory.Sequence("https://cgr-cinema-{}.example.com/".format)
    numCinema = factory.Sequence(int)
    password = "a great password"


class AllocineProviderFactory(BaseFactory):
    class Meta:
        model = models.Provider
        sqlalchemy_get_or_create = ["localClass"]

    name = factory.Sequence("Allociné Provider {}".format)
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
    price = decimal.Decimal("5.7")
