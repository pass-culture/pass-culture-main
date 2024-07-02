import datetime
import typing

import flask
import pydantic.v1 as pydantic_v1
import pytz

from pcapi.models.api_errors import ApiErrors


def to_camel(string: str) -> str:
    # used to define root level lists, see https://docs.pydantic.dev/1.10/usage/models/#custom-root-types
    if string == pydantic_v1.utils.ROOT_KEY:
        return pydantic_v1.utils.ROOT_KEY
    components = string.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def before_handler(
    _request: flask.Request,
    _response: flask.Response,
    pydantic_error: pydantic_v1.ValidationError | None,
    _: typing.Any,
) -> None:
    """Raises an ``ApiErrors` exception if input validation fails.

    This handler is automatically called through the ``spectree_serialize()`` decorator.
    """
    error_messages = {
        "type_error.decimal": "Saisissez un nombre valide",
        "type_error.integer": "Saisissez un nombre valide",
        "type_error.none.not_allowed": "Ce champ ne peut pas être nul",
        "value_error.datetime": "Format de date invalide",
        "value_error.extra": "Vous ne pouvez pas changer cette information",
        "value_error.missing": "Ce champ est obligatoire",
        "value_error.url.scheme": 'L\'URL doit commencer par "http://" ou "https://"',
        "value_error.url.host": 'L\'URL doit terminer par une extension (ex. ".fr")',
        "value_error.email": "Le format d'email est incorrect.",
        "value_error.number.not_gt": "Saisissez un nombre supérieur à {limit_value}",
        "value_error.number.not_ge": "Saisissez un nombre supérieur ou égal à {limit_value}",
        "value_error.decimal.not_finite": "La valeur n'est pas un nombre décimal valide",
    }

    if pydantic_error and pydantic_error.errors():
        api_errors = ApiErrors()
        for error in pydantic_error.errors():
            if error["type"] in error_messages:
                message = error_messages[error["type"]].format(**error.get("ctx", {}))
            else:
                message = error["msg"]

            location = ".".join(str(loc) for loc in error["loc"])
            api_errors.add_error(location, message)
        raise api_errors


def public_api_before_handler(
    _request: flask.Request,
    _response: flask.Response,
    pydantic_error: pydantic_v1.ValidationError | None,
    _: typing.Any,
) -> None:
    """Raises an ``ApiErrors` exception if input validation fails.

    This handler is automatically called through the ``spectree_serialize()`` decorator.
    This decorator doesn't translate errors to french since it is used for public APIs.
    """

    if pydantic_error and pydantic_error.errors():
        api_errors = ApiErrors()
        for error in pydantic_error.errors():
            message = error["msg"]
            location = ".".join(str(loc) for loc in error["loc"])
            api_errors.add_error(location, message)
        raise api_errors


def check_string_is_not_empty(string: str) -> str:
    if not string or string.isspace():
        raise pydantic_v1.MissingError()

    return string


# No functools.partial here as it has no __name__ and therefore is not compatible with pydantic
def check_string_length_wrapper(length: int) -> typing.Callable:
    def check_string_length(string: str) -> str:
        if string and len(string) > length:
            raise ValueError(f"Le champ doit faire moins de {length} caractères")
        return string

    return check_string_length


def string_to_boolean(string: str) -> bool | None:
    try:
        return {"true": True, "false": False}[string]
    except KeyError:
        raise ValueError("La valeur reçu doit être soit 'true' soit 'false'")


def validate_not_empty_string_when_provided(field_name: str) -> classmethod:
    return pydantic_v1.validator(field_name, pre=True, allow_reuse=True)(check_string_is_not_empty)


def string_to_boolean_field(field_name: str) -> classmethod:
    return pydantic_v1.validator(field_name, pre=True, allow_reuse=True)(string_to_boolean)


def string_length_validator(field_name: str, *, length: int) -> classmethod:
    return pydantic_v1.validator(field_name, pre=False, allow_reuse=True)(check_string_length_wrapper(length=length))


def as_utc_without_timezone(d: datetime.datetime) -> datetime.datetime:
    # We need this ugly workaround because
    # the api users send us datetimes like "2020-12-03T14:00:00Z"
    # (note the "Z" suffix). Pydantic deserializes it as a datetime
    # *with* a timezone. However, datetimes are stored in the database
    # as UTC datetimes *without* any timezone. We need to remove the timezone to prevent from errors like:
    # - wrongly detection of a change for a datetime field
    # - we compare this "timezone aware" datetime with another one that is not
    #
    # Warning:
    # this function might add an offset when converting to UTC.
    return d.astimezone(pytz.utc).replace(tzinfo=None)


def without_timezone(d: datetime.datetime) -> datetime.datetime:
    """Copy input without timezone information

    The day, hour, etc. are copied without any translation regarding
    the original timezone.
    """
    return datetime.datetime(d.year, d.month, d.day, d.hour, d.minute, d.second, d.microsecond)


def check_date_in_future_and_remove_timezone(value: datetime.datetime | None) -> datetime.datetime | None:
    if not value:
        return None
    if value.tzinfo is None:
        raise ValueError("The datetime must be timezone-aware.")
    no_tz_value = as_utc_without_timezone(value)
    if no_tz_value < datetime.datetime.utcnow():
        raise ValueError("The datetime must be in the future.")
    return no_tz_value


def validate_datetime(field_name: str) -> classmethod:
    return pydantic_v1.validator(field_name, pre=False, allow_reuse=True)(check_date_in_future_and_remove_timezone)
