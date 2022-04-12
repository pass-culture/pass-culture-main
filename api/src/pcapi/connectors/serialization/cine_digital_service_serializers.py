import datetime

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
