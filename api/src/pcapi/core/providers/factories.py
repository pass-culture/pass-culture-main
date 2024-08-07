import base64
import datetime
import decimal
import random
import secrets

import factory

from pcapi.core.factories import BaseFactory
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
import pcapi.core.providers.repository as providers_repository
from pcapi.utils.crypto import encrypt

from . import models


class AllocinePivotFactory(BaseFactory):
    class Meta:
        model = models.AllocinePivot

    venue = factory.SubFactory(offerers_factories.VenueFactory)
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

    name = factory.Sequence("Provider {}".format)
    localClass = factory.Sequence("{}Stocks".format)
    hmacKey = "secret"
    apiUrl = None
    enabledForPro = True
    isActive = True


class APIProviderFactory(BaseFactory):
    # This factory creates legacy providers.
    # The API they uses will be dropped, do not use this factory unless you specifically want to.
    class Meta:
        model = models.Provider

    name = factory.Sequence("API Provider {}".format)
    apiUrl = factory.Sequence("https://{}.example.org/stocks".format)
    enabledForPro = True
    isActive = True


class PublicApiProviderFactory(BaseFactory):
    class Meta:
        model = models.Provider
        sqlalchemy_get_or_create = ["name"]

    name = factory.Sequence("Public API Provider {}".format)
    enabledForPro = True
    isActive = True
    hmacKey = "secret"
    bookingExternalUrl = factory.Sequence("https://{}.example.org/booking".format)
    cancelExternalUrl = factory.Sequence("https://{}.example.org/booking".format)
    notificationExternalUrl = factory.Sequence("https://{}.example.org/booking".format)


class VenueProviderFactory(BaseFactory):
    class Meta:
        model = models.VenueProvider

    venue = factory.SubFactory(offerers_factories.VenueFactory)
    provider = factory.SubFactory(APIProviderFactory)
    isActive = True

    venueIdAtOfferProvider = factory.SelfAttribute("venue.siret")


class VenueProviderExternalUrlsFactory(BaseFactory):
    class Meta:
        model = models.VenueProviderExternalUrls

    bookingExternalUrl = factory.Sequence("https://{}.example.org/booking".format)
    cancelExternalUrl = factory.Sequence("https://{}.example.org/cancel".format)
    notificationExternalUrl = factory.Sequence("https://{}.example.org/notification".format)


class CinemaProviderPivotFactory(BaseFactory):
    class Meta:
        model = models.CinemaProviderPivot

    venue = factory.SubFactory(offerers_factories.VenueFactory)
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


class EMSCinemaProviderPivotFactory(CinemaProviderPivotFactory):
    class Meta:
        sqlalchemy_get_or_create = ["provider"]

    provider = factory.LazyFunction(lambda: providers_repository.get_provider_by_local_class("EMSStocks"))


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
    token = factory.LazyFunction(secrets.token_urlsafe)
    tokenExpirationDate = factory.LazyAttribute(lambda _: datetime.datetime.utcnow() + datetime.timedelta(hours=24))


class CGRCinemaDetailsFactory(BaseFactory):
    class Meta:
        model = models.CGRCinemaDetails

    cinemaProviderPivot = factory.SubFactory(CGRCinemaProviderPivotFactory)
    cinemaUrl = factory.Sequence("https://cgr-cinema-{}.example.com/".format)
    numCinema = factory.Sequence(int)
    password = factory.LazyAttribute(lambda _: encrypt("a great password"))


class EMSCinemaDetailsFactory(BaseFactory):
    class Meta:
        model = models.EMSCinemaDetails

    cinemaProviderPivot = factory.SubFactory(EMSCinemaProviderPivotFactory)
    lastVersion = 0


class AllocineProviderFactory(BaseFactory):
    class Meta:
        model = models.Provider
        sqlalchemy_get_or_create = ["localClass"]

    name = factory.Sequence("Allociné Provider {}".format)
    localClass = "AllocineStocks"
    enabledForPro = True
    isActive = True


class TiteLiveThingsProviderFactory(BaseFactory):
    class Meta:
        model = models.Provider
        sqlalchemy_get_or_create = ["localClass"]

    name = factory.Sequence("TiteLiveThings {}".format)
    localClass = "TiteLiveThings"
    enabledForPro = True
    isActive = True


class AllocineVenueProviderFactory(BaseFactory):
    class Meta:
        model = models.AllocineVenueProvider

    venue = factory.SubFactory(offerers_factories.VenueFactory)
    provider = factory.SubFactory(AllocineProviderFactory)
    venueIdAtOfferProvider = factory.SelfAttribute("venue.siret")
    internalId = factory.Sequence("P{}".format)
    isDuo = True
    quantity = 1000
    price = decimal.Decimal("5.7")


class OffererProviderFactory(BaseFactory):
    class Meta:
        model = offerers_models.OffererProvider

    offerer = factory.SubFactory(offerers_factories.OffererFactory)
    provider = factory.SubFactory(ProviderFactory)


class LocalProviderEventFactory(BaseFactory):
    class Meta:
        model = models.LocalProviderEvent

    provider = factory.SubFactory(ProviderFactory)
    type = models.LocalProviderEventType.SyncStart
    date = factory.LazyAttribute(lambda _: datetime.datetime.utcnow() - datetime.timedelta(days=30))
