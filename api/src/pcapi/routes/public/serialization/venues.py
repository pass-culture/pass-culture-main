import datetime
import typing

import pydantic.v1 as pydantic_v1

from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.api import OffererVenues
from pcapi.routes import serialization
from pcapi.routes.public.documentation_constants.fields import fields
from pcapi.utils import date as date_utils

from .accessibility import PartialAccessibility
from .utils import StrEnum


VenueTypeEnum = StrEnum(  # type: ignore[call-overload]
    "VenueTypeEnum", {venue_type.name: venue_type.name for venue_type in offerers_models.VenueTypeCode}
)


class VenueDigitalLocation(serialization.ConfiguredBaseModel):
    type: typing.Literal["digital"] = "digital"


class VenuePhysicalLocation(serialization.ConfiguredBaseModel):
    address: str | None = pydantic_v1.Field(example="55 rue du Faubourg-Saint-Honoré")
    city: str | None = pydantic_v1.Field(example="Paris")
    postalCode: str | None = pydantic_v1.Field(example="75008")
    type: typing.Literal["physical"] = "physical"


class VenueResponse(serialization.ConfiguredBaseModel):
    id: int = fields.VENUE_ID
    siret_comment: str | None = fields.VENUE_SIRET_COMMENT
    siret: str | None = fields.VENUE_SIRET
    created_datetime: datetime.datetime = fields.VENUE_CREATED_DATETIME
    location: VenuePhysicalLocation | VenueDigitalLocation = fields.VENUE_LOCATION
    legal_name: str = fields.VENUE_LEGAL_NAME
    public_name: str | None = fields.VENUE_PUBLIC_NAME
    venue_type_code: VenueTypeEnum = fields.VENUE_ACTIVITY_DOMAIN  # type: ignore[valid-type]
    accessibility: PartialAccessibility

    @classmethod
    def build_model(cls, venue: offerers_models.Venue) -> "VenueResponse":
        return cls(
            siret_comment=venue.comment,
            created_datetime=venue.dateCreated,
            id=venue.id,
            location=(
                VenuePhysicalLocation(address=venue.street, city=venue.city, postalCode=venue.postalCode)
                if not venue.isVirtual
                else VenueDigitalLocation()
            ),
            legal_name=venue.name,
            public_name=venue.publicName,
            siret=venue.siret,
            venue_type_code=venue.venueTypeCode.name,
            accessibility=PartialAccessibility.from_orm(venue),
        )

    class Config:
        json_encoders = {datetime.datetime: date_utils.format_into_utc_date}


class OffererResponse(serialization.ConfiguredBaseModel):
    id: int
    dateCreated: datetime.datetime = pydantic_v1.Field(..., alias="createdDatetime")
    name: str = pydantic_v1.Field(example="Structure A")
    siren: str | None = pydantic_v1.Field(example="123456789")


class GetOffererVenuesResponse(serialization.ConfiguredBaseModel):
    offerer: OffererResponse = pydantic_v1.Field(
        ..., description="Offerer to which the venues belong. Entity linked to the api key used."
    )
    venues: list[VenueResponse]


class GetOfferersVenuesResponse(serialization.BaseModel):
    __root__: list[GetOffererVenuesResponse]

    class Config:
        json_encoders = {datetime.datetime: date_utils.format_into_utc_date}

    @classmethod
    def _serialize_offerer_venues(cls, row: OffererVenues) -> GetOffererVenuesResponse:
        venues = [VenueResponse.build_model(venue) for venue in row.venues]
        return GetOffererVenuesResponse(offerer=row.offerer, venues=venues)

    @classmethod
    def serialize_offerers_venues(
        cls,
        rows: typing.Iterable[OffererVenues],
    ) -> "GetOfferersVenuesResponse":
        offerers_venues = [cls._serialize_offerer_venues(row) for row in rows]
        return cls(__root__=offerers_venues)


class GetOfferersVenuesQuery(serialization.ConfiguredBaseModel):
    siren: str | None = pydantic_v1.Field(example="123456789", regex=r"^\d{9}$")
