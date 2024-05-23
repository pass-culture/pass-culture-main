import datetime
import decimal
import random
import typing
import uuid

import factory
from factory.faker import faker

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.factories import BaseFactory
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.models as offers_models
from pcapi.core.providers.constants import TITELIVE_MUSIC_GENRES_BY_GTL_ID
from pcapi.core.providers.titelive_gtl import GTLS
import pcapi.core.users.factories as users_factories
from pcapi.domain import music_types
from pcapi.domain import show_types
from pcapi.models.offer_mixin import OfferValidationType

from . import models


class ProductFactory(BaseFactory):
    class Meta:
        model = models.Product

    subcategoryId = subcategories.SUPPORT_PHYSIQUE_FILM.id
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

        if "extraData" not in kwargs:
            subcategory_id = kwargs.get("subcategoryId")
            assert isinstance(
                subcategory_id, str
            )  # if the subcategoryId was not given in the factory, it will get the default subcategoryId
            kwargs["extraData"] = build_extra_data_from_subcategory(
                subcategory_id, kwargs.pop("set_all_fields", False), True
            )

        return super()._create(model_class, *args, **kwargs)


class ProductMediationFactory(BaseFactory):
    class Meta:
        model = models.ProductMediation

    product = factory.SubFactory(ProductFactory)
    url = factory.Sequence("http://example.com/product/{}".format)
    imageType = offers_models.TiteliveImageType.RECTO


class EventProductFactory(ProductFactory):
    subcategoryId = subcategories.SEANCE_CINE.id


class ThingProductFactory(ProductFactory):
    subcategoryId = subcategories.SUPPORT_PHYSIQUE_FILM.id


def build_extra_data_from_subcategory(
    subcategory_id: str, set_all_fields: bool, build_for_product: bool = False
) -> offers_models.OfferExtraData:
    fake = faker.Faker(locale="fr_FR")
    subcategory = subcategories.ALL_SUBCATEGORIES_DICT.get(subcategory_id)
    if not subcategory:
        raise ValueError(f"Unknown subcategory {subcategory_id}")
    extradata: offers_models.OfferExtraData = {}
    name_fields = [
        subcategories.ExtraDataFieldEnum.AUTHOR.value,
        subcategories.ExtraDataFieldEnum.PERFORMER.value,
        subcategories.ExtraDataFieldEnum.SPEAKER.value,
        subcategories.ExtraDataFieldEnum.STAGE_DIRECTOR.value,
    ]
    conditional_fields = (
        sorted(  # we sort to ensure MUSIC_SUB_TYPE and SHOW_SUB_TYPE is always after MUSIC_TYPE and SHOW_TYPE
            subcategory.conditional_fields,
            key=lambda field: (
                1
                if field
                in [
                    subcategories.ExtraDataFieldEnum.MUSIC_SUB_TYPE.value,
                    subcategories.ExtraDataFieldEnum.SHOW_SUB_TYPE.value,
                ]
                else 0
            ),
        )
    )
    for field in conditional_fields:
        if not set_all_fields and not subcategory.conditional_fields[field].is_required_in_internal_form:
            continue
        match field:
            case item if item in name_fields:
                extradata[field] = fake.name()  # type: ignore [literal-required]
            case subcategories.ExtraDataFieldEnum.EAN.value:
                extradata[field] = fake.ean13()
            case subcategories.ExtraDataFieldEnum.GTL_ID.value:
                if subcategory_id == subcategories.LIVRE_PAPIER.id:
                    if build_for_product:
                        extradata[field] = random.choice(list(GTLS.keys()))
                else:
                    extradata[field] = random.choice(list(TITELIVE_MUSIC_GENRES_BY_GTL_ID.keys()))
            case subcategories.ExtraDataFieldEnum.VISA.value:
                extradata[field] = fake.ean()
            case subcategories.ExtraDataFieldEnum.MUSIC_TYPE.value:
                extradata[field] = str(random.choice(music_types.music_types).code)
            case subcategories.ExtraDataFieldEnum.MUSIC_SUB_TYPE.value:
                music_type_code = extradata.get(subcategories.ExtraDataFieldEnum.MUSIC_TYPE.value)
                assert music_type_code
                music_type = music_types.MUSIC_TYPES_BY_CODE.get(int(music_type_code))
                assert music_type
                extradata[field] = str(random.choice(music_type.children).code)
            case subcategories.ExtraDataFieldEnum.SHOW_TYPE.value:
                extradata[field] = str(random.choice(show_types.show_types).code)
            case subcategories.ExtraDataFieldEnum.SHOW_SUB_TYPE.value:
                show_type_code = extradata.get(subcategories.ExtraDataFieldEnum.SHOW_TYPE.value)
                assert show_type_code
                show_type = show_types.SHOW_TYPES_BY_CODE.get(int(show_type_code))
                assert show_type
                extradata[field] = str(random.choice(show_type.children).code)

    return offers_models.OfferExtraData(**extradata)


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
        if "extraData" not in kwargs:
            product = kwargs.get("product")
            if product:
                kwargs["extraData"] = product.extraData
            subcategory_id = kwargs.get("subcategoryId")
            assert isinstance(
                subcategory_id, str
            )  # if the subcategoryId was not given in the factory, it will get the default subcategoryId
            kwargs["extraData"] = build_extra_data_from_subcategory(subcategory_id, kwargs.pop("set_all_fields", False))
        if "offererAddress" not in kwargs and "offererAddressId" not in kwargs:
            venue = kwargs.get("venue")
            if venue:
                kwargs["offererAddress"] = venue.offererAddress

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


class OfferValidationSubRuleFactory(BaseFactory):
    class Meta:
        model = models.OfferValidationSubRule

    validationRule = factory.SubFactory(OfferValidationRuleFactory)
    model = models.OfferValidationModel.OFFER
    attribute = models.OfferValidationAttribute.NAME
    operator = models.OfferValidationRuleOperator.CONTAINS
    comparated = {"comparated": ["suspicious", "verboten"]}


class OfferPriceLimitationRuleFactory(BaseFactory):
    class Meta:
        model = models.OfferPriceLimitationRule

    subcategoryId = subcategories.ACHAT_INSTRUMENT.id
    rate = decimal.Decimal(0.3)
