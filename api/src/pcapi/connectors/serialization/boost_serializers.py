import datetime
from decimal import Decimal

import pydantic

import pcapi.core.external_bookings.models as external_bookings_models
from pcapi.routes.serialization import BaseModel


BOOST_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


class LoginBoost(BaseModel):
    code: int | None
    message: str
    token: str | None


class Film2(BaseModel):
    """We transcribe their API schema and keep their name convention"""

    id: int
    titleCnc: str
    numVisa: int
    posterUrl: str
    thumbUrl: str | None
    idFilmAllocine: int

    def to_generic_movie(self) -> external_bookings_models.Movie:
        return external_bookings_models.Movie(
            id=str(self.id),
            title=self.titleCnc,
            duration=1,  # FIXME
            description="",  # FIXME
            posterpath=self.posterUrl,
            visa=str(self.numVisa),
        )


class Collection(BaseModel):
    data: list
    message: str
    page: int
    previousPage: int
    nextPage: int
    totalPages: int
    totalCount: int


class FilmCollection(Collection):
    data: list[Film2]


def _convert_to_utc_datetime(datetime_with_tz_offset: datetime.datetime) -> datetime.datetime:
    return datetime_with_tz_offset.astimezone(tz=datetime.timezone.utc)


class ShowTime3(BaseModel):
    id: int


class ShowTimeCollection(Collection):
    data: list[ShowTime3]


class ShowtimePricing(BaseModel):
    id: int
    pricingCode: str
    amountTaxesIncluded: Decimal


class ShowTime(BaseModel):
    id: int
    numberRemainingSeatsForOnlineSale: int
    showDate: datetime.datetime
    showEndDate: datetime.datetime
    soldOut: bool
    authorizedAccess: bool
    film: Film2
    format: dict
    version: dict
    screen: dict
    showtimePricing: list[ShowtimePricing]

    @pydantic.validator("showDate", "showEndDate")
    def normalize_datetime(cls, value: datetime.datetime) -> datetime.datetime:
        return _convert_to_utc_datetime(value)


class ShowTimeDetails(BaseModel):
    message: str
    data: ShowTime
