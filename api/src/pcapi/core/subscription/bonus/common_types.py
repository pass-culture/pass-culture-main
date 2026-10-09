"""
Prevent circular imports by extracting types common to this module
"""

import datetime
import typing

from pydantic import BeforeValidator


def _none_if_contains_placeholder(date_value: typing.Any) -> typing.Any:
    if isinstance(date_value, str) and "00-00" in date_value:
        return None
    return date_value


ApiParticulierDate = typing.Annotated[datetime.date | None, BeforeValidator(_none_if_contains_placeholder)]
