from datetime import datetime
import decimal
import enum
import typing
from typing import Any

from pydantic import EmailStr
from pydantic import Field
from pydantic import HttpUrl
from pydantic import constr
from pydantic import root_validator
from pydantic import validator
from pydantic.utils import GetterDict

from pcapi.core.categories.subcategories import SubcategoryIdEnum
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import repository as offers_repository
from pcapi.core.offers.serialize import CollectiveOfferType
from pcapi.models.offer_mixin import OfferStatus
from pcapi.routes.native.v1.serialization.common_models import AccessibilityComplianceMixin
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import base as base_serializers
from pcapi.serialization.utils import dehumanize_field
from pcapi.serialization.utils import humanize_field
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date
from pcapi.validation.routes.offers import check_offer_ean_is_valid
from pcapi.validation.routes.offers import check_offer_name_length_is_valid


class SubcategoryGetterDict(GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        if key == "conditional_fields":
            return list(self._obj.conditional_fields.keys())
        return super().get(key, default)


class SubcategoryResponseModel(BaseModel):
    id: str
    category_id: str
    pro_label: str
    app_label: str
    search_group_name: str | None
    is_event: bool
    conditional_fields: list[str]
    can_expire: bool
    can_be_duo: bool
    can_be_educational: bool
    online_offline_platform: str
    is_digital_deposit: bool
    is_physical_deposit: bool
    reimbursement_rule: str
    is_selectable: bool
    can_be_withdrawable: bool

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        getter_dict = SubcategoryGetterDict
        orm_mode = True


class CategoryResponseModel(BaseModel):
    id: str
    pro_label: str
    is_selectable: bool

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class PostOfferBodyModel(BaseModel):
    audio_disability_compliant: bool
    booking_email: EmailStr | None
    description: str | None
    duration_minutes: int | None
    external_ticket_office_url: HttpUrl | None
    extra_data: Any
    is_duo: bool | None
    is_national: bool | None
    mental_disability_compliant: bool
    motor_disability_compliant: bool
    name: str
    subcategory_id: str
    url: HttpUrl | None
    venue_id: int
    visual_disability_compliant: bool
    withdrawal_delay: int | None
    withdrawal_details: str | None
    withdrawal_type: offers_models.WithdrawalTypeEnum | None

    @validator("name", pre=True)
    def validate_name(cls, name: str, values: dict) -> str:
        check_offer_name_length_is_valid(name)
        return name

    @root_validator()
    def validate_ean(cls, values: dict) -> dict:
        if offers_api.should_retrieve_book_from_ean(values.get("subcategory_id", "")):
            check_offer_ean_is_valid(values.get("extra_data", {}).get("ean"))
        return values

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class OfferAddressType(enum.Enum):
    OFFERER_VENUE = "offererVenue"
    SCHOOL = "school"
    OTHER = "other"


class PatchOfferBodyModel(BaseModel, AccessibilityComplianceMixin):
    bookingEmail: EmailStr | None
    description: str | None
    isNational: bool | None
    name: str | None
    extraData: Any
    externalTicketOfficeUrl: HttpUrl | None
    url: HttpUrl | None
    withdrawalDetails: str | None
    withdrawalType: offers_models.WithdrawalTypeEnum | None
    withdrawalDelay: int | None
    isActive: bool | None
    isDuo: bool | None
    durationMinutes: int | None
    mediaUrls: list[str] | None
    ageMin: int | None
    ageMax: int | None
    conditions: str | None
    shouldSendMail: bool | None

    @validator("name", pre=True, allow_reuse=True)
    def validate_name(cls, name: str) -> str:
        if name:
            check_offer_name_length_is_valid(name)
        return name

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class PatchOfferPublishBodyModel(BaseModel):
    id: int


class PatchOfferActiveStatusBodyModel(BaseModel):
    is_active: bool
    ids: list[int]

    class Config:
        alias_generator = to_camel


class PatchAllOffersActiveStatusBodyModel(BaseModel):
    is_active: bool
    offerer_id: int | None
    venue_id: int | None
    # We should not use an alias nameOrIsbn, but ListOffersQueryModel is used
    # by the pro front for individual and collective search and most of the logic
    # is shared on the offer search page
    name_or_ean: str | None = Field(alias="nameOrIsbn")
    category_id: str | None
    creation_mode: str | None
    status: str | None
    period_beginning_date: datetime | None
    period_ending_date: datetime | None

    _dehumanize_offerer_id = dehumanize_field("offerer_id")
    _dehumanize_venue_id = dehumanize_field("venue_id")

    class Config:
        alias_generator = to_camel


class PatchAllOffersActiveStatusResponseModel(BaseModel):
    pass


class ListOffersStockResponseModel(BaseModel):
    nonHumanizedId: int
    hasBookingLimitDatetimePassed: bool
    remainingQuantity: int | str
    beginningDatetime: datetime | None
    bookingQuantity: int | None

    @validator("remainingQuantity", pre=True)
    def validate_remaining_quantity(cls, remainingQuantity: int | str) -> int | str:
        if remainingQuantity and remainingQuantity != "0" and not isinstance(remainingQuantity, int):
            return remainingQuantity.lstrip("0")
        return remainingQuantity


class ListOffersOfferResponseModel(BaseModel):
    hasBookingLimitDatetimesPassed: bool
    nonHumanizedId: int
    isActive: bool
    isEditable: bool
    isEvent: bool
    isThing: bool
    isEducational: bool
    name: str
    stocks: list[ListOffersStockResponseModel]
    thumbUrl: str | None
    productIsbn: str | None
    subcategoryId: SubcategoryIdEnum
    venue: base_serializers.ListOffersVenueResponseModel
    status: str
    isShowcase: bool | None


class ListOffersResponseModel(BaseModel):
    __root__: list[ListOffersOfferResponseModel]

    class Config:
        json_encoders = {datetime: format_into_utc_date}


class ListOffersQueryModel(BaseModel):
    # We should not use an alias nameOrIsbn, but ListOffersQueryModel is used
    # by the pro front for individual and collective search and most of the logic
    # is shared on the offer search page
    name_or_ean: str | None = Field(alias="nameOrIsbn")
    offerer_id: int | None
    status: str | None
    venue_id: int | None
    categoryId: str | None
    creation_mode: str | None
    period_beginning_date: str | None
    period_ending_date: str | None
    collective_offer_type: CollectiveOfferType | None

    class Config:
        alias_generator = to_camel
        extra = "forbid"
        arbitrary_types_allowed = True


class GetOfferStockResponseModel(BaseModel):
    activationCodesExpirationDatetime: datetime | None
    beginningDatetime: datetime | None
    bookingLimitDatetime: datetime | None
    dateCreated: datetime
    dateModified: datetime
    dnBookedQuantity: int = Field(alias="bookingsQuantity")
    hasActivationCode: bool
    isBookable: bool
    isEventDeletable: bool
    isEventExpired: bool
    isSoftDeleted: bool
    nonHumanizedId: int
    price: float
    priceCategoryId: int | None
    quantity: int | None
    remainingQuantity: int | str | None

    @classmethod
    def from_orm(cls, stock: offers_models.Stock) -> "GetOfferStockResponseModel":
        # here we have N+1 requests (for each stock we query an activation code)
        # but it should be more efficient than loading all activationCodes of all stocks
        if stock.canHaveActivationCodes:
            availble_activation_code = offers_repository.get_available_activation_code(stock)
            stock.hasActivationCode = availble_activation_code is not None
            stock.activationCodesExpirationDatetime = (
                availble_activation_code.expirationDate if availble_activation_code else None
            )
        else:
            stock.hasActivationCode = False
            stock.activationCodesExpirationDatetime = None
        return super().from_orm(stock)

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}


class GetOfferManagingOffererResponseModel(BaseModel):
    id: str
    nonHumanizedId: int
    name: str

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


class GetOfferVenueResponseModel(BaseModel, AccessibilityComplianceMixin):
    address: str | None
    bookingEmail: str | None
    city: str | None
    departementCode: str | None
    id: str
    nonHumanizedId: int
    isVirtual: bool
    lastProviderId: str | None
    managingOfferer: GetOfferManagingOffererResponseModel
    name: str
    postalCode: str | None
    publicName: str | None

    _humanize_id = humanize_field("id")
    _humanize_last_provider_id = humanize_field("lastProviderId")

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}


# FIXME (apibrac, 2021-03-23): we should not expose so much information to the fronts.
# Only the name is needed in pro and nothing in webapp => can we just send a providerName field?
# The field lastProviderId is not used anywhere in the fronts either.
class GetOfferLastProviderResponseModel(BaseModel):
    enabledForPro: bool
    id: str
    isActive: bool
    localClass: str | None
    name: str

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


class GetOfferMediationResponseModel(BaseModel):
    authorId: str | None
    credit: str | None
    dateCreated: datetime
    dateModifiedAtLastProvider: datetime | None
    fieldsUpdated: list[str]
    id: str
    idAtProviders: str | None
    isActive: bool
    lastProviderId: str | None
    offerId: str
    thumbCount: int
    thumbUrl: str | None

    _humanize_id = humanize_field("id")
    _humanize_offer_id = humanize_field("offerId")
    _humanize_last_provider_id = humanize_field("lastProviderId")

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}


class PriceCategoryResponseModel(BaseModel):
    price: float
    label: str
    id: int

    class Config:
        orm_mode = True


class GetIndividualOfferResponseModel(BaseModel, AccessibilityComplianceMixin):
    activeMediation: GetOfferMediationResponseModel | None
    bookingEmail: str | None
    dateCreated: datetime
    description: str | None
    durationMinutes: int | None
    extraData: Any
    hasBookingLimitDatetimesPassed: bool
    isActive: bool
    isDigital: bool
    isDuo: bool
    isEditable: bool
    isEducational: bool
    isEvent: bool
    isNational: bool
    isThing: bool
    nonHumanizedId: int
    lastProvider: GetOfferLastProviderResponseModel | None
    mediaUrls: list[str]
    mediations: list[GetOfferMediationResponseModel]
    name: str
    priceCategories: list[PriceCategoryResponseModel] | None
    stocks: list[GetOfferStockResponseModel]
    subcategoryId: SubcategoryIdEnum
    thumbUrl: str | None
    externalTicketOfficeUrl: str | None
    url: str | None
    venue: GetOfferVenueResponseModel
    withdrawalDelay: int | None
    withdrawalDetails: str | None
    withdrawalType: offers_models.WithdrawalTypeEnum | None
    status: OfferStatus

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}
        use_enum_values = True


class ImageBodyModel(BaseModel):
    url: str


class CategoriesResponseModel(BaseModel):
    categories: list[CategoryResponseModel]
    subcategories: list[SubcategoryResponseModel]


class DeleteOfferRequestBody(BaseModel):
    ids: list[int | None]


class CreatePriceCategoryModel(BaseModel):
    if typing.TYPE_CHECKING:
        label: str
    else:
        label: constr(min_length=1, max_length=50)
    price: decimal.Decimal

    class Config:
        extra = "forbid"


class EditPriceCategoryModel(BaseModel):
    id: int
    if typing.TYPE_CHECKING:
        label: str | None
    else:
        label: constr(min_length=1, max_length=50) | None
    price: decimal.Decimal | None

    class Config:
        extra = "forbid"


class PriceCategoryBody(BaseModel):
    price_categories: list[CreatePriceCategoryModel | EditPriceCategoryModel]

    class Config:
        alias_generator = to_camel
