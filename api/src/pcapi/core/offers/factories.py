import datetime
import uuid

import factory
import schwifty

from pcapi.core.categories import subcategories
from pcapi.core.categories.subcategories import ALL_SUBCATEGORIES
import pcapi.core.criteria.factories as criteria_factories
import pcapi.core.offerers.models as offerers_models
from pcapi.core.testing import BaseFactory
import pcapi.core.users.factories as users_factories
from pcapi.models.bank_information import BankInformation
from pcapi.models.bank_information import BankInformationStatus
from pcapi.models.offer_criterion import OfferCriterion
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.models.product import Product

from . import models


class OffererFactory(BaseFactory):
    class Meta:
        model = offerers_models.Offerer

    name = factory.Sequence("Le Petit Rintintin Management {}".format)
    address = "1 boulevard Poissonnière"
    postalCode = "75000"
    city = "Paris"
    siren = factory.Sequence(lambda n: f"{n:09}")
    isActive = True


class VenueFactory(BaseFactory):
    class Meta:
        model = offerers_models.Venue

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
    venueTypeCode = offerers_models.VenueTypeCode.OTHER  # type: ignore[attr-defined]
    venueType = factory.SubFactory(
        "pcapi.core.offerers.factories.VenueTypeFactory", label=factory.SelfAttribute("..venueTypeCode.value")
    )
    description = factory.Faker("text", max_nb_chars=64)
    audioDisabilityCompliant = False
    mentalDisabilityCompliant = False
    motorDisabilityCompliant = False
    visualDisabilityCompliant = False
    businessUnit = factory.SubFactory(
        "pcapi.core.finance.factories.BusinessUnitFactory",
        siret=factory.LazyAttribute(lambda bu: bu.factory_parent.siret),
    )
    contact = factory.RelatedFactory("pcapi.core.offerers.factories.VenueContactFactory", factory_related_name="venue")
    bookingEmail = factory.Sequence("venue{}@example.net".format)


class VirtualVenueFactory(VenueFactory):
    isVirtual = True
    address = None
    departementCode = None
    postalCode = None
    city = None
    latitude = None  # type: ignore [assignment]
    longitude = None  # type: ignore [assignment]
    siret = None
    audioDisabilityCompliant = False
    mentalDisabilityCompliant = False
    motorDisabilityCompliant = False
    visualDisabilityCompliant = False
    venueTypeCode = offerers_models.VenueTypeCode.DIGITAL  # type: ignore[attr-defined]


class ProductFactory(BaseFactory):
    class Meta:
        model = Product

    subcategoryId = factory.Iterator(ALL_SUBCATEGORIES, getter=lambda s: s.id)
    name = factory.Sequence("Product {}".format)
    description = factory.Sequence("A passionate description of product {}".format)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):  # type: ignore [no-untyped-def]
        # Graciously provide the required idAtProviders if lastProvider is given.
        if kwargs.get("lastProvider") and not kwargs.get("idAtProviders"):
            kwargs["idAtProviders"] = uuid.uuid4()
        return super()._create(model_class, *args, **kwargs)


class EventProductFactory(ProductFactory):
    subcategoryId = subcategories.SEANCE_CINE.id


class ThingProductFactory(ProductFactory):
    subcategoryId = subcategories.SUPPORT_PHYSIQUE_FILM.id


class DigitalProductFactory(ThingProductFactory):
    subcategoryId = subcategories.VOD.id
    name = factory.Sequence("Digital product {}".format)
    url = factory.Sequence("http://example.com/product/{}".format)
    isNational = True


class OfferFactory(BaseFactory):
    class Meta:
        model = models.Offer

    product = factory.SubFactory(ThingProductFactory)
    venue = factory.SubFactory(VenueFactory)
    subcategoryId = factory.SelfAttribute("product.subcategoryId")
    name = factory.SelfAttribute("product.name")
    description = factory.SelfAttribute("product.description")
    url = factory.SelfAttribute("product.url")
    audioDisabilityCompliant = False
    mentalDisabilityCompliant = False
    motorDisabilityCompliant = False
    visualDisabilityCompliant = False
    isEducational = False
    lastValidationType = OfferValidationType.AUTO

    @classmethod
    def _create(cls, model_class, *args, **kwargs):  # type: ignore [no-untyped-def]
        # Graciously provide the required idAtProvider if lastProvider is given.
        if kwargs.get("lastProvider") and not kwargs.get("idAtProvider"):
            kwargs["idAtProvider"] = uuid.uuid4()

        if kwargs.get("isActive") is None:
            kwargs["isActive"] = kwargs.get("validation") not in (
                models.OfferValidationStatus.REJECTED,
                models.OfferValidationStatus.PENDING,
            )

        return super()._create(model_class, *args, **kwargs)


class EventOfferFactory(OfferFactory):
    product = factory.SubFactory(EventProductFactory)


class EducationalEventOfferFactory(OfferFactory):
    product = factory.SubFactory(EventProductFactory)
    isEducational = True
    extraData = {}  # type: ignore [var-annotated]


class EducationalEventShadowOfferFactory(EducationalEventOfferFactory):
    extraData = {
        "students": [
            "CAP - 1re ann\u00e9e",
            "CAP - 2e ann\u00e9e",
            "Lyc\u00e9e - Seconde",
            "Lyc\u00e9e - Premi\u00e8re",
        ],
        "offerVenue": {
            "addressType": "other",
            "otherAddress": "1 rue des polissons, Paris 75017",
            "venueId": "",
        },
        "contactEmail": "miss.rond@point.com",
        "contactPhone": "01010100101",
        "isShowcase": True,
    }


class EducationalThingOfferFactory(OfferFactory):
    product = factory.SubFactory(ThingProductFactory)
    isEducational = True


class ThingOfferFactory(OfferFactory):
    product = factory.SubFactory(ThingProductFactory)


class DigitalOfferFactory(OfferFactory):
    product = factory.SubFactory(DigitalProductFactory)
    venue = factory.SubFactory(VirtualVenueFactory)


class StockFactory(BaseFactory):
    class Meta:
        model = models.Stock

    offer = factory.SubFactory(OfferFactory)
    price = 10
    quantity = 1000

    beginningDatetime = factory.Maybe(
        "offer.isEvent",
        factory.LazyFunction(lambda: datetime.datetime.utcnow() + datetime.timedelta(days=5)),
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
    beginningDatetime = factory.LazyFunction(lambda: datetime.datetime.utcnow() + datetime.timedelta(days=5))
    bookingLimitDatetime = factory.LazyAttribute(lambda stock: stock.beginningDatetime - datetime.timedelta(minutes=60))


class EducationalThingStockFactory(StockFactory):
    offer = factory.SubFactory(EducationalThingOfferFactory)


class EducationalEventStockFactory(StockFactory):
    offer = factory.SubFactory(EducationalEventOfferFactory)
    beginningDatetime = factory.LazyFunction(lambda: datetime.datetime.utcnow() + datetime.timedelta(days=5))
    bookingLimitDatetime = factory.LazyAttribute(lambda stock: stock.beginningDatetime - datetime.timedelta(minutes=60))
    numberOfTickets = 30
    educationalPriceDetail = (
        "Le prix inclus l'accès à la séance et un atelier une fois la séance terminée. 1000 caractères max."
    )


class EducationalEventShadowStockFactory(StockFactory):
    offer = factory.SubFactory(EducationalEventShadowOfferFactory)
    beginningDatetime = datetime.datetime(2030, 1, 1)
    bookingLimitDatetime = datetime.datetime(2030, 1, 1)
    numberOfTickets = 1
    educationalPriceDetail = (
        "Le prix inclus l'accès à la séance et un atelier une fois la séance terminée. 1000 caractères max."
    )


class StockWithActivationCodesFactory(StockFactory):
    offer = factory.SubFactory(DigitalOfferFactory)

    @factory.post_generation
    def activationCodes(self, create, extracted, **kwargs) -> None:  # type: ignore [no-untyped-def]
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


class OfferCriterionFactory(BaseFactory):
    class Meta:
        model = OfferCriterion

    offer = factory.SubFactory(OfferFactory)
    criterion = factory.SubFactory(criteria_factories.CriterionFactory)


class VenueCriterionFactory(BaseFactory):
    class Meta:
        model = offerers_models.VenueCriterion

    venue = factory.SubFactory(VenueFactory)
    criterion = factory.SubFactory(criteria_factories.CriterionFactory)


class BankInformationFactory(BaseFactory):
    class Meta:
        model = BankInformation

    bic = "BDFEFRPP"
    iban = factory.LazyAttributeSequence(
        lambda o, n: schwifty.IBAN.generate("FR", bank_code="10010", account_code=f"{n:010}").compact
    )
    status = BankInformationStatus.ACCEPTED


class OfferReportFactory(BaseFactory):
    class Meta:
        model = models.OfferReport

    user = factory.SubFactory(users_factories.UserFactory)
    offer = factory.SubFactory(OfferFactory)
    reason = "INAPPROPRIATE"


class OfferValidationConfigFactory(BaseFactory):
    class Meta:
        model = models.OfferValidationConfig

    user = factory.SubFactory(users_factories.UserFactory)
    specs = factory.LazyAttribute(lambda config: {"minimum_score": 0.1, "rules": []})


class OffererTagFactory(BaseFactory):
    class Meta:
        model = offerers_models.OffererTag

    name = factory.Sequence("OffererTag_{}".format)


class OffererTagMappingFactory(BaseFactory):
    class Meta:
        model = offerers_models.OffererTagMapping

    offerer = factory.SubFactory(OffererFactory)
    tag = factory.SubFactory(OffererTagFactory)
