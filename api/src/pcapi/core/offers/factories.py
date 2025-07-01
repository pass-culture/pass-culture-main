import datetime
import decimal
import random
import typing
import uuid

import factory
from factory.faker import faker

import pcapi.core.artist.models as artist_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.models as offers_models
import pcapi.core.users.factories as users_factories
from pcapi.core.categories import subcategories
from pcapi.core.categories.genres import music
from pcapi.core.categories.genres import show
from pcapi.core.factories import BaseFactory
from pcapi.core.offerers.schemas import VenueTypeCode
from pcapi.core.providers.constants import TITELIVE_MUSIC_GENRES_BY_GTL_ID
from pcapi.core.providers.titelive_gtl import GTLS
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationType

from . import models


fake = faker.Faker(locale="fr_FR")

EVENT_PRODUCT_SUBCATEGORIES_IDS = [subcategories.SEANCE_CINE.id]
THINGS_PRODUCT_SUBCATEGORIES_IDS = [
    subcategories.LIVRE_PAPIER.id,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
]
ALL_PRODUCT_SUBCATEGORIES_IDS = EVENT_PRODUCT_SUBCATEGORIES_IDS + THINGS_PRODUCT_SUBCATEGORIES_IDS
OPENING_HOURS = [("10:00", "13:00"), ("14:00", "19:30")]


class ProductFactory(BaseFactory):
    AVAILABLE_SUBCATEGORIES = ALL_PRODUCT_SUBCATEGORIES_IDS

    class Meta:
        model = models.Product
        exclude = ("AVAILABLE_SUBCATEGORIES",)

    subcategoryId = subcategories.LIVRE_PAPIER.id
    name = factory.Sequence("Product {}".format)
    description = factory.Sequence("A passionate description of product {}".format)
    ean = factory.LazyAttribute(
        lambda o: (
            fake.ean13()
            if o.subcategoryId in THINGS_PRODUCT_SUBCATEGORIES_IDS or getattr(o, "set_all_fields", False)
            else None
        )
    )

    @classmethod
    def _create(
        cls,
        model_class: type[models.Product],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.Product:
        # Graciously provide the required idAtProviders if lastProvider is given.

        if kwargs["subcategoryId"] not in cls.AVAILABLE_SUBCATEGORIES:
            raise ValueError(f"Events products subcategory can only be one of {cls.AVAILABLE_SUBCATEGORIES}.")

        if "extraData" not in kwargs:
            subcategory_id = kwargs.get("subcategoryId")
            assert isinstance(
                subcategory_id, str
            )  # if the subcategoryId was not given in the factory, it will get the default subcategoryId
            kwargs["extraData"] = build_extra_data_from_subcategory(
                subcategory_id, kwargs.pop("set_all_fields", False), True
            )

        if kwargs.get("extraData") and "ean" in kwargs.get("extraData", {}):
            raise ValueError("'ean' key is no longer allowed in extraData. Use the ean column instead.")

        return super()._create(model_class, *args, **kwargs)


class ProductMediationFactory(BaseFactory):
    class Meta:
        model = models.ProductMediation

    product = factory.SubFactory(ProductFactory)
    uuid = factory.LazyFunction(lambda: str(uuid.uuid4()))
    imageType = offers_models.ImageType.RECTO


class EventProductFactory(ProductFactory):
    AVAILABLE_SUBCATEGORIES = EVENT_PRODUCT_SUBCATEGORIES_IDS
    subcategoryId = subcategories.SEANCE_CINE.id


class ThingProductFactory(ProductFactory):
    AVAILABLE_SUBCATEGORIES = THINGS_PRODUCT_SUBCATEGORIES_IDS
    subcategoryId = subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id


class OfferMetaDataFactory(BaseFactory):
    class Meta:
        model = offers_models.OfferMetaData

    offer = factory.SubFactory("pcapi.core.offers.factories.OfferFactory")
    videoUrl: str | None = None


def build_extra_data_from_subcategory(
    subcategory_id: str, set_all_fields: bool, build_for_product: bool = False
) -> offers_models.OfferExtraData:
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
                extradata[field] = fake.name()  # type: ignore[literal-required]
            case subcategories.ExtraDataFieldEnum.GTL_ID.value:
                if subcategory_id == subcategories.LIVRE_PAPIER.id:
                    if build_for_product:
                        extradata[field] = random.choice(list(GTLS.keys()))
                else:
                    extradata[field] = random.choice(list(TITELIVE_MUSIC_GENRES_BY_GTL_ID.keys()))
            case subcategories.ExtraDataFieldEnum.VISA.value:
                extradata[field] = fake.ean()
            case subcategories.ExtraDataFieldEnum.MUSIC_TYPE.value:
                extradata[field] = str(random.choice(music.OLD_MUSIC_TYPES).code)
            case subcategories.ExtraDataFieldEnum.MUSIC_SUB_TYPE.value:
                music_type_code = extradata.get(subcategories.ExtraDataFieldEnum.MUSIC_TYPE.value)
                assert music_type_code
                music_type = music.MUSIC_TYPES_BY_CODE.get(int(music_type_code))
                assert music_type
                extradata[field] = str(random.choice(music_type.children).code)
            case subcategories.ExtraDataFieldEnum.SHOW_TYPE.value:
                extradata[field] = str(random.choice(show.SHOW_TYPES).code)
            case subcategories.ExtraDataFieldEnum.SHOW_SUB_TYPE.value:
                show_type_code = extradata.get(subcategories.ExtraDataFieldEnum.SHOW_TYPE.value)
                assert show_type_code
                show_type = show.SHOW_TYPES_BY_CODE.get(int(show_type_code))
                assert show_type
                extradata[field] = str(random.choice(show_type.children).code)

    return offers_models.OfferExtraData(**extradata)


class OfferFactory(BaseFactory):
    class Meta:
        model = models.Offer

    venue = factory.SubFactory(offerers_factories.VenueFactory)
    subcategoryId = factory.LazyAttribute(
        lambda o: (o.product.subcategoryId if hasattr(o, "product") else subcategories.SUPPORT_PHYSIQUE_FILM.id)
    )
    name = factory.LazyAttributeSequence(
        lambda o, n: o.product.name if hasattr(o, "product") and o.product else f"Offer {n}"
    )
    description = factory.LazyAttributeSequence(
        lambda o, n: None if hasattr(o, "product") and o.product else f"A passionate description of offer {n}"
    )
    audioDisabilityCompliant = False
    mentalDisabilityCompliant = False
    motorDisabilityCompliant = False
    visualDisabilityCompliant = False
    lastValidationType = OfferValidationType.AUTO

    ean = factory.LazyAttributeSequence(lambda o, n: fake.ean13() if getattr(o, "set_all_fields", False) else None)

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

        # TODO: (tcoudray-pass, 18/06/2025) Refacto when we get rid of `isActive`
        if (
            kwargs["isActive"]
            and kwargs.get("validation") != models.OfferValidationStatus.DRAFT
            and "publicationDatetime" not in kwargs
        ):
            kwargs["publicationDatetime"] = datetime.datetime.now() - datetime.timedelta(minutes=5)

        if kwargs.get("validation") != models.OfferValidationStatus.DRAFT and "finalizationDatetime" not in kwargs:
            kwargs["finalizationDatetime"] = datetime.datetime.now()

        product = kwargs.get("product")
        if product:
            _check_offer_kwargs(product, kwargs)
            kwargs["name"] = product.name
            kwargs["subcategoryId"] = product.subcategoryId
            kwargs["description"] = None
            kwargs["ean"] = product.ean
            kwargs["extraData"] = None
            kwargs["durationMinutes"] = None
        else:
            if "extraData" not in kwargs:
                subcategory_id = kwargs.get("subcategoryId")
                assert isinstance(
                    subcategory_id, str
                )  # if the subcategoryId was not given in the factory, it will get the default subcategoryId
                kwargs["extraData"] = build_extra_data_from_subcategory(
                    subcategory_id, kwargs.pop("set_all_fields", False)
                )
        if "offererAddress" not in kwargs and "offererAddressId" not in kwargs:
            venue = kwargs.get("venue")
            if venue:
                kwargs["offererAddress"] = venue.offererAddress

        kwargs.pop("isActive", None)
        return super()._create(model_class, *args, **kwargs)


class DraftOfferFactory(OfferFactory):
    isActive = False
    validation = models.OfferValidationStatus.DRAFT


class ArtistProductLinkFactory(BaseFactory):
    class Meta:
        model = artist_models.ArtistProductLink

    artist_type = artist_models.ArtistType.AUTHOR


def _check_offer_kwargs(product: models.Product, kwargs: dict[str, typing.Any]) -> None:
    if kwargs.get("extraData") and "ean" in kwargs.get("extraData", {}):
        raise ValueError("'ean' key is no longer allowed in extraData. Use the ean column instead.")
    if kwargs.get("name") and kwargs.get("name") != product.name:
        raise ValueError("Name of the offer and the product must be the same")
    if kwargs.get("subcategoryId") and kwargs.get("subcategoryId") != product.subcategoryId:
        raise ValueError("SubcategoryId of the offer and the product must be the same")
    if kwargs.get("durationMinutes"):
        raise ValueError("DurationMinutes of the offer must be None when product is given")
    if kwargs.get("description"):
        raise ValueError("Description of the offer must be None when product is given")
    if kwargs.get("extraData") and kwargs.get("extraData") != product.extraData:
        raise ValueError("ExtraData of the offer and the product must be the same")


class EventOfferFactory(OfferFactory):
    subcategoryId = factory.LazyAttribute(
        lambda o: (o.product.subcategoryId if hasattr(o, "product") else subcategories.SEANCE_CINE.id)
    )


class ThingOfferFactory(OfferFactory):
    subcategoryId = factory.LazyAttribute(
        lambda o: (o.product.subcategoryId if hasattr(o, "product") else subcategories.CARTE_CINE_ILLIMITE.id)
    )


class DigitalOfferFactory(OfferFactory):
    subcategoryId = factory.LazyAttribute(
        lambda o: (o.product.subcategoryId if hasattr(o, "product") else subcategories.VOD.id)
    )
    url = factory.Sequence("http://example.com/offer/{}".format)
    venue = factory.SubFactory(offerers_factories.VirtualVenueFactory)
    offererAddress: factory.declarations.BaseDeclaration | None = None


class HeadlineOfferFactory(BaseFactory):
    class Meta:
        model = models.HeadlineOffer

    offer = factory.SubFactory(
        OfferFactory,
        isActive=True,
        venue=factory.SubFactory(offerers_factories.VenueFactory, venueTypeCode=VenueTypeCode.LIBRARY),
    )
    venue = factory.SelfAttribute("offer.venue")
    timespan = (datetime.datetime.utcnow(),)

    @factory.post_generation
    def without_mediation(
        self,
        create: bool,
        without_mediation: bool = False,
        **_kwargs: typing.Any,
    ) -> None:
        if create:
            StockFactory(offer=self.offer)
            if not without_mediation:
                MediationFactory(offer=self.offer)


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
        label = (
            db.session.query(offers_models.PriceCategoryLabel)
            .filter_by(label=kwargs.get("label"), venue=kwargs.get("venue"))
            .one_or_none()
        )
        if label:
            return label
        return super()._create(model_class, *args, **kwargs)


class PriceCategoryFactory(BaseFactory):
    class Meta:
        model = models.PriceCategory

    price = decimal.Decimal("10.1")
    offer = factory.SubFactory(EventOfferFactory)
    priceCategoryLabel = factory.SubFactory(PriceCategoryLabelFactory, venue=factory.SelfAttribute("..offer.venue"))


_DAY_TO_WEEKDAY = {
    0: models.Weekday.MONDAY,
    1: models.Weekday.TUESDAY,
    2: models.Weekday.WEDNESDAY,
    3: models.Weekday.THURSDAY,
    4: models.Weekday.FRIDAY,
    5: models.Weekday.SATURDAY,
    6: models.Weekday.SUNDAY,
}


class StockFactory(BaseFactory):
    class Meta:
        model = models.Stock

    offer = factory.SubFactory(OfferFactory)
    price = decimal.Decimal("10.1")
    quantity = 1000

    beginningDatetime: factory.declarations.BaseDeclaration | None = factory.Maybe(
        "offer.isEvent",
        factory.LazyFunction(
            lambda: datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(days=30)
        ),
        None,
    )
    bookingLimitDatetime: factory.declarations.BaseDeclaration | None = factory.Maybe(
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
                ActivationCodeFactory.create(stockId=self.id, code=code)  # type: ignore[attr-defined]
        else:
            available_activation_counts = 5
            self.quantity = available_activation_counts
            ActivationCodeFactory.create_batch(size=available_activation_counts, stockId=self.id, **kwargs)  # type: ignore[attr-defined]


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


class OfferComplianceFactory(BaseFactory):
    class Meta:
        model = models.OfferCompliance

    offer = factory.SubFactory(OfferFactory)
    compliance_score = 12
    compliance_reasons = ["stock_price", "offer_description"]
