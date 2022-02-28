from datetime import datetime
from typing import Dict
from typing import Optional

from pcapi import settings
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.repository import get_api_key_prefixes
from pcapi.core.offerers.repository import has_digital_venue_with_at_least_one_offer
from pcapi.core.offerers.repository import has_physical_venue_without_draft_or_accepted_bank_information
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization.venues_serialize import VenueStatsResponseModel
from pcapi.serialization.utils import humanize_field
from pcapi.utils.date import format_into_utc_date


class GetOffererVenueResponseModel(BaseModel):
    address: Optional[str]
    bookingEmail: Optional[str]
    businessUnitId: Optional[int]
    city: Optional[str]
    comment: Optional[str]
    departementCode: Optional[str]
    id: str
    isValidated: bool
    isVirtual: bool
    managingOffererId: str
    name: str
    postalCode: Optional[str]
    publicName: Optional[str]
    venueLabelId: Optional[str]
    withdrawalDetails: Optional[str]
    audioDisabilityCompliant: Optional[bool]
    mentalDisabilityCompliant: Optional[bool]
    motorDisabilityCompliant: Optional[bool]
    visualDisabilityCompliant: Optional[bool]
    _humanize_id = humanize_field("id")
    _humanize_managing_offerer_id = humanize_field("managingOffererId")
    _humanize_venue_label_id = humanize_field("venueLabelId")

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}


class OffererApiKey(BaseModel):
    maxAllowed: int
    prefixes: list[str]


class GetOffererResponseModel(BaseModel):
    address: Optional[str]
    apiKey: OffererApiKey
    bic: Optional[str]
    city: str
    dateCreated: datetime
    dateModifiedAtLastProvider: Optional[datetime]
    demarchesSimplifieesApplicationId: Optional[str]
    fieldsUpdated: list[str]
    hasDigitalVenueAtLeastOneOffer: bool
    hasMissingBankInformation: bool
    iban: Optional[str]
    id: str
    idAtProviders: Optional[str]
    isValidated: bool
    isActive: bool
    lastProviderId: Optional[str]
    managedVenues: list[GetOffererVenueResponseModel]
    name: str
    postalCode: str
    # FIXME (dbaty, 2020-11-09): optional until we populate the database (PC-5693)
    siren: Optional[str]

    _humanize_id = humanize_field("id")

    @classmethod
    def from_orm(cls, offerer: Offerer, venue_stats_by_ids: Optional[Dict[int, VenueStatsResponseModel]] = None):  # type: ignore
        offerer.apiKey = {
            "maxAllowed": settings.MAX_API_KEY_PER_OFFERER,
            "prefixes": get_api_key_prefixes(offerer.id),
        }
        if venue_stats_by_ids:
            for managedVenue in offerer.managedVenues:
                managedVenue.stats = venue_stats_by_ids[managedVenue.id]

        offerer.hasDigitalVenueAtLeastOneOffer = has_digital_venue_with_at_least_one_offer(offerer.id)
        offerer.hasMissingBankInformation = not offerer.demarchesSimplifieesApplicationId and (
            has_physical_venue_without_draft_or_accepted_bank_information(offerer.id)
            or offerer.hasDigitalVenueAtLeastOneOffer
        )
        return super().from_orm(offerer)

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}


class GetOffererNameResponseModel(BaseModel):
    id: str
    name: str

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


class GetOfferersNamesResponseModel(BaseModel):
    offerersNames: list[GetOffererNameResponseModel]

    class Config:
        orm_mode = True


class GetOfferersNamesQueryModel(BaseModel):
    validated: Optional[bool]
    validated_for_user: Optional[bool]

    class Config:
        extra = "forbid"


class GetEducationalOffererVenueResponseModel(BaseModel):
    address: Optional[str]
    city: Optional[str]
    id: str
    isVirtual: bool
    publicName: Optional[str]
    name: str
    postalCode: Optional[str]
    audioDisabilityCompliant: Optional[bool]
    mentalDisabilityCompliant: Optional[bool]
    motorDisabilityCompliant: Optional[bool]
    visualDisabilityCompliant: Optional[bool]
    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


class GetEducationalOffererResponseModel(BaseModel):
    id: str
    name: str
    managedVenues: list[GetEducationalOffererVenueResponseModel]

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


class GetEducationalOfferersResponseModel(BaseModel):
    educationalOfferers: list[GetEducationalOffererResponseModel]

    class Config:
        orm_mode = True


class GetEducationalOfferersQueryModel(BaseModel):
    offerer_id: Optional[str]

    class Config:
        extra = "forbid"


class GenerateOffererApiKeyResponse(BaseModel):
    apiKey: str


class CreateOffererQueryModel(BaseModel):
    address: Optional[str]
    city: str
    latitude: Optional[float]
    longitude: Optional[float]
    name: str
    postalCode: str
    siren: str

    class Config:
        extra = "forbid"
        anystr_strip_whitespace = True


class UserOffererResponseModel(BaseModel):
    id: str
    userId: str
    offererId: str

    _humanize_id = humanize_field("id")
    _humanize_user_id = humanize_field("userId")
    _humanize_offerer_id = humanize_field("offererId")

    class Config:
        orm_mode = True


class ListUserOfferersResponseModel(BaseModel):
    __root__: list[UserOffererResponseModel]


class GetOfferersResponseModel(BaseModel):
    id: str
    postalCode: str
    dateCreated: datetime
    name: str
    # FIXME (mageoffray, 2021-12-27): optional until we populate the database (PC-5693)
    siren: Optional[str]
    bic: Optional[str]
    iban: Optional[str]
    demarchesSimplifieesApplicationId: Optional[str]
    dateModifiedAtLastProvider: Optional[datetime]
    fieldsUpdated: list[str]
    idAtProviders: Optional[str]
    isActive: bool
    address: Optional[str]
    city: str
    isValidated: bool
    userHasAccess: bool
    dateValidated: Optional[datetime]
    lastProviderId: Optional[str]
    nOffers: int
    thumbCount: int
    managedVenues: list[GetOffererVenueResponseModel]

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


class GetOfferersListResponseModel(BaseModel):
    offerers: list[GetOfferersResponseModel]
    nbTotalResults: int


class GetOffererListQueryModel(BaseModel):
    keywords: Optional[str]
    page: Optional[int] = 0
    paginate: Optional[int] = 10
