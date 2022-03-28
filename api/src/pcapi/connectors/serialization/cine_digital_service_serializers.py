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
