import datetime
import decimal
import typing
import uuid

import factory

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.factories import BaseFactory
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.models as offers_models
import pcapi.core.users.factories as users_factories
from pcapi.models.offer_mixin import OfferValidationType

from . import models


class ProductFactory(BaseFactory):
    class Meta:
        model = models.Product

    subcategoryId = subcategories.CARTE_MUSEE.id
    name = factory.Sequence("Product {}".format)
    description = factory.Sequence("A passionate description of product {}".format)

    @classmethod
    def _create(
        cls,
        model_class: type[models.Product],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.Product:
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

    venue = factory.SubFactory(offerers_factories.VenueFactory)
    subcategoryId = subcategories.SUPPORT_PHYSIQUE_FILM.id
    name = factory.Sequence("Offer {}".format)
    description = factory.Sequence("A passionate description of offer {}".format)
    audioDisabilityCompliant = False
    mentalDisabilityCompliant = False
    motorDisabilityCompliant = False
    visualDisabilityCompliant = False
    lastValidationType = OfferValidationType.AUTO
    extraData = None

    @classmethod
    def _create(
        cls,
        model_class: type[models.Offer],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.Offer:
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
    subcategoryId = subcategories.SEANCE_CINE.id


class ThingOfferFactory(OfferFactory):
    subcategoryId = subcategories.CARTE_CINE_ILLIMITE.id


class DigitalOfferFactory(OfferFactory):
    subcategoryId = subcategories.VOD.id
    url = factory.Sequence("http://example.com/offer/{}".format)
    venue = factory.SubFactory(offerers_factories.VirtualVenueFactory)


class PriceCategoryLabelFactory(BaseFactory):
    class Meta:
        model = models.PriceCategoryLabel

    label = "Tarif unique"
    venue = factory.SubFactory(offerers_factories.VenueFactory)

    @classmethod
    def _create(
        cls,
        model_class: type[models.PriceCategoryLabel],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.PriceCategoryLabel:
        label = offers_models.PriceCategoryLabel.query.filter_by(
            label=kwargs.get("label"), venue=kwargs.get("venue")
        ).one_or_none()
        if label:
            return label
        return super()._create(model_class, *args, **kwargs)


class PriceCategoryFactory(BaseFactory):
    class Meta:
        model = models.PriceCategory

    price = decimal.Decimal("10.1")
    offer = factory.SubFactory(EventOfferFactory)
    priceCategoryLabel = factory.SubFactory(PriceCategoryLabelFactory, venue=factory.SelfAttribute("..offer.venue"))


class StockFactory(BaseFactory):
    class Meta:
        model = models.Stock

    offer = factory.SubFactory(OfferFactory)
    price = decimal.Decimal("10.1")
    quantity = 1000

    beginningDatetime = factory.Maybe(
        "offer.isEvent",
        factory.LazyFunction(
            lambda: datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(days=30)
        ),
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
    beginningDatetime = factory.LazyFunction(
        lambda: datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(days=30)
    )
    bookingLimitDatetime = factory.LazyAttribute(lambda stock: stock.beginningDatetime - datetime.timedelta(minutes=60))
    priceCategory = factory.SubFactory(
        PriceCategoryFactory,
        offer=factory.SelfAttribute("..offer"),
        price=factory.SelfAttribute("..price"),
        priceCategoryLabel__venue=factory.SelfAttribute("..offer.venue"),
    )


class CinemaStockProviderFactory(EventStockFactory):
    beginningDatetime = factory.LazyFunction(
        lambda: datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(days=30)
    )
    bookingLimitDatetime = factory.LazyAttribute(lambda stock: stock.beginningDatetime - datetime.timedelta(minutes=60))


class StockWithActivationCodesFactory(StockFactory):
    offer = factory.SubFactory(DigitalOfferFactory)

    @factory.post_generation
    def activationCodes(
        self,
        create: bool,
        extracted: list[str],
        **kwargs: typing.Any,
    ) -> None:
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
    thumbCount = 1


class OfferReportFactory(BaseFactory):
    class Meta:
        model = models.OfferReport

    user = factory.SubFactory(users_factories.UserFactory)
    offer = factory.SubFactory(OfferFactory)
    reason = "INAPPROPRIATE"


class OfferValidationRuleFactory(BaseFactory):
    class Meta:
        model = models.OfferValidationRule

    name = factory.Sequence("Offer validation rule {}".format)
    dateModified = datetime.datetime.utcnow()
    latestAuthor = factory.SubFactory(users_factories.UserFactory)


class OfferValidationSubRuleFactory(BaseFactory):
    class Meta:
        model = models.OfferValidationSubRule

    validationRule = factory.SubFactory(OfferValidationRuleFactory)
    model = models.OfferValidationModel.OFFER
    attribute = models.OfferValidationAttribute.NAME
    operator = models.OfferValidationRuleOperator.CONTAINS
    comparated = {"comparated": ["suspicious", "verboten"]}
