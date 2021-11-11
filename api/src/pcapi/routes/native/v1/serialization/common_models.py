from decimal import Decimal
from typing import Optional

from . import BaseModel


class Coordinates(BaseModel):
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]
