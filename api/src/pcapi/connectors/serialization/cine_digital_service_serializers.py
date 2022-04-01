import datetime
from typing import Dict
from typing import Optional

from pydantic import Field

from pcapi.routes.serialization import BaseModel


class IdObjectCDS(BaseModel):
    id: int


class ShowTariffCDS(BaseModel):
    tariff: IdObjectCDS = Field(alias="tariffid")

    class Config:
        allow_population_by_field_name = True


class ShowCDS(BaseModel):
    id: int
    is_cancelled: bool = Field(alias="canceled")
    is_deleted: bool = Field(alias="deleted")
    is_disabled_seatmap: bool = Field(alias="disableseatmap")
    internet_remaining_place: int = Field(alias="internetremainingplace")
    showtime: datetime.datetime
    shows_tariff_pos_type_collection: list[ShowTariffCDS] = Field(alias="showsTariffPostypeCollection")
    screen: IdObjectCDS = Field(alias="screenid")

    class Config:
        allow_population_by_field_name = True


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
    tariff: Optional[TariffCDS] = Field(alias="tariffid")

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
    seat_col: Optional[int] = Field(alias="seatcol")
    seat_row: Optional[int] = Field(alias="seatrow")
    seat_number: Optional[str] = Field(alias="seatnumber")
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
    seat_number: Optional[str] = Field(alias="seatnumber")

    class Config:
        allow_population_by_field_name = True


class CreateTransactionResponseCDS(BaseModel):
    id: int
    invoice_id: str = Field(alias="invoiceid")
    tickets: list[TicketResponseCDS]

    class Config:
        allow_population_by_field_name = True
