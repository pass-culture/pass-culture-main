import datetime
import typing

import pydantic

from pcapi.core.offerers import models as offerers_models
from pcapi.routes import serialization
from pcapi.utils import date as date_utils

from .accessibility import PartialAccessibility
from .utils import StrEnum


VenueTypeEnum = StrEnum(  # type: ignore [call-overload]
    "VenueTypeEnum", {venue_type.name: venue_type.name for venue_type in offerers_models.VenueTypeCode}
)


class VenueDigitalLocation(serialization.ConfiguredBaseModel):
    type: typing.Literal["digital"] = "digital"


class VenuePhysicalLocation(serialization.ConfiguredBaseModel):
    address: str | None = pydantic.Field(example="55 rue du Faubourg-Saint-Honoré")
    city: str | None = pydantic.Field(example="Paris")
    postalCode: str | None = pydantic.Field(example="75008")
    type: typing.Literal["physical"] = "physical"


class VenueResponse(serialization.ConfiguredBaseModel):
    comment: str | None = pydantic.Field(
        None, description="Applicable if siret is null and venue is physical.", alias="siretComment", example=None
    )
    dateCreated: datetime.datetime = pydantic.Field(..., alias="createdDatetime")
    id: int
    location: VenuePhysicalLocation | VenueDigitalLocation = pydantic.Field(
        ...,
        description="Location where the offers will be available or will take place. There is exactly one digital venue per offerer, which is listed although its id is not required to create a digital offer (see DigitalLocation model).",
        discriminator="type",
    )
    name: str = pydantic.Field(alias="legalName", example="Palais de l'Élysée")
    publicName: str | None = pydantic.Field(..., description="If null, legalName is used.", example="Élysée")
    siret: str | None = pydantic.Field(
        description="Null when venue is digital or when siretComment field is not null.", example="12345678901234"
    )
    venueTypeCode: VenueTypeEnum = pydantic.Field(alias="activityDomain")  # type: ignore [valid-type]
    accessibility: PartialAccessibility

    @classmethod
    def build_model(cls, venue: offerers_models.Venue) -> "VenueResponse":
        return cls(
            comment=venue.comment,
            dateCreated=venue.dateCreated,
            id=venue.id,
            location=VenuePhysicalLocation(address=venue.address, city=venue.city, postalCode=venue.postalCode)
            if not venue.isVirtual
            else VenueDigitalLocation(),
            name=venue.name,
            publicName=venue.publicName,
            siret=venue.siret,
            venueTypeCode=venue.venueTypeCode.name,
            accessibility=PartialAccessibility.from_orm(venue),
        )

    class Config:
        json_encoders = {datetime.datetime: date_utils.format_into_utc_date}
