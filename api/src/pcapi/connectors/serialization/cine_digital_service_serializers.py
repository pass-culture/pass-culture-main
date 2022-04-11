import datetime
from typing import Dict

from pydantic import Field

from pcapi.routes.serialization import BaseModel


class ShowCDS(BaseModel):
    id: int
    is_cancelled: bool = Field(alias="canceled")
    is_deleted: bool = Field(alias="deleted")
    internet_remaining_place: int = Field(alias="internetremainingplace")
    showtime: datetime.datetime

    class Config:
        allow_population_by_field_name = True


class PaymentTypeCDS(BaseModel):
    id: int
    is_active: bool = Field(alias="active")
    short_label: str = Field(alias="shortlabel")

    class Config:
        allow_population_by_field_name = True


class TariffCDS(BaseModel):
    id: int
    price: float
    is_active: bool = Field(alias="active")
    label: str = Field(alias="labeltariff")

    class Config:
        allow_population_by_field_name = True


class ScreenCDS(BaseModel):
    id: int
    seatmap_front_to_back: bool = Field(alias="seatmapfronttoback")
    seatmap_left_to_right: bool = Field(alias="seatmaplefttoright")
    seatmap_skip_missing_seats: bool = Field(alias="seatmapskipmissingseats")


class CancelBookingCDS(BaseModel):
    barcodes: list[str]
    paiement_type_id: int = Field(alias="paiementtypeid")


class CancelBookingsErrorsCDS(BaseModel):
    __root__: Dict[str, str]
