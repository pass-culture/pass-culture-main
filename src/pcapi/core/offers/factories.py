import datetime
import uuid

import factory

from pcapi import models
from pcapi.core.categories import subcategories
from pcapi.core.categories.subcategories import ALL_SUBCATEGORIES
from pcapi.core.categories.subcategories import ALL_SUBCATEGORIES_DICT
import pcapi.core.offerers.models as offerers_models
from pcapi.core.offers.models import OfferReport
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.testing import BaseFactory
import pcapi.core.users.factories as users_factories
from pcapi.models import db
from pcapi.models import offer_type


ALL_TYPES = {
    name for name in offer_type.ALL_OFFER_TYPES_DICT if name not in ("ThingType.ACTIVATION", "EventType.ACTIVATION")
}  # {"EventType.Musique", "ThingType.Musique"...}


class OffererFactory(BaseFactory):
    class Meta:
        model = offerers_models.Offerer

    name = factory.Sequence("Le Petit Rintintin Management {}".format)
    address = "1 boulevard Poissonnière"
    postalCode = "75000"
    city = "Paris"
    siren = factory.Sequence(lambda n: f"{n:09}")


class UserOffererFactory(BaseFactory):
    class Meta:
        model = models.UserOfferer

    user = factory.SubFactory(users_factories.ProFactory)
    offerer = factory.SubFactory(OffererFactory)


class VenueFactory(BaseFactory):
    class Meta:
        model = models.Venue

    name = factory.Sequence("Le Petit Rintintin {}".format)
    departementCode = factory.LazyAttribute(lambda o: None if o.isVirtual else "75")
    latitude = 48.87004
    longitude = 2.37850
    managingOfferer = factory.SubFactory(OffererFactory)
    address = factory.LazyAttribute(lambda o: None if o.isVirtual else "1 boulevard Poissonnière")
    postalCode = factory.LazyAttribute(lambda o: None if o.isVirtual else "75000")
    city = factory.LazyAttribute(lambda o: None if o.isVirtual else "Paris")
    publicName = factory.SelfAttribute("name")
    siret = factory.LazyAttributeSequence(lambda o, n: f"{o.managingOfferer.siren}{n:05}")
    isVirtual = False
    venueTypeCode = offerers_models.VenueTypeCode.OTHER.value


class VirtualVenueFactory(VenueFactory):
    isVirtual = True
    address = None
    departementCode = None
    postalCode = None
    city = None
    siret = None


class ProductFactory(BaseFactory):
    class Meta:
        model = models.Product

    subcategoryId = factory.Iterator(ALL_SUBCATEGORIES, getter=lambda s: s.id)
    type = "MATCHED_FROM_SUBCATEGORY_ID_IN_POST_GENERATION"  # FIXME: fseguin(2021-07-22): deprecated
    name = factory.Sequence("Product {}".format)
    description = factory.Sequence("A passionate description of product {}".format)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Graciously provide the required idAtProviders if lastProvider is given.
        if kwargs.get("lastProvider") and not kwargs.get("idAtProviders"):
            kwargs["idAtProviders"] = uuid.uuid4()
        return super()._create(model_class, *args, **kwargs)

    # FIXME: fseguin(2021-07-22): deprecated
    @factory.post_generation
    def match_type(self, create, extracted, **kwargs):
        self.type = getattr(ALL_SUBCATEGORIES_DICT.get(self.subcategoryId, ""), "matching_type", None)
        db.session.add(self)
        db.session.commit()


class EventProductFactory(ProductFactory):
    subcategoryId = subcategories.SEANCE_CINE.id


class ThingProductFactory(ProductFactory):
    subcategoryId = subcategories.SUPPORT_PHYSIQUE_FILM.id


class DigitalProductFactory(ThingProductFactory):
    name = factory.Sequence("Digital product {}".format)
    url = factory.Sequence("http://example.com/product/{}".format)
    isNational = True


class OfferFactory(BaseFactory):
    class Meta:
        model = models.Offer

    product = factory.SubFactory(ThingProductFactory)
    venue = factory.SubFactory(VenueFactory)
    type = "MATCHED_FROM_SUBCATEGORY_ID_IN_POST_GENERATION"  # FIXME: fseguin(2021-07-22): deprecated
    subcategoryId = factory.SelfAttribute("product.subcategoryId")
    name = factory.SelfAttribute("product.name")
    description = factory.SelfAttribute("product.description")
    url = factory.SelfAttribute("product.url")
    audioDisabilityCompliant = False
    mentalDisabilityCompliant = False
    motorDisabilityCompliant = False
    visualDisabilityCompliant = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Graciously provide the required idAtProviders if lastProvider is given.
        if kwargs.get("lastProvider") and not kwargs.get("idAtProviders"):
            kwargs["idAtProviders"] = uuid.uuid4()

        if kwargs.get("isActive") is None:
            kwargs["isActive"] = (
                False  # pylint:disable=simplifiable-if-expression
                if (
                    kwargs.get("validation") == OfferValidationStatus.REJECTED
                    or kwargs.get("validation") == OfferValidationStatus.PENDING
                )
                else True
            )

        return super()._create(model_class, *args, **kwargs)

    # FIXME: fseguin(2021-07-22): deprecated
    @factory.post_generation
    def match_type(self, create, extracted, **kwargs):
        self.type = getattr(ALL_SUBCATEGORIES_DICT.get(self.subcategoryId, ""), "matching_type", None)
        db.session.add(self)
        db.session.commit()


class EventOfferFactory(OfferFactory):
    product = factory.SubFactory(EventProductFactory)


class ThingOfferFactory(OfferFactory):
    product = factory.SubFactory(ThingProductFactory)


class DigitalOfferFactory(OfferFactory):
    product = factory.SubFactory(DigitalProductFactory)


class StockFactory(BaseFactory):
    class Meta:
        model = models.Stock

    offer = factory.SubFactory(OfferFactory)
    price = 10
    quantity = 1000

    beginningDatetime = factory.Maybe(
        "offer.isEvent",
        factory.LazyFunction(lambda: datetime.datetime.now() + datetime.timedelta(days=5)),
        None,
    )
    bookingLimitDatetime = factory.Maybe(
        "stock.beginningDatetime and offer.isEvent",
        factory.LazyAttribute(lambda stock: stock.beginningDatetime - datetime.timedelta(minutes=60)),
        None,
    )


class ThingStockFactory(StockFactory):
    offer = factory.SubFactory(ThingOfferFactory)


class EventStockFactory(StockFactory):
    offer = factory.SubFactory(EventOfferFactory)
    beginningDatetime = factory.LazyFunction(lambda: datetime.datetime.now() + datetime.timedelta(days=5))
    bookingLimitDatetime = factory.LazyAttribute(lambda stock: stock.beginningDatetime - datetime.timedelta(minutes=60))


class StockWithActivationCodesFactory(StockFactory):
    offer = factory.SubFactory(DigitalOfferFactory)

    @factory.post_generation
    def activationCodes(self, create, extracted, **kwargs):
        if extracted:
            for code in extracted:
                ActivationCodeFactory(stockId=self.id, code=code)
        else:
            available_activation_counts = 5
            self.quantity = available_activation_counts
            ActivationCodeFactory.create_batch(size=available_activation_counts, stockId=self.id, **kwargs)


class ActivationCodeFactory(BaseFactory):
    class Meta:
        model = models.ActivationCode

    code = factory.Faker("lexify", text="code-?????????")


class MediationFactory(BaseFactory):
    class Meta:
        model = models.Mediation

    offer = factory.SubFactory(OfferFactory)
    isActive = True


class CriterionFactory(BaseFactory):
    class Meta:
        model = models.Criterion

    name = factory.Sequence("Criterion {}".format)


class OfferCriterionFactory(BaseFactory):
    class Meta:
        model = models.OfferCriterion

    offer = factory.SubFactory(OfferFactory)
    criterion = factory.SubFactory(CriterionFactory)


class BankInformationFactory(BaseFactory):
    class Meta:
        model = models.BankInformation

    bic = factory.Sequence(lambda n: f"TESTFR2{n:04}")
    iban = factory.LazyAttributeSequence(lambda o, n: f"FR{n:016}")
    applicationId = factory.Sequence(int)
    status = "ACCEPTED"


class OfferReportFactory(BaseFactory):
    class Meta:
        model = OfferReport

    user = factory.SubFactory(users_factories.UserFactory)
    offer = factory.SubFactory(OfferFactory)
    reason = "INAPPROPRIATE"
