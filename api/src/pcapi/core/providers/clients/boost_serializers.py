import datetime
from decimal import Decimal

import pydantic

from pcapi.core.offers import models as offers_models


class LoginBoost(pydantic.BaseModel):
    code: int | None = None
    message: str
    token: str | None = None


class Film2(pydantic.BaseModel):
    """We transcribe their API schema and keep their name convention"""

    id: int
    titleCnc: str
    numVisa: int
    posterUrl: str
    thumbUrl: str | None = None
    duration: int  # in minutes
    idFilmAllocine: int

    def to_generic_movie(self) -> offers_models.Movie:
        return offers_models.Movie(
            allocine_id=str(self.idFilmAllocine),
            description=None,
            duration=self.duration,
            extra_data=None,
            poster_url=self.posterUrl,
            title=self.titleCnc,
            visa=str(self.numVisa),
        )


class Collection(pydantic.BaseModel):
    data: list
    message: str
    page: int
    previousPage: int
    nextPage: int
    totalPages: int
    totalCount: int


def _convert_to_utc_datetime(datetime_with_tz_offset: datetime.datetime) -> datetime.datetime:
    """Convert the upcoming date information to utc before stripping it"""
    return datetime_with_tz_offset.astimezone(tz=datetime.timezone.utc).replace(tzinfo=None)


class ShowtimePricing(pydantic.BaseModel):
    id: int
    pricingCode: str
    amountTaxesIncluded: Decimal
    title: str


class ShowTime4(pydantic.BaseModel):
    """We transcribe their API schema and keep their name convention"""

    id: int
    numberSeatsRemaining: int
    showDate: datetime.datetime
    showEndDate: datetime.datetime
    film: Film2
    format: dict
    version: dict
    screen: dict
    showtimePricing: list[ShowtimePricing] = pydantic.Field(default_factory=list)
    attributs: list[int]

    @pydantic.field_validator("showDate", "showEndDate")
    def normalize_datetime(cls, value: datetime.datetime) -> datetime.datetime:
        return _convert_to_utc_datetime(value)


class ShowTimeCollection(Collection):
    data: list[ShowTime4]


class ShowTimeDetails(pydantic.BaseModel):
    message: str
    data: ShowTime4


class BasketItem(pydantic.BaseModel):
    idShowtimePricing: int
    quantity: int


class SaleRequest(pydantic.BaseModel):
    codePayment: str
    basketItems: list[BasketItem]
    idsBeforeSale: str | None = None


class Seat(pydantic.BaseModel):
    id: int | None = None
    code: str
    line: int
    numLine: int


class TicketResponse4(pydantic.BaseModel):
    id: int
    idCnc: int
    seat: Seat | None = None
    ticketReference: str


class SaleResponse3(pydantic.BaseModel):
    id: int
    code: str
    type: str
    amountTaxesIncluded: float | None = None
    tickets: list[TicketResponse4]


class SaleConfirmationResponse(pydantic.BaseModel):
    message: str
    data: SaleResponse3


class SalePreparation(pydantic.BaseModel):
    id: int
    idVendor: int
    idShowtime: int
    nbPlaceSelected: int
    placePrice: float
    pricingTitle: str | None = None
    reservation: str


class SalePreparationResponse(pydantic.BaseModel):
    message: str
    data: list[SalePreparation]


class SaleCancelItem(pydantic.BaseModel):
    code: str | None = None
    refundType: str


class SaleCancel(pydantic.BaseModel):
    sales: list[SaleCancelItem]


class CinemaAttribut(pydantic.BaseModel):
    id: int
    title: str


class CinemaAttributCollection(pydantic.BaseModel):
    data: list[CinemaAttribut]
