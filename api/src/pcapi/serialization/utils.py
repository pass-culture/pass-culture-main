import datetime
import typing
from functools import partial

import flask
import pydantic as pydantic_v2
import pydantic.v1 as pydantic_v1
import pytz

from pcapi.models.api_errors import ApiErrors
from pcapi.utils import date as date_utils
from pcapi.utils.date import get_naive_utc_now

from .exceptions import PydanticError


NOW_LITERAL = typing.Literal["now"]


def to_camel(string: str) -> str:
    # used to define root level lists, see https://docs.pydantic.dev/1.10/usage/models/#custom-root-types
    if string == pydantic_v1.utils.ROOT_KEY:
        return pydantic_v1.utils.ROOT_KEY
    components = string.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def before_handler(
    _request: flask.Request,
    _response: flask.Response,
    pydantic_error: pydantic_v1.ValidationError | pydantic_v2.ValidationError | None,
    _: typing.Any,
) -> None:
    """Raises an ``ApiErrors` exception if input validation fails.

    This handler is automatically called through the ``spectree_serialize()`` decorator.
    """
    error_messages_by_error_type = {
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
        # pydantic V2
        "missing": "Ce champ est obligatoire",
        "int_parsing": "Saisissez un entier valide",
        "int_type": "Saisissez un entier valide",
        "float_parsing": "Saisissez un nombre valide",
        "string_type": "Saisissez une chaîne de caractères valide",
        "string_too_short": "Cette chaîne de caractères doit avoir une taille minimum de {min_length} caractères",
        "greater_than_equal": "Saisissez un nombre supérieur ou égal à {ge}",
    }

    # pydantic V2 is not precise enough on error_types so for some errors
    # we must use the message for translation mapping
    error_messages_by_message = {
        "value is not a valid email address: An email address must have an @-sign.": "Saisissez un email valide",
    }

    if pydantic_error and pydantic_error.errors():
        api_errors = ApiErrors()
        for error in pydantic_error.errors():
            if error["type"] in error_messages_by_error_type:
                message = error_messages_by_error_type[error["type"]].format(**error.get("ctx", {}))
            elif error["msg"] in error_messages_by_message:
                message = error_messages_by_message[error["msg"]].format(**error.get("ctx", {}))
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


def check_date_in_future(value: datetime.datetime | NOW_LITERAL | None) -> datetime.datetime | None:
    if not value:
        return None
    if value == "now":
        return datetime.datetime.now(datetime.UTC)

    assert isinstance(value, datetime.datetime)  # to make mypy happy
    if value.tzinfo is None:
        raise ValueError("The datetime must be timezone-aware.")
    no_tz_value = as_utc_without_timezone(value)
    if no_tz_value < datetime.datetime.now(datetime.UTC).replace(tzinfo=None):
        raise ValueError("The datetime must be in the future.")
    return value


# TODO(jbaudet-09/2025) remove once database models uses timezone
# aware columns. Migrate to `check_date_in_future`.
def check_date_in_future_and_remove_timezone(
    value: datetime.datetime | NOW_LITERAL | None,
    pydantic_version: typing.Literal["v1"] | typing.Literal["v2"],
) -> datetime.datetime | None:
    ErrorClass = PydanticError if pydantic_version == "v2" else ValueError
    if not value:
        return None

    if value == "now":
        return get_naive_utc_now()

    assert isinstance(value, datetime.datetime)  # to make mypy happy

    if value.tzinfo is None:
        raise ErrorClass("The datetime must be timezone-aware.")
    no_tz_value = as_utc_without_timezone(value)
    if no_tz_value < date_utils.get_naive_utc_now():
        raise ErrorClass("The datetime must be in the future.")
    return no_tz_value


def validate_datetime(field_name: str, always: bool = False) -> classmethod:
    return pydantic_v1.validator(field_name, pre=False, allow_reuse=True, always=always)(
        partial(check_date_in_future_and_remove_timezone, pydantic_version="v1")
    )


def validate_timezoned_datetime(field_name: str, always: bool = False) -> classmethod:
    return pydantic_v1.validator(field_name, pre=False, allow_reuse=True, always=always)(check_date_in_future)


def parse_args_as_list(args: typing.Any) -> list[typing.Any] | None:
    if args is None or isinstance(args, list):
        return args

    return [args]


# use this validator for a query parameter that we need to parse as a list
args_as_list_validator = pydantic_v2.BeforeValidator(parse_args_as_list)
