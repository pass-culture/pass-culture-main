import datetime
from decimal import Decimal

import pydantic.v1 as pydantic_v1

import pcapi.core.external_bookings.models as external_bookings_models
from pcapi.routes.serialization import BaseModel


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
    duration: int  # in minutes
    idFilmAllocine: int

    def to_generic_movie(self) -> external_bookings_models.Movie:
        return external_bookings_models.Movie(
            id=str(self.id),
            title=self.titleCnc,
            duration=self.duration,
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


def _convert_to_utc_datetime(datetime_with_tz_offset: datetime.datetime) -> datetime.datetime:
    """Convert the upcoming date information to utc before stripping it"""
    return datetime_with_tz_offset.astimezone(tz=datetime.timezone.utc).replace(tzinfo=None)


class ShowtimePricing(BaseModel):
    id: int
    pricingCode: str
    amountTaxesIncluded: Decimal
    title: str


class ShowTime4(BaseModel):
    """We transcribe their API schema and keep their name convention"""

    id: int
    numberSeatsRemaining: int
    showDate: datetime.datetime
    showEndDate: datetime.datetime
    film: Film2
    format: dict
    version: dict
    screen: dict
    showtimePricing: list[ShowtimePricing] = pydantic_v1.Field(default_factory=list)
    attributs: list[int]

    @pydantic_v1.validator("showDate", "showEndDate")
    def normalize_datetime(cls, value: datetime.datetime) -> datetime.datetime:
        return _convert_to_utc_datetime(value)


class ShowTimeCollection(Collection):
    data: list[ShowTime4]


class ShowTimeDetails(BaseModel):
    message: str
    data: ShowTime4


class BasketItem(BaseModel):
    idShowtimePricing: int
    quantity: int


class SaleRequest(BaseModel):
    codePayment: str
    basketItems: list[BasketItem]
    idsBeforeSale: str | None


# FIXME(fseguin, 2022-11-08: waiting for the specs)
class Seat(BaseModel):
    id: int | None
    code: str
    line: int
    numLine: int


class TicketResponse4(BaseModel):
    id: int
    idCnc: int
    seat: Seat | None
    ticketReference: str


class SaleResponse3(BaseModel):
    id: int
    code: str
    type: str
    amountTaxesIncluded: float | None
    tickets: list[TicketResponse4]


class SaleConfirmationResponse(BaseModel):
    message: str
    data: SaleResponse3


class SalePreparation(BaseModel):
    id: int
    idVendor: int
    idShowtime: int
    nbPlaceSelected: int
    placePrice: float
    pricingTitle: str | None
    reservation: str


class SalePreparationResponse(BaseModel):
    message: str
    data: list[SalePreparation]


class SaleCancelItem(BaseModel):
    code: str | None
    refundType: str


class SaleCancel(BaseModel):
    sales: list[SaleCancelItem]


class CinemaAttribut(BaseModel):
    id: int
    title: str


class CinemaAttributCollection(BaseModel):
    data: list[CinemaAttribut]
