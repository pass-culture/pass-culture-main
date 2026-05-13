import datetime
import typing

import pydantic
from pydantic import Field

import pcapi.core.offers.models as offers_models


class CineOfficeBaseModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(validate_by_name=True)


class IdObject(CineOfficeBaseModel):
    id: int


class ShowTariff(CineOfficeBaseModel):
    tariff: IdObject = Field(alias="tariffid")


class ShowsMediaOptions(CineOfficeBaseModel):
    media_options_id: IdObject = Field(alias="mediaoptionsid")


class CinemaParameter(CineOfficeBaseModel):
    id: int
    key: str
    value: str | None = None


class CinemaCDS(CineOfficeBaseModel):
    id: str
    is_internet_sale_gauge_active: bool = Field(alias="internetsalegaugeactive")
    cinema_parameters: list[CinemaParameter] = Field(alias="cinemaParameters", default_factory=list)


class MediaOptionCDS(CineOfficeBaseModel):
    id: int
    ticketlabel: str | None = None
    label: str


class Show(CineOfficeBaseModel):
    id: int
    is_cancelled: bool = Field(alias="canceled")
    is_deleted: bool = Field(alias="deleted")
    is_disabled_seatmap: bool = Field(alias="disableseatmap")
    is_empty_seatmap: str | bool = Field(alias="seatmap")
    remaining_place: int = Field(alias="remainingplace")
    internet_remaining_place: int = Field(alias="internetremainingplace")
    showtime: datetime.datetime
    shows_tariff_pos_type_collection: list[ShowTariff] = Field(alias="showsTariffPostypeCollection")
    screen: IdObject = Field(alias="screenid")
    media: IdObject = Field(alias="mediaid")
    shows_mediaoptions_collection: list[ShowsMediaOptions] = Field(alias="showsMediaoptionsCollection")

    @pydantic.field_validator("is_empty_seatmap")
    def string_with_no_digit_to_true(cls, value: str | bool) -> bool:
        """
        2022/08/02 a seatmap should be similar to [[1,1,1,0],[1,1,1,0]]
        when empty, it can be "[[],[]]" or ""
        """
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if not any(char.isdigit() for char in value):
                return True
        return False


class Media(CineOfficeBaseModel):
    id: int
    title: str
    duration: int | None = None  # CDS api returns duration in seconds
    posterpath: str | None = None
    storyline: str | None = None
    visanumber: str | None = None
    allocineid: str | None = None

    def to_generic_movie(self) -> offers_models.Movie:
        return offers_models.Movie(
            allocine_id=str(self.allocineid) if self.allocineid else None,
            duration=self.duration // 60 if self.duration else None,
            description=self.storyline,
            extra_data=None,
            poster_url=self.posterpath,
            title=self.title,
            visa=self.visanumber,
        )


class PaymentTypeCDS(CineOfficeBaseModel):
    id: int
    internal_code: str = Field(alias="internalcode")
    is_active: bool = Field(alias="active")


class Tariff(CineOfficeBaseModel):
    id: int
    price: float
    is_active: bool = Field(alias="active")
    label: str = Field(alias="labeltariff")


class VoucherType(CineOfficeBaseModel):
    id: int
    code: str | None = None
    tariff: Tariff | None = Field(alias="tariffid", default=None)


class Screen(CineOfficeBaseModel):
    id: int
    seatmap_front_to_back: bool = Field(alias="seatmapfronttoback")
    seatmap_left_to_right: bool = Field(alias="seatmaplefttoright")
    seatmap_skip_missing_seats: bool = Field(alias="seatmapskipmissingseats")


class Seatmap(pydantic.RootModel, CineOfficeBaseModel):
    root: list[list[int]]

    @property
    def map(self) -> list[list[int]]:
        return self.root

    @property
    def nb_row(self) -> int:
        return len(self.map)

    @property
    def nb_col(self) -> int:
        return len(self.map[0]) if len(self.map[0]) > 0 else 0


class CancelBooking(CineOfficeBaseModel):
    barcodes: list[int]
    paiement_type_id: int = Field(alias="paiementtypeid")


class CancelBookingsErrors(pydantic.RootModel, CineOfficeBaseModel):
    root: dict[str, str]


class TicketSale(CineOfficeBaseModel):
    id: int
    cinema_id: str = Field(alias="cinemaid")
    operation_date: str = Field(alias="operationdate")
    is_cancelled: bool = Field(alias="canceled")
    seat_col: int | None = Field(alias="seatcol", default=None)
    seat_row: int | None = Field(alias="seatrow", default=None)
    seat_number: str | None = Field(alias="seatnumber", default=None)
    tariff: IdObject = Field(alias="tariffid")
    voucher_type: str = Field(alias="vouchertype")
    show: IdObject = Field(alias="showid")
    disabled_person: bool = Field(alias="disabledperson")


class TransactionPayement(CineOfficeBaseModel):
    id: int
    amount: float
    payement_type: IdObject = Field(alias="paiementtypeid")
    voucher_type: IdObject = Field(alias="vouchertypeid")


class CreateTransactionBody(CineOfficeBaseModel):
    cinema_id: str = Field(alias="cinemaid")
    transaction_date: str = Field(alias="transactiondate")
    is_cancelled: bool = Field(alias="canceled")
    ticket_sale_collection: list[TicketSale] = Field(alias="ticketsaleCollection")
    payement_collection: list[TransactionPayement] = Field(alias="paiementCollection")


class TicketResponse(CineOfficeBaseModel):
    barcode: str
    seat_number: str | None = Field(alias="seatnumber", default=None)


class CreateTransactionResponse(CineOfficeBaseModel):
    id: int
    invoice_id: str = Field(alias="invoiceid")
    tickets: list[TicketResponse]


class Seat:
    def __init__(
        self,
        seat_location_indices: tuple[int, int],
        screen_infos: Screen,
        seat_map: Seatmap,
        hardcoded_seatmap: list[list[str | typing.Literal[0]]],
    ):
        self.seatRow = seat_location_indices[0]
        self.seatCol = seat_location_indices[1]
        if hardcoded_seatmap:
            self.seatNumber = hardcoded_seatmap[self.seatRow][self.seatCol]
            assert isinstance(self.seatNumber, str)  # cannot be zero (int)
        else:
            seat_number_row = self.seatRow
            seat_number_col = self.seatCol
            if not screen_infos.seatmap_front_to_back:
                seat_number_row = seat_map.nb_row - seat_location_indices[0] - 1
            if not screen_infos.seatmap_left_to_right:
                seat_number_col = seat_map.nb_col - seat_location_indices[1] - 1

            if screen_infos.seatmap_skip_missing_seats:
                # Skip missing seats only to count seat column number
                seat_row_array = seat_map.map[seat_location_indices[0]]
                previous_col_seats = (
                    seat_row_array[: seat_location_indices[1]]
                    if screen_infos.seatmap_left_to_right
                    else seat_row_array[seat_location_indices[1] :]
                )

                skipped_col_seats = sum(1 for seat_value in previous_col_seats if seat_value == 0)
                seat_number_col -= skipped_col_seats

            previous_rows = (
                seat_map.map[: seat_location_indices[0]]
                if screen_infos.seatmap_front_to_back
                else seat_map.map[seat_location_indices[0] :]
            )
            skipped_rows = 0
            for row_seats in previous_rows:
                if all(seat == 0 for seat in row_seats):
                    skipped_rows += 1
            seat_number_row -= skipped_rows

            seat_letter = chr(ord("A") + seat_number_row)
            self.seatNumber = f"{seat_letter}_{seat_number_col + 1}"
