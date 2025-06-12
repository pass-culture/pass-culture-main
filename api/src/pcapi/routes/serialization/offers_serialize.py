import datetime
import decimal
import typing
from typing import Any

from pydantic.v1 import EmailStr
from pydantic.v1 import Field
from pydantic.v1 import HttpUrl
from pydantic.v1 import conlist
from pydantic.v1 import constr
from pydantic.v1 import validator
from pydantic.v1.utils import GetterDict

from pcapi.core.categories.subcategories import SubcategoryIdEnum
from pcapi.core.educational.models import CollectiveOfferDisplayedStatus
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import repository as offers_repository
from pcapi.core.offers import schemas as offers_schemas
from pcapi.models.offer_mixin import OfferStatus
from pcapi.routes.native.v1.serialization.common_models import AccessibilityComplianceMixin
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import ConfiguredBaseModel
from pcapi.routes.serialization import base as base_serializers
from pcapi.routes.serialization import collective_offers_serialize
from pcapi.routes.serialization.address_serialize import AddressResponseIsLinkedToVenueModel
from pcapi.routes.serialization.address_serialize import retrieve_address_info_from_oa
from pcapi.serialization.utils import to_camel
from pcapi.utils import date as date_utils
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
    is_event: bool
    conditional_fields: list[str]
    can_expire: bool
    can_be_duo: bool
    online_offline_platform: str
    is_digital_deposit: bool
    is_physical_deposit: bool
    reimbursement_rule: str
    is_selectable: bool
    can_be_withdrawable: bool
    can_have_opening_hours: bool

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
    address: offerers_schemas.AddressBodyModel | None
    audio_disability_compliant: bool
    booking_contact: EmailStr | None
    booking_email: EmailStr | None
    description: str | None
    duration_minutes: int | None
    external_ticket_office_url: HttpUrl | None
    extra_data: dict[str, typing.Any] | None
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


class PatchOfferBodyModel(BaseModel, AccessibilityComplianceMixin):
    address: offerers_schemas.AddressBodyModel | None
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
    publicationDatetime: datetime.datetime | None
    bookingAllowedDatetime: datetime.datetime | None


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
    offerer_address_id: int | None

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


def offer_address_getter_dict_helper(offer: offers_models.Offer) -> AddressResponseIsLinkedToVenueModel | None:
    if offer.status == OfferStatus.DRAFT and not offer.offererAddressId:
        # The offer is still in the funnel creation and without any offererAddress defined
        # We don't want to blindly return venue.offererAddress
        return None
    offerer_address = None
    if offer.offererAddress:
        offerer_address = offer.offererAddress
    elif offer.venue.offererAddress:
        offerer_address = offer.venue.offererAddress
    if not offerer_address:  # The only offers without oa neither in themselves nor in venues are the numerics ones.
        return None
    label = offer.venue.common_name if offerer_address._isLinkedToVenue else offerer_address.label
    return AddressResponseIsLinkedToVenueModel(
        **retrieve_address_info_from_oa(offerer_address), label=label, isLinkedToVenue=offerer_address._isLinkedToVenue
    )


class ListOffersOfferResponseModelsGetterDict(GetterDict):
    def get(self, key: str, default: Any | None = None) -> Any:
        if key == "stocks":
            # TODO: front pro doesn't need the soft deleted stocks but maybe this could be handled in the request directly
            return [_serialize_stock(stock) for stock in self._obj.stocks if not stock.isSoftDeleted]
        if key == "productIsbn":
            return self._obj.ean
        if key == "venue":
            return _serialize_venue(self._obj.venue)
        if key == "isShowcase":
            return False
        if key == "isHeadlineOffer":
            return self._obj.is_headline_offer
        if key == "address":
            return offer_address_getter_dict_helper(self._obj)
        return super().get(key, default)


class ListOffersOfferResponseModel(BaseModel):
    hasBookingLimitDatetimesPassed: bool
    id: int
    isActive: bool
    isEditable: bool
    isEvent: bool
    isThing: bool
    isEducational: bool
    isHeadlineOffer: bool
    name: str
    stocks: list[ListOffersStockResponseModel]
    thumbUrl: str | None
    productIsbn: str | None
    subcategoryId: SubcategoryIdEnum
    venue: base_serializers.ListOffersVenueResponseModel
    status: OfferStatus
    isShowcase: bool | None
    address: AddressResponseIsLinkedToVenueModel | None
    isDigital: bool

    class Config:
        json_encoders = {datetime.datetime: format_into_utc_date}
        orm_mode = True
        getter_dict = ListOffersOfferResponseModelsGetterDict


class ListOffersResponseModel(BaseModel):
    __root__: list[ListOffersOfferResponseModel]

    class Config:
        json_encoders = {datetime.datetime: format_into_utc_date}


def _serialize_offer_paginated(offer: offers_models.Offer) -> ListOffersOfferResponseModel:
    return ListOffersOfferResponseModel.from_orm(offer)


def _serialize_stock(stock: offers_models.Stock) -> ListOffersStockResponseModel:
    return ListOffersStockResponseModel(
        id=stock.id,
        hasBookingLimitDatetimePassed=stock.hasBookingLimitDatetimePassed,
        remainingQuantity=stock.remainingQuantity,
        beginningDatetime=stock.beginningDatetime,
        bookingQuantity=stock.dnBookedQuantity,
    )


def _serialize_venue(venue: offerers_models.Venue) -> base_serializers.ListOffersVenueResponseModel:
    return base_serializers.ListOffersVenueResponseModel(
        id=venue.id,
        isVirtual=venue.isVirtual,
        name=venue.name,
        offererName=venue.managingOfferer.name,
        publicName=venue.publicName,
        departementCode=venue.departementCode,
    )


def serialize_capped_offers(paginated_offers: list[offers_models.Offer]) -> list[ListOffersOfferResponseModel]:
    return [_serialize_offer_paginated(offer) for offer in paginated_offers]


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
    collective_offer_type: collective_offers_serialize.CollectiveOfferType | None
    offerer_address_id: int | None

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
    allowedOnAdage: bool

    class Config:
        orm_mode = True


class GetOfferVenueResponseModel(BaseModel, AccessibilityComplianceMixin):
    street: str | None
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


def _build_base_opening_hours_dict() -> dict[str, list]:
    base_dict: dict[str, list] = {}

    for weekday in offers_models.Weekday:
        base_dict[weekday.name] = []

    return base_dict


class GetEventOpeningHoursResponseGetterDict(GetterDict):
    def get(self, key: str, default: Any | None = None) -> Any:
        if key == "openingHours":
            opening_hours_dict = _build_base_opening_hours_dict()
            event_opening_hours: offers_models.EventOpeningHours = self._obj
            for weekDayOpeningHours in event_opening_hours.weekDayOpeningHours:
                opening_hours_dict[weekDayOpeningHours.weekday.name] = [
                    {
                        "open": date_utils.int_to_time(int(timeSpan.lower)),
                        "close": date_utils.int_to_time(int(timeSpan.upper)),
                    }
                    for timeSpan in weekDayOpeningHours.timeSpans
                ]

            return opening_hours_dict
        return super().get(key, default)


class OpeningHoursModel(BaseModel):
    MONDAY: offers_schemas.TimeSpanListType
    TUESDAY: offers_schemas.TimeSpanListType
    WEDNESDAY: offers_schemas.TimeSpanListType
    THURSDAY: offers_schemas.TimeSpanListType
    FRIDAY: offers_schemas.TimeSpanListType
    SATURDAY: offers_schemas.TimeSpanListType
    SUNDAY: offers_schemas.TimeSpanListType

    @validator("*")
    def validate_time_spans_dont_overlap(
        cls, value: offers_schemas.TimeSpanListType
    ) -> offers_schemas.TimeSpanListType:
        offers_schemas.validate_time_spans_dont_overlap(value)
        return value


def _format_time(time_to_format: datetime.time) -> str:
    return time_to_format.strftime("%H:%M")


class GetEventOpeningHoursResponseModel(BaseModel):
    id: int
    startDatetime: datetime.datetime
    endDatetime: datetime.datetime | None
    openingHours: OpeningHoursModel

    class Config:
        orm_mode = True
        getter_dict = GetEventOpeningHoursResponseGetterDict
        json_encoders = {datetime.datetime: format_into_utc_date, datetime.time: _format_time}


class IndividualOfferResponseGetterDict(GetterDict):
    def get(self, key: str, default: Any | None = None) -> Any:
        if key == "extraData" and self._obj.product:
            self._obj.ean = self._obj.product.ean
        if key == "extraData" and self._obj.ean:
            extra_data_copy = self._obj.extraData.copy() if self._obj.extraData else {}
            extra_data_copy["ean"] = self._obj.ean
            return extra_data_copy
        if key == "eventOpeningHours":
            return next(
                (
                    eventOpeningHour
                    for eventOpeningHour in self._obj.eventOpeningHours
                    if not eventOpeningHour.isSoftDeleted
                ),
                None,
            )
        return super().get(key, default)


class IndividualOfferWithAddressResponseGetterDict(IndividualOfferResponseGetterDict):
    def get(self, key: str, default: Any | None = None) -> Any:
        if key == "address":
            return offer_address_getter_dict_helper(self._obj)
        if key == "isHeadlineOffer":
            return self._obj.is_headline_offer
        return super().get(key, default)


class GetIndividualOfferResponseModel(BaseModel, AccessibilityComplianceMixin):
    activeMediation: GetOfferMediationResponseModel | None
    bookingContact: str | None
    bookingsCount: int | None
    bookingEmail: str | None
    dateCreated: datetime.datetime
    publicationDate: datetime.datetime | None
    description: str | None
    durationMinutes: int | None
    extraData: Any
    hasBookingLimitDatetimesPassed: bool
    hasStocks: bool
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
    subcategoryId: SubcategoryIdEnum
    productId: int | None
    thumbUrl: str | None
    externalTicketOfficeUrl: str | None
    url: str | None
    venue: GetOfferVenueResponseModel
    withdrawalDelay: int | None
    withdrawalDetails: str | None
    withdrawalType: offers_models.WithdrawalTypeEnum | None
    status: OfferStatus
    isNonFreeOffer: bool | None
    eventOpeningHours: GetEventOpeningHoursResponseModel | None

    class Config:
        orm_mode = True
        json_encoders = {datetime.datetime: format_into_utc_date, datetime.time: _format_time}
        use_enum_values = True
        getter_dict = IndividualOfferResponseGetterDict


class GetActiveEANOfferResponseModel(BaseModel, AccessibilityComplianceMixin):
    dateCreated: datetime.datetime
    isActive: bool
    id: int
    name: str
    subcategoryId: SubcategoryIdEnum
    productId: int | None
    status: OfferStatus

    class Config:
        orm_mode = True
        json_encoders = {datetime.datetime: format_into_utc_date}
        use_enum_values = True
        getter_dict = IndividualOfferResponseGetterDict


class GetIndividualOfferWithAddressResponseModel(GetIndividualOfferResponseModel):
    address: AddressResponseIsLinkedToVenueModel | None
    hasPendingBookings: bool
    isHeadlineOffer: bool

    class Config:
        orm_mode = True
        json_encoders = {datetime.datetime: format_into_utc_date}
        use_enum_values = True
        getter_dict = IndividualOfferWithAddressResponseGetterDict


class GetStocksResponseModel(ConfiguredBaseModel):
    stocks: list[GetOfferStockResponseModel]
    stock_count: int
    has_stocks: bool

    class Config:
        json_encoders = {datetime.datetime: format_into_utc_date}


class StockStatsResponseModel(ConfiguredBaseModel):
    oldest_stock: datetime.datetime | None
    newest_stock: datetime.datetime | None
    stock_count: int | None
    remaining_quantity: int | None

    class Config:
        json_encoders = {datetime.datetime: format_into_utc_date}


class StocksQueryModel(BaseModel):
    date: datetime.date | None
    time: datetime.time | None
    price_category_id: int | None
    order_by: offers_repository.StocksOrderedBy = offers_repository.StocksOrderedBy.BEGINNING_DATETIME
    order_by_desc: bool = False
    page: int = Field(1, ge=1)
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
    price_categories: list[CreatePriceCategoryModel | EditPriceCategoryModel] = Field(
        max_items=offers_models.Offer.MAX_PRICE_CATEGORIES_PER_OFFER
    )

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


class MusicTypeResponse(BaseModel):
    gtl_id: str
    label: str
    canBeEvent: bool


class GetMusicTypesResponse(BaseModel):
    __root__: list[MusicTypeResponse]


class GetProductInformations(BaseModel):
    id: int
    name: str
    description: str | None
    subcategoryId: str
    gtl_id: str
    author: str
    performer: str
    images: dict

    @classmethod
    def from_orm(cls, product: offers_models.Product) -> "GetProductInformations":
        product.gtl_id = product.extraData.get("gtl_id", "") if product.extraData else ""
        product.author = product.extraData.get("author", "") if product.extraData else ""
        product.performer = product.extraData.get("performer", "") if product.extraData else ""
        return super().from_orm(product)

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True
