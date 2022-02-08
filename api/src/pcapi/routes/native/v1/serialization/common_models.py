from decimal import Decimal
from typing import Optional

from pcapi.routes.serialization import BaseModel


class Coordinates(BaseModel):
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]
