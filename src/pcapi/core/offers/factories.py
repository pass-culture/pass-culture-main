import datetime
import uuid

import factory

from pcapi import models
from pcapi.core.testing import BaseFactory
import pcapi.core.users.factories as users_factories
from pcapi.models import offer_type


ALL_TYPES = {t.name for t in list(offer_type.EventType) + list(offer_type.ThingType)}


class OffererFactory(BaseFactory):
    class Meta:
        model = models.Offerer

    name = factory.Sequence("Le Petit Rintintin Management {}".format)
    postalCode = "75000"
    city = "Paris"

    @factory.iterator
    def siren():
        for i in range(10 ** 9):
            yield f"{i:09}"


class UserOffererFactory(BaseFactory):
    class Meta:
        model = models.UserOfferer

    user = factory.SubFactory(users_factories.UserFactory)
    offerer = factory.SubFactory(OffererFactory)
    rights = models.RightsType.editor


class ApiKeyFactory(BaseFactory):
    class Meta:
        model = models.ApiKey

    offerer = factory.SubFactory(OffererFactory)
    value = factory.Sequence("API KEY {}".format)


class VenueFactory(BaseFactory):
    class Meta:
        model = models.VenueSQLEntity

    name = factory.Sequence("Le Petit Rintintin {}".format)
    departementCode = "75"
    latitude = 48.87004
    longitude = 2.37850
    managingOfferer = factory.SubFactory(OffererFactory)
    postalCode = "75000"
    city = "Paris"
    publicName = factory.SelfAttribute("name")

    # FIXME: should depend on self.offerer.siret
    @factory.iterator
    def siret():
        for i in range(10 ** 14):
            yield f"{i:014}"


class VirtualVenueFactory(VenueFactory):
    isVirtual = True
    departementCode = None
    postalCode = None
    city = None
    siret = None


class ProductFactory(BaseFactory):
    class Meta:
        model = models.Product

    type = factory.Iterator(ALL_TYPES)
    name = factory.Sequence("Product {}".format)
    description = factory.Sequence("A passionate description of product {}".format)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Graciously provide the required idAtProviders if lastProvider is given.
        if kwargs.get("lastProvider") and not kwargs.get("idAtProviders"):
            kwargs["idAtProviders"] = uuid.uuid4()
        return super()._create(model_class, *args, **kwargs)


class EventProductFactory(ProductFactory):
    type = str(offer_type.EventType.CINEMA)


class ThingProductFactory(ProductFactory):
    type = str(offer_type.ThingType.AUDIOVISUEL)


class OfferFactory(BaseFactory):
    class Meta:
        model = models.Offer

    product = factory.SubFactory(ProductFactory)
    venue = factory.SubFactory(VenueFactory)
    type = factory.SelfAttribute("product.type")
    name = factory.SelfAttribute("product.name")
    description = factory.SelfAttribute("product.description")
    url = factory.SelfAttribute("product.url")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Graciously provide the required idAtProviders if lastProvider is given.
        if kwargs.get("lastProvider") and not kwargs.get("idAtProviders"):
            kwargs["idAtProviders"] = uuid.uuid4()
        return super()._create(model_class, *args, **kwargs)


class EventOfferFactory(OfferFactory):
    product = factory.SubFactory(EventProductFactory)


class ThingOfferFactory(OfferFactory):
    product = factory.SubFactory(ThingProductFactory)


class StockFactory(BaseFactory):
    class Meta:
        model = models.Stock

    offer = factory.SubFactory(OfferFactory)
    price = 10
    quantity = 1000


class EventStockFactory(StockFactory):
    offer = factory.SubFactory(EventOfferFactory)
    beginningDatetime = factory.LazyFunction(lambda: datetime.datetime.now() + datetime.timedelta(days=5))
    bookingLimitDatetime = factory.LazyAttribute(lambda stock: stock.beginningDatetime - datetime.timedelta(minutes=60))
