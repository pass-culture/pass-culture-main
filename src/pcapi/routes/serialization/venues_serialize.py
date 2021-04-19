from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from pcapi.domain.venue.venue_with_offerer_name.venue_with_offerer_name import VenueWithOffererName
from pcapi.serialization.utils import humanize_field
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize


def serialize_venues_with_offerer_name(venues: list[VenueWithOffererName]) -> list[dict]:
    return [serialize_venue_with_offerer_name(venue) for venue in venues]


def serialize_venue_with_offerer_name(venue: VenueWithOffererName) -> dict:
    return {
        "id": humanize(venue.identifier),
        "managingOffererId": humanize(venue.managing_offerer_identifier),
        "name": venue.name,
        "offererName": venue.offerer_name,
        "publicName": venue.public_name,
        "isVirtual": venue.is_virtual,
        "bookingEmail": venue.booking_email,
    }


class VenueStatsResponseModel(BaseModel):
    activeBookingsQuantity: int
    validatedBookingsQuantity: int
    activeOffersCount: int
    soldOutOffersCount: int


class GetVenueManagingOffererResponseModel(BaseModel):
    address: Optional[str]
    bic: Optional[str]
    city: str
    dateCreated: datetime
    dateModifiedAtLastProvider: Optional[datetime]
    demarchesSimplifieesApplicationId: Optional[str]
    fieldsUpdated: list[str]
    iban: Optional[str]
    id: str
    idAtProviders: Optional[str]
    isValidated: bool
    lastProviderId: Optional[str]
    name: str
    postalCode: str
    # FIXME (dbaty, 2020-11-09): optional until we populate the database (PC-5693)
    siren: Optional[str]

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}


class GetVenueResponseModel(BaseModel):
    address: Optional[str]
    bic: Optional[str]
    bookingEmail: Optional[str]
    city: Optional[str]
    comment: Optional[str]
    dateCreated: datetime
    dateModifiedAtLastProvider: Optional[datetime]
    demarchesSimplifieesApplicationId: Optional[str]
    departementCode: Optional[str]
    fieldsUpdated: list[str]
    iban: Optional[str]
    id: str
    idAtProviders: Optional[str]
    isValidated: bool
    isVirtual: bool
    lastProviderId: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    managingOfferer: GetVenueManagingOffererResponseModel
    managingOffererId: str
    name: str
    postalCode: Optional[str]
    publicName: Optional[str]
    siret: Optional[str]
    venueLabelId: Optional[str]
    venueTypeId: Optional[str]

    _humanize_id = humanize_field("id")
    _humanize_managing_offerer_id = humanize_field("managingOffererId")
    _humanize_venue_label_id = humanize_field("venueLabelId")
    _humanize_venue_type_id = humanize_field("venueTypeId")

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}
