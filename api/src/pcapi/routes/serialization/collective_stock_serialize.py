import logging
from datetime import datetime
from typing import Any

from pydantic.v1 import Field
from pydantic.v1 import validator

from pcapi.core.educational import schemas as educational_schemas
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import to_camel
from pcapi.utils.date import format_into_utc_date


logger = logging.getLogger(__name__)


class CollectiveStockEditionBodyModel(BaseModel):
    startDatetime: datetime | None
    endDatetime: datetime | None
    bookingLimitDatetime: datetime | None
    price: float | None = Field(alias="totalPrice")
    numberOfTickets: int | None
    educationalPriceDetail: str | None

    _validate_number_of_tickets = educational_schemas.number_of_tickets_validator("numberOfTickets")
    _validate_total_price = educational_schemas.price_validator("price")
    _validate_educational_price_detail = educational_schemas.price_detail_validator("educationalPriceDetail")
    _validate_start_datetime = educational_schemas.start_datetime_validator("startDatetime")
    _validate_end_datetime = educational_schemas.end_datetime_validator("endDatetime")

    # FIXME (cgaunet, 2022-04-28): Once edit_collective_stock is not used by legacy code,
    # we can use the same interface as for creation and thus reuse the validator defined above.
    @validator("bookingLimitDatetime")
    def validate_booking_limit_datetime(
        cls, booking_limit_datetime: datetime | None, values: dict[str, Any]
    ) -> datetime | None:
        if (
            booking_limit_datetime
            and values.get("startDatetime") is not None
            and booking_limit_datetime > values["startDatetime"]
        ):
            raise ValueError("La date limite de réservation ne peut être postérieure à la date de début de l'évènement")
        return booking_limit_datetime

    # FIXME (cgaunet, 2022-04-28): Once edit_collective_stock is not used by legacy code,
    # we can use the same interface as for creation and thus reuse the validator defined above.
    @validator("endDatetime")
    def validate_end_limit_datetime(cls, endDatetime: datetime | None, values: dict[str, Any]) -> datetime | None:
        startDatetime = values.get("startDatetime")
        if endDatetime is None:
            raise ValueError("La date de fin de l'évènement ne peut pas être nulle.")
        if startDatetime and endDatetime < startDatetime:
            raise ValueError("La date de fin de l'évènement ne peut précéder la date de début.")
        return endDatetime

    # FIXME (cgaunet, 2022-04-28): Once edit_collective_stock is not used by legacy code,
    # we can use the same interface as for creation and thus reuse the validator defined above.
    @validator("startDatetime", pre=True)
    def validate_start_limit_datetime(cls, startDatetime: datetime | None) -> datetime | None:
        if startDatetime is None:
            raise ValueError("La date de début de l'évènement ne peut pas être nulle.")
        return startDatetime

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class CollectiveStockResponseModel(BaseModel):
    id: int
    startDatetime: datetime | None
    endDatetime: datetime | None
    bookingLimitDatetime: datetime | None
    price: float
    numberOfTickets: int | None
    priceDetail: str | None = Field(alias="educationalPriceDetail")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: format_into_utc_date}
        orm_mode = True
