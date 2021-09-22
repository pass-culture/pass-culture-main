from datetime import datetime
from typing import Dict
from typing import Optional

from pydantic import BaseModel

from pcapi import settings
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.repository import get_api_key_prefixes
from pcapi.core.offerers.repository import has_digital_venue_with_at_least_one_offer
from pcapi.core.offerers.repository import has_physical_venue_without_draft_or_accepted_bank_information
from pcapi.routes.serialization.venues_serialize import VenueStatsResponseModel
from pcapi.serialization.utils import humanize_field
from pcapi.utils.date import format_into_utc_date


class GetOffererVenueResponseModel(BaseModel):
    address: Optional[str]
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
    venueTypeId: Optional[str]
    _humanize_id = humanize_field("id")
    _humanize_managing_offerer_id = humanize_field("managingOffererId")
    _humanize_venue_label_id = humanize_field("venueLabelId")
    _humanize_venue_type_id = humanize_field("venueTypeId")

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
