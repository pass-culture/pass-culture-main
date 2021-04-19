from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from pcapi.serialization.utils import humanize_field
from pcapi.utils.date import format_into_utc_date


class GetOffererVenueResponseModel(BaseModel):
    address: Optional[str]
    bic: Optional[str]
    bookingEmail: Optional[str]
    city: Optional[str]
    comment: Optional[str]
    dateCreated: datetime
    dateModifiedAtLastProvider: Optional[datetime]
    demarchesSimplifieesApplicationId: Optional[str]
    departementCode: Optional[str]
    iban: Optional[str]
    id: str
    idAtProviders: Optional[str]
    isValidated: bool
    isVirtual: bool
    lastProviderId: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    managingOffererId: str
    name: str
    nOffers: int
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


class GetOffererResponseModel(BaseModel):
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
    managedVenues: list[GetOffererVenueResponseModel]
    name: str
    nOffers: int
    postalCode: str
    # FIXME (dbaty, 2020-11-09): optional until we populate the database (PC-5693)
    siren: Optional[str]

    _humanize_id = humanize_field("id")

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
