import datetime
from typing import Dict

from pydantic import Field

import pcapi.core.booking_providers.models as booking_providers_models
from pcapi.routes.serialization import BaseModel


class IdObjectCDS(BaseModel):
    id: int


class ShowTariffCDS(BaseModel):
    tariff: IdObjectCDS = Field(alias="tariffid")

    class Config:
        allow_population_by_field_name = True


class CinemasCDS(BaseModel):
    id: str
    is_internet_sale_gauge_active: bool = Field(alias="internetsalegaugeactive")

    class Config:
        allow_population_by_field_name = True


class ShowCDS(BaseModel):
    id: int
    is_cancelled: bool = Field(alias="canceled")
    is_deleted: bool = Field(alias="deleted")
    is_disabled_seatmap: bool = Field(alias="disableseatmap")
    remaining_place: int = Field(alias="remainingplace")
    internet_remaining_place: int = Field(alias="internetremainingplace")
    showtime: datetime.datetime
    shows_tariff_pos_type_collection: list[ShowTariffCDS] = Field(alias="showsTariffPostypeCollection")
    screen: IdObjectCDS = Field(alias="screenid")
    media: IdObjectCDS = Field(alias="mediaid")

    class Config:
        allow_population_by_field_name = True


class MediaCDS(BaseModel):
    id: int
    title: str
    duration: int  # CDS api returns duration in seconds
    posterpath: str | None
    storyline: str
    visanumber: str

    class Config:
        allow_population_by_field_name = True

    def to_generic_movie(self) -> booking_providers_models.Movie:
        return booking_providers_models.Movie(
            id=str(self.id),
            title=self.title,
            duration=self.duration // 60,
            description=self.storyline,
            posterpath=self.posterpath,
            visa=self.visanumber,
        )


class PaymentTypeCDS(BaseModel):
    id: int
    internal_code: str = Field(alias="internalcode")
    is_active: bool = Field(alias="active")

    class Config:
        allow_population_by_field_name = True


class TariffCDS(BaseModel):
    id: int
    price: float
    is_active: bool = Field(alias="active")
    label: str = Field(alias="labeltariff")

    class Config:
        allow_population_by_field_name = True


class VoucherTypeCDS(BaseModel):
    id: int
    code: str
    tariff: TariffCDS | None = Field(alias="tariffid")

    class Config:
        allow_population_by_field_name = True


class ScreenCDS(BaseModel):
    id: int
    seatmap_front_to_back: bool = Field(alias="seatmapfronttoback")
    seatmap_left_to_right: bool = Field(alias="seatmaplefttoright")
    seatmap_skip_missing_seats: bool = Field(alias="seatmapskipmissingseats")

    class Config:
        allow_population_by_field_name = True


class SeatmapCDS(BaseModel):
    __root__: list[list[int]]

    @property
    def map(self) -> list[list[int]]:
        return self.__root__

    @property
    def nb_row(self) -> int:
        return len(self.map)

    @property
    def nb_col(self) -> int:
        return len(self.map[0]) if len(self.map[0]) > 0 else 0


class CancelBookingCDS(BaseModel):
    barcodes: list[int]
    paiement_type_id: int = Field(alias="paiementtypeid")


class CancelBookingsErrorsCDS(BaseModel):
    __root__: Dict[str, str]


class TicketSaleCDS(BaseModel):
    id: int
    cinema_id: str = Field(alias="cinemaid")
    operation_date: str = Field(alias="operationdate")
    is_cancelled: bool = Field(alias="canceled")
    seat_col: int | None = Field(alias="seatcol")
    seat_row: int | None = Field(alias="seatrow")
    seat_number: str | None = Field(alias="seatnumber")
    tariff: IdObjectCDS = Field(alias="tariffid")
    show: IdObjectCDS = Field(alias="showid")
    disabled_person: bool = Field(alias="disabledperson")

    class Config:
        allow_population_by_field_name = True


class TransactionPayementCDS(BaseModel):
    id: int
    amount: float
    payement_type: IdObjectCDS = Field(alias="paiementtypeid")
    voucher_type: IdObjectCDS = Field(alias="vouchertypeid")

    class Config:
        allow_population_by_field_name = True


class CreateTransactionBodyCDS(BaseModel):
    cinema_id: str = Field(alias="cinemaid")
    transaction_date: str = Field(alias="transactiondate")
    is_cancelled: bool = Field(alias="canceled")
    ticket_sale_collection: list[TicketSaleCDS] = Field(alias="ticketsaleCollection")
    payement_collection: list[TransactionPayementCDS] = Field(alias="paiementCollection")

    class Config:
        allow_population_by_field_name = True


class TicketResponseCDS(BaseModel):
    barcode: str
    seat_number: str | None = Field(alias="seatnumber")

    class Config:
        allow_population_by_field_name = True


class CreateTransactionResponseCDS(BaseModel):
    id: int
    invoice_id: str = Field(alias="invoiceid")
    tickets: list[TicketResponseCDS]

    class Config:
        allow_population_by_field_name = True


class SeatCDS:
    def __init__(self, seat_location_indices: tuple[int, int], screen_infos: ScreenCDS, seat_map: SeatmapCDS):
        self.seatRow = seat_location_indices[0] + 1
        self.seatCol = seat_location_indices[1] + 1
        if not screen_infos.seatmap_front_to_back:
            self.seatRow = seat_map.nb_row - seat_location_indices[0]
        if not screen_infos.seatmap_left_to_right:
            self.seatCol = seat_map.nb_col - seat_location_indices[1]

        if screen_infos.seatmap_skip_missing_seats:
            seat_row_array = seat_map.map[seat_location_indices[0]]
            previous_seats = (
                seat_row_array[: seat_location_indices[1]]
                if screen_infos.seatmap_left_to_right
                else seat_row_array[seat_location_indices[1] :]
            )
            skipped_seat = sum(1 for seat_value in previous_seats if seat_value == 0)
            self.seatCol -= skipped_seat

        seat_letter = chr(ord("A") + self.seatRow - 1)
        self.seatNumber = f"{seat_letter}_{self.seatCol}"
