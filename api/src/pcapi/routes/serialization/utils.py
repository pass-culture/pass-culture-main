import typing

from pydantic_core import InitErrorDetails
from pydantic_core import ValidationError

from pcapi.serialization.exceptions import PydanticError


def raise_error_from_location(invalid_value: typing.Any, loc: str, msg: str) -> None:
    """
    To raise a located validation error inside a pydantic model.

    Useful to locate error raised by a `@pydantic_v2.model_validator`.
    By default, the error raised inside a `model_validator` has no location.
    (see https://github.com/pydantic/pydantic/issues/9686#issuecomment-2301754693)

    :param invalid_value: Value causing the error
    :param loc: Wich field has caused the error (for instance: `name`, `email`...)
    :param msg: Error message
    """
    raise ValidationError.from_exception_data(
        f"{loc.capitalize()}Error",
        [
            InitErrorDetails(
                type=PydanticError(msg),
                loc=(loc,),
                input=invalid_value,
                ctx={loc: invalid_value, "error": msg},
            )
        ],
    )
