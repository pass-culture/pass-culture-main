import datetime
import decimal
import enum
import typing
from typing import Any

from pydantic.v1 import EmailStr
from pydantic.v1 import Field
from pydantic.v1 import HttpUrl
from pydantic.v1 import conlist
from pydantic.v1 import constr
from pydantic.v1 import validator
from pydantic.v1.utils import GetterDict

from pcapi.core.categories.subcategories_v2 import SubcategoryIdEnum
from pcapi.core.educational.models import CollectiveOfferDisplayedStatus
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import repository as offers_repository
from pcapi.core.offers.serialize import CollectiveOfferType
from pcapi.models.offer_mixin import OfferStatus
from pcapi.routes.native.v1.serialization.common_models import AccessibilityComplianceMixin
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import base as base_serializers
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date
from pcapi.validation.routes.offers import check_offer_name_length_is_valid


class SubcategoryGetterDict(GetterDict):
    def get(self, key: str, default: Any | None = None) -> Any:
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
    booking_contact: EmailStr | None
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

    @validator("withdrawal_type")
    def validate_withdrawal_type(cls, value: offers_models.WithdrawalTypeEnum) -> offers_models.WithdrawalTypeEnum:
        if value == offers_models.WithdrawalTypeEnum.IN_APP:
            raise ValueError("Withdrawal type cannot be in_app for manually created offers")
        return value

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class OfferAddressType(enum.Enum):
    OFFERER_VENUE = "offererVenue"
    SCHOOL = "school"
    OTHER = "other"


class PatchOfferBodyModel(BaseModel, AccessibilityComplianceMixin):
    bookingContact: EmailStr | None
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
    period_beginning_date: datetime.date | None
    period_ending_date: datetime.date | None

    class Config:
        alias_generator = to_camel


class PatchAllOffersActiveStatusResponseModel(BaseModel):
    pass


class ListOffersStockResponseModel(BaseModel):
    id: int
    hasBookingLimitDatetimePassed: bool
    remainingQuantity: int | str
    beginningDatetime: datetime.datetime | None
    bookingQuantity: int | None

    @validator("remainingQuantity", pre=True)
    def validate_remaining_quantity(cls, remainingQuantity: int | str) -> int | str:
        if remainingQuantity and remainingQuantity != "0" and not isinstance(remainingQuantity, int):
            return remainingQuantity.lstrip("0")
        return remainingQuantity


class ListOffersOfferResponseModel(BaseModel):
    hasBookingLimitDatetimesPassed: bool
    id: int
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
    status: OfferStatus
    isShowcase: bool | None


class ListOffersResponseModel(BaseModel):
    __root__: list[ListOffersOfferResponseModel]

    class Config:
        json_encoders = {datetime.datetime: format_into_utc_date}


class ListOffersQueryModel(BaseModel):
    # We should not use an alias nameOrIsbn, but ListOffersQueryModel is used
    # by the pro front for individual and collective search and most of the logic
    # is shared on the offer search page
    name_or_ean: str | None = Field(alias="nameOrIsbn")
    offerer_id: int | None
    status: OfferStatus | CollectiveOfferDisplayedStatus | None
    venue_id: int | None
    categoryId: str | None
    creation_mode: str | None
    period_beginning_date: datetime.date | None
    period_ending_date: datetime.date | None
    collective_offer_type: CollectiveOfferType | None

    class Config:
        alias_generator = to_camel
        extra = "forbid"
        arbitrary_types_allowed = True


class GetOfferStockResponseModel(BaseModel):
    activationCodesExpirationDatetime: datetime.datetime | None
    beginningDatetime: datetime.datetime | None
    bookingLimitDatetime: datetime.datetime | None
    dnBookedQuantity: int = Field(alias="bookingsQuantity")
    hasActivationCode: bool
    isEventDeletable: bool
    id: int
    price: float
    priceCategoryId: int | None
    quantity: int | None
    remainingQuantity: int | str | None

    @classmethod
    def from_orm(cls, stock: offers_models.Stock) -> "GetOfferStockResponseModel":
        # here we have N+1 requests (for each stock we query an activation code)
        # but it should be more efficient than loading all activationCodes of all stocks
        if stock.canHaveActivationCodes:
            available_activation_code = offers_repository.get_available_activation_code(stock)
            stock.hasActivationCode = available_activation_code is not None
            stock.activationCodesExpirationDatetime = (
                available_activation_code.expirationDate if available_activation_code else None
            )
        else:
            stock.hasActivationCode = False
            stock.activationCodesExpirationDatetime = None
        return super().from_orm(stock)

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
        json_encoders = {datetime.datetime: format_into_utc_date}


class GetOfferManagingOffererResponseModel(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class GetOfferVenueResponseModel(BaseModel, AccessibilityComplianceMixin):
    address: str | None
    bookingEmail: str | None
    city: str | None
    departementCode: str | None
    id: int
    isVirtual: bool
    managingOfferer: GetOfferManagingOffererResponseModel
    name: str
    postalCode: str | None
    publicName: str | None

    class Config:
        orm_mode = True
        json_encoders = {datetime.datetime: format_into_utc_date}


class GetOfferLastProviderResponseModel(BaseModel):
    name: str

    class Config:
        orm_mode = True


class GetOfferMediationResponseModel(BaseModel):
    authorId: str | None
    credit: str | None
    thumbUrl: str | None

    class Config:
        orm_mode = True


class PriceCategoryResponseModel(BaseModel):
    price: float
    label: str
    id: int

    class Config:
        orm_mode = True


class GetIndividualOfferResponseModel(BaseModel, AccessibilityComplianceMixin):
    activeMediation: GetOfferMediationResponseModel | None
    bookingContact: str | None
    bookingEmail: str | None
    dateCreated: datetime.datetime
    description: str | None
    durationMinutes: int | None
    extraData: Any
    hasBookingLimitDatetimesPassed: bool
    isActive: bool
    isActivable: bool
    isDigital: bool
    isDuo: bool
    isEditable: bool
    isEvent: bool
    isNational: bool
    isThing: bool
    id: int
    lastProvider: GetOfferLastProviderResponseModel | None
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
        json_encoders = {datetime.datetime: format_into_utc_date}
        use_enum_values = True


class GetStocksResponseModel(BaseModel):
    stocks: list[GetOfferStockResponseModel]
    stock_count: int

    class Config:
        json_encoders = {datetime.datetime: format_into_utc_date}


class StockStatsResponseModel(BaseModel):
    oldestStock: datetime.datetime | None
    newestStock: datetime.datetime | None
    stockCount: int | None
    remainingQuantity: int | None

    class Config:
        json_encoders = {datetime.datetime: format_into_utc_date}


class StocksQueryModel(BaseModel):
    date: datetime.date | None
    time: datetime.time | None
    price_category_id: int | None
    order_by: offers_repository.StocksOrderedBy = offers_repository.StocksOrderedBy.BEGINNING_DATETIME
    order_by_desc: bool = False
    page: int = 1
    stocks_limit_per_page: int = offers_repository.LIMIT_STOCKS_PER_PAGE


class DeleteStockListBody(BaseModel):
    if typing.TYPE_CHECKING:
        ids_to_delete: list[int]
    else:
        ids_to_delete: conlist(int, max_items=offers_repository.STOCK_LIMIT_TO_DELETE)


class DeleteFilteredStockListBody(BaseModel):
    date: datetime.date | None
    time: datetime.time | None
    price_category_id: int | None


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

    @validator("price_categories")
    def get_unique_price_categories(
        cls,
        price_categories: list[CreatePriceCategoryModel | EditPriceCategoryModel],
    ) -> list[CreatePriceCategoryModel | EditPriceCategoryModel]:
        unique_price_categories = []
        for price_category in price_categories:
            if (price_category.label, price_category.price) in unique_price_categories:
                raise ValueError("Price categories must be unique")
            unique_price_categories.append((price_category.label, price_category.price))
        return price_categories

    class Config:
        alias_generator = to_camel
