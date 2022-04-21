from datetime import datetime
from typing import Any
from typing import Dict
from typing import Optional

from pydantic import validator

from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import dehumanize_field
from pcapi.serialization.utils import humanize_field
from pcapi.serialization.utils import to_camel


class CollectiveStockIdResponseModel(BaseModel):
    id: str

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


class CollectiveStockCreationBodyModel(BaseModel):
    offer_id: int
    beginning_datetime: datetime
    booking_limit_datetime: Optional[datetime]
    total_price: float
    number_of_tickets: int
    educational_price_detail: Optional[str]

    _dehumanize_id = dehumanize_field("offer_id")

    @validator("number_of_tickets", pre=True)
    def validate_number_of_tickets(cls, number_of_tickets: int) -> int:  # pylint: disable=no-self-argument
        if number_of_tickets < 0:
            raise ValueError("Le nombre de places ne peut pas être négatif.")
        return number_of_tickets

    @validator("total_price", pre=True)
    def validate_price(cls, price: float) -> float:  # pylint: disable=no-self-argument
        if price < 0:
            raise ValueError("Le prix ne peut pas être négatif.")
        return price

    @validator("booking_limit_datetime")
    def validate_booking_limit_datetime(  # pylint: disable=no-self-argument
        cls, booking_limit_datetime: Optional[datetime], values: Dict[str, Any]
    ) -> Optional[datetime]:
        if booking_limit_datetime and booking_limit_datetime > values["beginning_datetime"]:
            raise ValueError("La date limite de réservation ne peut être postérieure à la date de début de l'évènement")
        return booking_limit_datetime

    @validator("educational_price_detail")
    def validate_price_detail(  # pylint: disable=no-self-argument
        cls, educational_price_detail: Optional[str]
    ) -> Optional[str]:
        if educational_price_detail and len(educational_price_detail) > 1000:
            raise ValueError("Le détail du prix ne doit pas excéder 1000 caractères.")
        return educational_price_detail

    class Config:
        alias_generator = to_camel
        extra = "forbid"
