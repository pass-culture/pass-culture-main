from datetime import date
from datetime import datetime
import enum
import typing

import flask
from pydantic import EmailStr
from pydantic import Field
from pydantic import root_validator
from pydantic import validator
from pydantic.types import constr

from pcapi.core.categories.subcategories import SubcategoryIdEnum
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.educational.models import StudentLevels
from pcapi.core.offerers.models import Venue
from pcapi.core.offers import validation as offers_validation
from pcapi.core.offers.serialize import CollectiveOfferType
from pcapi.models.feature import FeatureToggle
from pcapi.models.offer_mixin import OfferStatus
from pcapi.routes.native.v1.serialization.common_models import AccessibilityComplianceMixin
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import base as base_serializers
from pcapi.routes.serialization.educational_institutions import EducationalInstitutionResponseModel
from pcapi.serialization.utils import dehumanize_field
from pcapi.serialization.utils import humanize_field
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize
from pcapi.utils.image_conversion import CropParams
from pcapi.validation.routes.offers import check_collective_offer_name_length_is_valid


T_GetCollectiveOfferBaseResponseModel = typing.TypeVar(
    "T_GetCollectiveOfferBaseResponseModel", bound="GetCollectiveOfferBaseResponseModel"
)


class ListCollectiveOffersQueryModel(BaseModel):
    nameOrIsbn: str | None
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


class CollectiveOffersStockResponseModel(BaseModel):
    id: str
    hasBookingLimitDatetimePassed: bool
    offerId: str
    remainingQuantity: int | str
    beginningDatetime: datetime | None
    bookingLimitDatetime: datetime | None

    @validator("remainingQuantity", pre=True)
    def validate_remaining_quantity(cls, remainingQuantity: int | str) -> int | str:
        if remainingQuantity and remainingQuantity != "0" and not isinstance(remainingQuantity, int):
            return remainingQuantity.lstrip("0")
        return remainingQuantity


class EducationalRedactorResponseModel(BaseModel):
    email: str | None
    firstName: str | None
    lastName: str | None
    civility: str | None

    class Config:
        orm_mode = True


class CollectiveOffersBookingResponseModel(BaseModel):
    id: str
    booking_status: str


class CollectiveOfferResponseModel(BaseModel):
    hasBookingLimitDatetimesPassed: bool
    id: str
    nonHumanizedId: int
    isActive: bool
    isEditable: bool
    isEducational: bool
    name: str
    stocks: list[CollectiveOffersStockResponseModel]
    booking: CollectiveOffersBookingResponseModel | None
    subcategoryId: SubcategoryIdEnum
    isShowcase: bool
    venue: base_serializers.ListOffersVenueResponseModel
    status: str
    venueId: str
    educationalInstitution: EducationalInstitutionResponseModel | None
    interventionArea: list[str]
    templateId: str | None
    imageCredit: str | None
    imageUrl: str | None
    isPublicApi: bool


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
    last_booking = (
        _get_serialize_last_booking(offer.collectiveStock.collectiveBookings)
        if isinstance(offer, CollectiveOffer) and offer.collectiveStock
        else None
    )
    serialized_stocks = [serialized_stock] if serialized_stock is not None else []
    is_offer_template = isinstance(offer, CollectiveOfferTemplate)
    institution = getattr(offer, "institution", None)
    templateId = getattr(offer, "templateId", None)

    return CollectiveOfferResponseModel(  # type: ignore [call-arg]
        hasBookingLimitDatetimesPassed=offer.hasBookingLimitDatetimesPassed if not is_offer_template else False,  # type: ignore [arg-type]
        id=humanize(offer.id),  # type: ignore [arg-type]
        nonHumanizedId=offer.id,
        isActive=False if offer.status == OfferStatus.INACTIVE else offer.isActive,
        isEditable=offer.isEditable,
        isEducational=True,
        name=offer.name,
        stocks=serialized_stocks,  # type: ignore [arg-type]
        booking=last_booking,
        thumbUrl=None,
        subcategoryId=offer.subcategoryId,  # type: ignore [arg-type]
        venue=_serialize_venue(offer.venue),  # type: ignore [arg-type]
        venueId=humanize(offer.venue.id),  # type: ignore [arg-type]
        status=offer.status.name,  # type: ignore [attr-defined]
        isShowcase=is_offer_template,
        offerId=humanize(offer.offerId),
        educationalInstitution=EducationalInstitutionResponseModel.from_orm(institution) if institution else None,
        interventionArea=offer.interventionArea,
        templateId=templateId,
        imageCredit=offer.imageCredit,
        imageUrl=offer.imageUrl,
        isPublicApi=offer.isPublicApi if not is_offer_template else False,
    )


def _serialize_stock(offer_id: int, stock: CollectiveStock | None = None) -> dict:
    if stock:
        return {
            "id": humanize(stock.id),
            "nonHumanizedId": stock.id,
            "offerId": humanize(offer_id),
            "hasBookingLimitDatetimePassed": stock.hasBookingLimitDatetimePassed,
            "remainingQuantity": 0 if stock.isSoldOut else 1,
            "beginningDatetime": stock.beginningDatetime,
            "bookingLimitDatetime": stock.bookingLimitDatetime,
        }
    return {
        "id": humanize(0),
        "offerId": humanize(offer_id),
        "hasBookingLimitDatetimePassed": False,
        "remainingQuantity": 1,
        "beginningDatetime": datetime(year=2030, month=1, day=1),
        "bookingLimitDatetime": datetime(year=2030, month=1, day=1),
    }


def _serialize_venue(venue: Venue) -> dict:
    return {
        "id": humanize(venue.id),
        "nonHumanizedId": venue.id,
        "isVirtual": venue.isVirtual,
        "managingOffererId": humanize(venue.managingOffererId),
        "name": venue.name,
        "offererName": venue.managingOfferer.name,
        "publicName": venue.publicName,
        "departementCode": venue.departementCode,
    }


def _get_serialize_last_booking(bookings: list[CollectiveBooking]) -> CollectiveOffersBookingResponseModel | None:
    if len(bookings) == 0:
        return None
    last_booking = sorted(bookings, key=lambda b: b.dateCreated, reverse=True)[0]
    return CollectiveOffersBookingResponseModel(
        id=last_booking.id,  # type: ignore [arg-type]
        booking_status=last_booking.status.value,
    )


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
    nonHumanizedId: int
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
    nonHumanizedId: int
    idAtProviders: str | None
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
    venueId: int | None

    @validator("venueId", pre=True)
    def validate_venueId(cls, venue_id: str | int | None) -> int | None:
        if isinstance(venue_id, int):
            return venue_id
        if not venue_id:
            return None
        return dehumanize(venue_id)


class GetCollectiveOfferCollectiveStockResponseModel(BaseModel):
    id: str
    nonHumanizedId: int
    isSoldOut: bool = Field(alias="isBooked")
    is_cancellable_from_offerer: bool = Field(alias="isCancellable")
    beginningDatetime: datetime | None
    bookingLimitDatetime: datetime | None
    price: float
    numberOfTickets: int | None
    priceDetail: str | None = Field(alias="educationalPriceDetail")
    isEditable: bool = Field(alias="isEducationalStockEditable")

    _humanize_id = humanize_field("id")

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}


class GetCollectiveOfferBaseResponseModel(BaseModel, AccessibilityComplianceMixin):
    id: str
    bookingEmails: list[str]
    dateCreated: datetime
    description: str
    durationMinutes: int | None
    students: list[StudentLevels]
    offerVenue: CollectiveOfferOfferVenueResponseModel
    contactEmail: str
    contactPhone: str | None
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
    is_cancellable_from_offerer: bool = Field(alias="isCancellable")
    imageCredit: str | None
    imageUrl: str | None

    _humanize_id = humanize_field("id")
    _humanize_offerId = humanize_field("offerId")
    _humanize_venue_id = humanize_field("venueId")

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}
        use_enum_values = True


class GetCollectiveOfferTemplateResponseModel(GetCollectiveOfferBaseResponseModel):
    priceDetail: str | None = Field(alias="educationalPriceDetail")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class GetCollectiveOfferRequestResponseModel(BaseModel):
    email: str
    requestedDate: date | None
    totalStudents: int | None
    totalTeachers: int | None
    phoneNumber: str | None
    comment: str

    class Config:
        allow_population_by_field_name = True


class GetCollectiveOfferResponseModel(GetCollectiveOfferBaseResponseModel):
    isBookable: bool
    collectiveStock: GetCollectiveOfferCollectiveStockResponseModel | None
    institution: EducationalInstitutionResponseModel | None
    isVisibilityEditable: bool
    templateId: str | None
    lastBookingStatus: CollectiveBookingStatus | None
    lastBookingId: int | None
    teacher: EducationalRedactorResponseModel | None
    _humanize_templateId = humanize_field("templateId")
    isPublicApi: bool

    @classmethod
    def from_orm(cls, offer: CollectiveOffer) -> "GetCollectiveOfferResponseModel":
        result = super().from_orm(offer)

        if result.status == OfferStatus.INACTIVE.name:
            result.isActive = False

        return result


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
    venueId: int | None

    class Config:
        alias_generator = to_camel
        extra = "forbid"


def is_intervention_area_valid(
    intervention_area: list[str] | None,
    offer_venue: CollectiveOfferVenueBodyModel | None,
) -> bool:
    if intervention_area is None:
        return False

    if offer_venue is not None and offer_venue.addressType == OfferAddressType.OFFERER_VENUE:
        return True

    if len(intervention_area) == 0:
        return False

    return True


class PostCollectiveOfferBodyModel(BaseModel):
    venue_id: int
    subcategory_id: str
    name: str
    booking_emails: list[str]
    description: str
    domains: list[int] | None
    duration_minutes: int | None
    audio_disability_compliant: bool = False
    mental_disability_compliant: bool = False
    motor_disability_compliant: bool = False
    visual_disability_compliant: bool = False
    students: list[StudentLevels]
    offer_venue: CollectiveOfferVenueBodyModel
    contact_email: EmailStr
    contact_phone: str | None
    intervention_area: list[str] | None
    template_id: int | None
    offerer_id: str | None  # FIXME (MathildeDuboille - 24/10/22) prevent bug in production where offererId is sent in params

    @validator("name", pre=True)
    def validate_name(cls, name: str) -> str:
        check_collective_offer_name_length_is_valid(name)
        return name

    @validator("students")
    def validate_students(cls, students: list[StudentLevels]) -> list[StudentLevels]:
        # FIXME (rpa - 06/02/23) remove this validator when removing the Feature Flag
        if not FeatureToggle.WIP_ADD_CLG_6_5_COLLECTIVE_OFFER.is_active():
            results = []
            for student in students:
                if student in (StudentLevels.COLLEGE5, StudentLevels.COLLEGE6):
                    continue
                results.append(student)
            if not results:
                raise ValueError("Les offres EAC ne sont pas encore ouvertes aux 6eme et 5eme.")
            return results
        return students

    @root_validator
    def validate_domains(cls, values: dict) -> dict:
        domains = values.get("domains")
        is_from_template = bool(values.get("template_id", None))
        if not domains and not is_from_template:
            raise ValueError("domains must have at least one value")
        return values

    @root_validator
    def validate_intervention_area(cls, values: dict) -> dict:
        intervention_area = values.get("intervention_area", None)
        is_from_template = bool(values.get("template_id", None))
        offer_venue = values.get("offer_venue", None)
        if not is_intervention_area_valid(intervention_area, offer_venue) and not is_from_template:
            raise ValueError("intervention_area must have at least one value")
        return values

    @root_validator
    def validate_booking_emails(cls, values: dict) -> dict:
        booking_emails = values.get("booking_emails", [])
        is_from_template = bool(values.get("template_id", None))
        if not booking_emails:
            if is_from_template:
                values["booking_emails"] = [values["contact_email"]]
            else:
                raise ValueError("Un email doit etre renseigné")
        return values

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class PostCollectiveOfferTemplateBodyModel(PostCollectiveOfferBodyModel):
    if typing.TYPE_CHECKING:
        price_detail: str | None
    else:
        price_detail: constr(max_length=1000) | None

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class CollectiveOfferTemplateBodyModel(BaseModel):
    price_detail: str | None = Field(alias="educationalPriceDetail")

    @validator("price_detail")
    def validate_price_detail(cls, price_detail: str | None) -> str | None:
        if price_detail and len(price_detail) > 1000:
            raise ValueError("Le détail du prix ne doit pas excéder 1000 caractères.")
        return price_detail

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class CollectiveOfferTemplateResponseIdModel(BaseModel):
    id: str
    nonHumanizedId: int

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class PatchCollectiveOfferBodyModel(BaseModel, AccessibilityComplianceMixin):
    bookingEmails: list[str] | None
    description: str | None
    name: str | None
    students: list[StudentLevels] | None
    offerVenue: CollectiveOfferVenueBodyModel | None
    contactEmail: EmailStr | None
    contactPhone: str | None
    durationMinutes: int | None
    subcategoryId: SubcategoryIdEnum | None
    domains: list[int] | None
    interventionArea: list[str] | None
    venueId: int | None

    @validator("name", allow_reuse=True)
    def validate_name(cls, name: str | None) -> str | None:
        assert name is not None and name.strip() != ""
        check_collective_offer_name_length_is_valid(name)
        return name

    @validator("students")
    def validate_students(cls, students: list[StudentLevels]) -> list[StudentLevels]:
        # FIXME (rpa - 06/02/23) remove this validator when removing the Feature Flag
        if students and not FeatureToggle.WIP_ADD_CLG_6_5_COLLECTIVE_OFFER.is_active():
            results = []
            for student in students:
                if student in (StudentLevels.COLLEGE5, StudentLevels.COLLEGE6):
                    continue
                results.append(student)
            if not results:
                raise ValueError("Les offres EAC ne sont pas encore ouvertes aux 6eme et 5eme.")
            return results
        return students

    @validator("description", allow_reuse=True)
    def validate_description(cls, description: str | None) -> str | None:
        if description is None:
            raise ValueError("Description cannot be NULL.")
        return description

    @validator("domains")
    def validate_domains_collective_offer_edition(
        cls,
        domains: list[int] | None,
    ) -> list[int] | None:
        if domains is None or (domains is not None and len(domains) == 0):
            raise ValueError("domains must have at least one value")

        return domains

    @validator("interventionArea")
    def validate_intervention_area_not_empty_when_specified(
        cls,
        intervention_area: list[str] | None,
        values: dict,
    ) -> list[str] | None:
        if not is_intervention_area_valid(intervention_area, values.get("offerVenue", None)):
            raise ValueError("interventionArea must have at least one value")

        return intervention_area

    @validator("bookingEmails")
    def validate_booking_emails(cls, booking_emails: list[str]) -> list[str]:
        if not booking_emails:
            raise ValueError("Un email doit etre renseigné.")
        return booking_emails

    @validator("venueId", allow_reuse=True)
    def validate_venue_id(cls, venue_id: int | None) -> int | None:
        if venue_id is None:
            raise ValueError("venue_id cannot be NULL.")
        return venue_id

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class PatchCollectiveOfferTemplateBodyModel(PatchCollectiveOfferBodyModel):
    priceDetail: str | None
    domains: list[int] | None

    @validator("priceDetail")
    def validate_price_detail(cls, price_detail: str | None) -> str | None:
        if price_detail and len(price_detail) > 1000:
            raise ValueError("Le détail du prix ne doit pas excéder 1000 caractères.")
        return price_detail

    @validator("domains")
    def validate_domains_collective_offer_template_edition(
        cls,
        domains: list[int] | None,
    ) -> list[int] | None:
        if domains is not None and len(domains) == 0:
            raise ValueError("domains must have at least one value")

        return domains

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class PatchCollectiveOfferActiveStatusBodyModel(BaseModel):
    is_active: bool
    ids: list[int]

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
    teacher_email: str | None

    class Config:
        alias_generator = to_camel
        extra = "allow"


class AttachImageFormModel(BaseModel):
    credit: str
    cropping_rect_x: float
    cropping_rect_y: float
    cropping_rect_height: float
    cropping_rect_width: float

    class Config:
        alias_generator = to_camel

    @property
    def crop_params(self) -> CropParams:
        return CropParams.build(
            x_crop_percent=self.cropping_rect_x,
            y_crop_percent=self.cropping_rect_y,
            height_crop_percent=self.cropping_rect_height,
            width_crop_percent=self.cropping_rect_width,
        )

    def get_image_as_bytes(self, request: flask.Request) -> bytes:
        """
        Get the image from the POSTed data (request)
        Only the max size is checked at this stage, and possibly the content type header
        """
        if "thumb" in request.files:
            blob = request.files["thumb"]
            image_as_bytes = blob.read()
            offers_validation.check_image_size(image_as_bytes)
            return image_as_bytes

        raise offers_validation.exceptions.MissingImage()


class AttachImageResponseModel(BaseModel):
    imageUrl: str

    class Config:
        orm_mode = True
