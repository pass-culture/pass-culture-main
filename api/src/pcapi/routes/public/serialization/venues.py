import datetime
import typing

import pydantic.v1 as pydantic_v1

from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.api import OffererVenues
from pcapi.routes import serialization
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
    comment: str | None = pydantic_v1.Field(
        None, description="Applicable if siret is null and venue is physical.", alias="siretComment", example=None
    )
    dateCreated: datetime.datetime = pydantic_v1.Field(..., alias="createdDatetime")
    id: int
    location: VenuePhysicalLocation | VenueDigitalLocation = pydantic_v1.Field(
        ...,
        description="Location where the offers will be available or will take place. There is exactly one digital venue per offerer, which is listed although its id is not required to create a digital offer (see DigitalLocation model).",
        discriminator="type",
    )
    name: str = pydantic_v1.Field(alias="legalName", example="Palais de l'Élysée")
    publicName: str | None = pydantic_v1.Field(..., description="If null, legalName is used.", example="Élysée")
    siret: str | None = pydantic_v1.Field(
        description="Null when venue is digital or when siretComment field is not null.", example="12345678901234"
    )
    venueTypeCode: VenueTypeEnum = pydantic_v1.Field(alias="activityDomain")  # type: ignore[valid-type]
    accessibility: PartialAccessibility

    @classmethod
    def build_model(cls, venue: offerers_models.Venue) -> "VenueResponse":
        return cls(  # type: ignore[call-arg]
            comment=venue.comment,
            dateCreated=venue.dateCreated,
            id=venue.id,
            location=(
                VenuePhysicalLocation(address=venue.street, city=venue.city, postalCode=venue.postalCode)
                if not venue.isVirtual
                else VenueDigitalLocation()
            ),
            name=venue.name,
            publicName=venue.publicName,
            siret=venue.siret,
            venueTypeCode=venue.venueTypeCode.name,
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
