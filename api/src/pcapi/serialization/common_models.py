from decimal import Decimal
from decimal import InvalidOperation
from typing import Annotated
from typing import Any

from pydantic import AfterValidator
from pydantic import BeforeValidator
from pydantic import Field

from pcapi.serialization.exceptions import PydanticError


MAX_LONGITUDE = 180
MAX_LATITUDE = 90


def format_coordinate(value: Any) -> Decimal:
    if not isinstance(value, (int, str, float, Decimal)):
        raise PydanticError("Format incorrect")

    try:
        decimal_value = Decimal(value).quantize(Decimal("1.00000"))
    except InvalidOperation:
        raise PydanticError("Format incorrect")

    return decimal_value


LatitudeDecimal = Annotated[Decimal, BeforeValidator(format_coordinate), Field(gt=-MAX_LATITUDE, lt=MAX_LATITUDE)]
LongitudeDecimal = Annotated[Decimal, BeforeValidator(format_coordinate), Field(gt=-MAX_LONGITUDE, lt=MAX_LONGITUDE)]

# prefer Decimal when possible
LatitudeFloat = Annotated[
    float, AfterValidator(format_coordinate), AfterValidator(float), Field(gt=-MAX_LATITUDE, lt=MAX_LATITUDE)
]
LongitudeFloat = Annotated[
    float, AfterValidator(format_coordinate), AfterValidator(float), Field(gt=-MAX_LONGITUDE, lt=MAX_LONGITUDE)
]
