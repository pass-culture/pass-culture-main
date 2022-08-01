from datetime import datetime
import enum

from pydantic import Field
from pydantic import validator

from pcapi.core.categories.subcategories import SubcategoryIdEnum
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.educational.models import StudentLevels
from pcapi.core.offerers.models import Venue
from pcapi.models.offer_mixin import OfferStatus
from pcapi.routes.native.v1.serialization.common_models import AccessibilityComplianceMixin
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization.educational_institutions import EducationalInstitutionResponseModel
from pcapi.routes.serialization.offers_serialize import ListOffersVenueResponseModel
from pcapi.serialization.utils import dehumanize_field
from pcapi.serialization.utils import dehumanize_list_field
from pcapi.serialization.utils import humanize_field
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize
from pcapi.validation.routes.offers import check_offer_name_length_is_valid


class ListCollectiveOffersQueryModel(BaseModel):
    nameOrIsbn: str | None
    offerer_id: int | None
    status: str | None
    venue_id: int | None
    categoryId: str | None
    creation_mode: str | None
    period_beginning_date: str | None
    period_ending_date: str | None

    _dehumanize_venue_id = dehumanize_field("venue_id")
    _dehumanize_offerer_id = dehumanize_field("offerer_id")

    class Config:
        alias_generator = to_camel
        extra = "forbid"
        arbitrary_types_allowed = True


class CollectiveOffersStockResponseModel(BaseModel):
    id: str
    hasBookingLimitDatetimePassed: bool
    offerId: str
    remainingQuantity: int | str
    beginningDatetime: datetime | None

    @validator("remainingQuantity", pre=True)
    def validate_remaining_quantity(cls, remainingQuantity):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        if remainingQuantity and remainingQuantity != "0" and not isinstance(remainingQuantity, int):
            return remainingQuantity.lstrip("0")
        return remainingQuantity


class CollectiveOfferResponseModel(BaseModel):
    hasBookingLimitDatetimesPassed: bool
    id: str
    isActive: bool
    isEditable: bool
    isEvent: bool
    isThing: bool
    isEducational: bool
    name: str
    stocks: list[CollectiveOffersStockResponseModel]
    thumbUrl: str | None
    productIsbn: str | None
    subcategoryId: SubcategoryIdEnum
    venue: ListOffersVenueResponseModel
    status: str
    venueId: str
    isShowcase: bool | None
    offerId: str | None
    educationalInstitution: EducationalInstitutionResponseModel | None
    interventionArea: list[str]


class ListCollectiveOffersResponseModel(BaseModel):
    __root__: list[CollectiveOfferResponseModel]

    class Config:
        json_encoders = {datetime: format_into_utc_date}


def serialize_collective_offers_capped(
    paginated_offers: list[CollectiveOffer | CollectiveOfferTemplate],
) -> list[CollectiveOfferResponseModel]:
    return [_serialize_offer_paginated(offer) for offer in paginated_offers]


def _serialize_offer_paginated(offer: CollectiveOffer | CollectiveOfferTemplate) -> CollectiveOfferResponseModel:
    serialized_stock = _serialize_stock(offer.id, getattr(offer, "collectiveStock", None))

    serialized_stocks = [serialized_stock] if serialized_stock is not None else []
    is_offer_template = isinstance(offer, CollectiveOfferTemplate)
    institution = getattr(offer, "institution", None)

    return CollectiveOfferResponseModel(
        hasBookingLimitDatetimesPassed=offer.hasBookingLimitDatetimesPassed if not is_offer_template else False,
        id=humanize(offer.id),
        isActive=offer.isActive,
        isEditable=offer.isEditable,
        isEvent=True,
        isThing=False,
        isEducational=True,
        productIsbn=None,
        name=offer.name,
        stocks=serialized_stocks,
        thumbUrl=None,
        subcategoryId=offer.subcategoryId,
        venue=_serialize_venue(offer.venue),  # type: ignore [arg-type]
        venueId=humanize(offer.venue.id),
        status=offer.status.name,  # type: ignore [attr-defined]
        isShowcase=is_offer_template,
        offerId=humanize(offer.offerId),
        educationalInstitution=EducationalInstitutionResponseModel.from_orm(institution) if institution else None,
        interventionArea=offer.interventionArea,
    )


def _serialize_stock(offer_id: int, stock: CollectiveStock | None = None) -> dict:
    if stock:
        return {
            "id": humanize(stock.id),
            "offerId": humanize(offer_id),
            "hasBookingLimitDatetimePassed": stock.hasBookingLimitDatetimePassed,
            "remainingQuantity": 0 if stock.isSoldOut else 1,
            "beginningDatetime": stock.beginningDatetime,
        }
    return {
        "id": humanize(0),
        "offerId": humanize(offer_id),
        "hasBookingLimitDatetimePassed": False,
        "remainingQuantity": 1,
        "beginningDatetime": datetime(year=2030, month=1, day=1),
    }


def _serialize_venue(venue: Venue) -> dict:
    return {
        "id": humanize(venue.id),
        "isVirtual": venue.isVirtual,
        "managingOffererId": humanize(venue.managingOffererId),
        "name": venue.name,
        "offererName": venue.managingOfferer.name,
        "publicName": venue.publicName,
        "departementCode": venue.departementCode,
    }


class OfferDomain(BaseModel):
    id: int
    name: str

    class Config:
        alias_generator = to_camel
        orm_mode = True


class GetCollectiveOfferManagingOffererResponseModel(BaseModel):
    address: str | None
    city: str
    dateCreated: datetime
    dateModifiedAtLastProvider: datetime | None
    id: str
    idAtProviders: str | None
    isActive: bool
    isValidated: bool
    lastProviderId: str | None
    name: str
    postalCode: str
    # FIXME (dbaty, 2020-11-09): optional until we populate the database (PC-5693)
    siren: str | None
    thumbCount: int

    _humanize_id = humanize_field("id")
    _humanize_last_provider_id = humanize_field("lastProviderId")

    class Config:
        orm_mode = True


class GetCollectiveOfferVenueResponseModel(BaseModel, AccessibilityComplianceMixin):
    address: str | None
    bookingEmail: str | None
    city: str | None
    comment: str | None
    dateCreated: datetime | None
    dateModifiedAtLastProvider: datetime | None
    departementCode: str | None
    fieldsUpdated: list[str]
    id: str
    idAtProviders: str | None
    isValidated: bool
    isVirtual: bool
    lastProviderId: str | None
    latitude: float | None
    longitude: float | None
    managingOfferer: GetCollectiveOfferManagingOffererResponseModel
    managingOffererId: str
    name: str
    postalCode: str | None
    publicName: str | None
    siret: str | None
    thumbCount: int
    venueLabelId: str | None

    _humanize_id = humanize_field("id")
    _humanize_managing_offerer_id = humanize_field("managingOffererId")
    _humanize_last_provider_id = humanize_field("lastProviderId")
    _humanize_venue_label_id = humanize_field("venueLabelId")

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}


class OfferAddressType(enum.Enum):
    OFFERER_VENUE = "offererVenue"
    SCHOOL = "school"
    OTHER = "other"


class CollectiveOfferOfferVenueResponseModel(BaseModel):
    addressType: OfferAddressType
    otherAddress: str
    venueId: str


class GetCollectiveOfferCollectiveStockResponseModel(BaseModel):
    id: str
    isSoldOut: bool = Field(alias="isBooked")

    _humanize_id = humanize_field("id")

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}


class GetCollectiveOfferBaseResponseModel(BaseModel, AccessibilityComplianceMixin):
    id: str
    bookingEmail: str | None
    dateCreated: datetime
    description: str | None
    durationMinutes: int | None
    students: list[StudentLevels]
    offerVenue: CollectiveOfferOfferVenueResponseModel
    contactEmail: str
    contactPhone: str
    hasBookingLimitDatetimesPassed: bool
    offerId: str | None
    isActive: bool
    isEditable: bool
    nonHumanizedId: int
    name: str
    subcategoryId: SubcategoryIdEnum
    venue: GetCollectiveOfferVenueResponseModel
    venueId: str
    status: OfferStatus
    domains: list[OfferDomain]
    interventionArea: list[str]

    _humanize_id = humanize_field("id")
    _humanize_offerId = humanize_field("offerId")
    _humanize_venue_id = humanize_field("venueId")

    @classmethod
    def from_orm(cls, offer):  # type: ignore
        offer.nonHumanizedId = offer.id
        return super().from_orm(offer)

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}
        use_enum_values = True


class GetCollectiveOfferTemplateResponseModel(GetCollectiveOfferBaseResponseModel):
    priceDetail: str | None = Field(alias="educationalPriceDetail")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class GetCollectiveOfferResponseModel(GetCollectiveOfferBaseResponseModel):
    isBookable: bool
    collectiveStock: GetCollectiveOfferCollectiveStockResponseModel | None
    institution: EducationalInstitutionResponseModel | None
    isVisibilityEditable: bool


class CollectiveOfferResponseIdModel(BaseModel):
    id: str

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class CollectiveOfferVenueBodyModel(BaseModel):
    addressType: OfferAddressType
    otherAddress: str
    venueId: str

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class PostCollectiveOfferBodyModel(BaseModel):
    offerer_id: str
    venue_id: str
    subcategory_id: str
    name: str
    booking_email: str | None
    description: str | None
    domains: list[int] | None
    duration_minutes: int | None
    audio_disability_compliant: bool = False
    mental_disability_compliant: bool = False
    motor_disability_compliant: bool = False
    visual_disability_compliant: bool = False
    students: list[StudentLevels]
    offer_venue: CollectiveOfferVenueBodyModel
    contact_email: str
    contact_phone: str
    intervention_area: list[str] | None

    @validator("name", pre=True)
    def validate_name(cls: BaseModel, name: str, values: str) -> str:  # pylint: disable=no-self-argument
        check_offer_name_length_is_valid(name)
        return name

    @validator("domains", pre=True)
    def validate_domains(  # pylint: disable=no-self-argument
        cls: "PostCollectiveOfferBodyModel",
        domains: list[str] | None,
    ) -> list[str] | None:
        if domains is not None and len(domains) == 0:
            raise ValueError("domains must have at least one value")

        return domains

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class CollectiveOfferTemplateBodyModel(BaseModel):
    price_detail: str | None = Field(alias="educationalPriceDetail")

    @validator("price_detail")
    def validate_price_detail(cls, price_detail: str | None) -> str | None:  # pylint: disable=no-self-argument
        if price_detail and len(price_detail) > 1000:
            raise ValueError("Le détail du prix ne doit pas excéder 1000 caractères.")
        return price_detail

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class CollectiveOfferTemplateResponseIdModel(BaseModel):
    id: str

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class PatchCollectiveOfferBodyModel(BaseModel, AccessibilityComplianceMixin):
    bookingEmail: str | None
    description: str | None
    name: str | None
    students: list[StudentLevels] | None
    offerVenue: CollectiveOfferVenueBodyModel | None
    contactEmail: str | None
    contactPhone: str | None
    durationMinutes: int | None
    subcategoryId: SubcategoryIdEnum | None
    domains: list[int] | None

    @validator("name", allow_reuse=True)
    def validate_name(cls, name):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        assert name is not None and name.strip() != ""
        check_offer_name_length_is_valid(name)
        return name

    @validator("domains")
    def validate_domains_collective_offer_edition(  # pylint: disable=no-self-argument
        cls: "PatchCollectiveOfferBodyModel",
        domains: list[int] | None,
    ) -> list[int] | None:
        if domains is not None and len(domains) == 0:
            raise ValueError("domains must have at least one value")

        return domains

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class PatchCollectiveOfferTemplateBodyModel(PatchCollectiveOfferBodyModel):
    priceDetail: str | None
    domains: list[int] | None

    @validator("priceDetail")
    def validate_price_detail(cls, price_detail: str | None) -> str | None:  # pylint: disable=no-self-argument
        if price_detail and len(price_detail) > 1000:
            raise ValueError("Le détail du prix ne doit pas excéder 1000 caractères.")
        return price_detail

    @validator("domains")
    def validate_domains_collective_offer_template_edition(  # pylint: disable=no-self-argument
        cls: "PatchCollectiveOfferTemplateBodyModel",
        domains: list[int] | None,
    ) -> list[int] | None:
        if domains is not None and len(domains) == 0:
            raise ValueError("domains must have at least one value")

        return domains

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class CollectiveOfferFromTemplateResponseModel(BaseModel):
    id: str  # it's the stock id for compatibility
    beginningDatetime: datetime
    bookingLimitDatetime: datetime
    isEducationalStockEditable: bool = True
    numberOfTickets: int | None
    offerId: str
    price: float
    priceDetail: str | None = Field(alias="educationalPriceDetail")

    _humanize_id = humanize_field("id")

    @classmethod
    def from_orm(cls, offer: CollectiveOffer) -> "CollectiveOfferFromTemplateResponseModel":
        stock = offer.collectiveStock
        stock.offerId = humanize(offer.id)  # type: ignore [attr-defined]
        return super().from_orm(stock)

    class Config:
        json_encoders = {datetime: format_into_utc_date}
        orm_mode = True


class PatchCollectiveOfferActiveStatusBodyModel(BaseModel):
    is_active: bool
    ids: list[int]

    _dehumanize_ids = dehumanize_list_field("ids")

    class Config:
        alias_generator = to_camel


class PatchAllCollectiveOffersActiveStatusBodyModel(BaseModel):
    is_active: bool
    offerer_id: int | None
    venue_id: int | None
    name_or_isbn: str | None
    category_id: str | None
    creation_mode: str | None
    status: str | None
    period_beginning_date: datetime | None
    period_ending_date: datetime | None

    _dehumanize_offerer_id = dehumanize_field("offerer_id")
    _dehumanize_venue_id = dehumanize_field("venue_id")

    class Config:
        alias_generator = to_camel


class PatchCollectiveOfferEducationalInstitution(BaseModel):
    educational_institution_id: int | None
    is_creating_offer: bool

    class Config:
        alias_generator = to_camel
        extra = "forbid"
