import datetime
import decimal
import ipaddress
import typing
from functools import partial
from typing import Annotated
from urllib import parse

import flask
import pydantic as pydantic_v2
import pydantic.v1 as pydantic_v1
import pytz
from pydantic.v1 import validator
from pydantic_core import PydanticCustomError

import pcapi.connectors.entreprise.api as api_entreprise
from pcapi.models.api_errors import ApiErrors
from pcapi.utils import date as date_utils
from pcapi.utils import phone_number as phone_number_utils

from .exceptions import PydanticError


NOW_LITERAL = typing.Literal["now"]


def to_camel(string: str) -> str:
    # used to define root level lists, see https://docs.pydantic.dev/1.10/usage/models/#custom-root-types
    if string == pydantic_v1.utils.ROOT_KEY:
        return pydantic_v1.utils.ROOT_KEY
    components = string.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def _is_email_error(error_message: str) -> bool:
    # email errors do not have an error_type, we must check the message directly
    return error_message.startswith("value is not a valid email address")


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
        "string_too_long": "Cette chaîne de caractères doit avoir une taille maximum de {max_length} caractères",
        "greater_than_equal": "Saisissez un nombre supérieur ou égal à {ge}",
        "less_than_equal": "Saisissez un nombre inférieur ou égal à {le}",
        "greater_than": "Saisissez un nombre supérieur à {gt}",
        "less_than": "Saisissez un nombre inférieur à {lt}",
        "too_short": "Cette liste doit avoir une taille minimum de {min_length}",
        "too_long": "Cette liste doit avoir une taille maximum de {max_length}",
        "model_attributes_type": "Format incorrect",
        "datetime_type": "Format de date invalide",
        "decimal_max_places": "Saisissez un nombre avec au maximum {decimal_places} décimales",
        "decimal_max_digits": "Saisissez un nombre avec au maximum {max_digits} chiffres au total",
        "extra_forbidden": "Vous ne pouvez pas changer cette information",
        "url_parsing": "L'URL est invalide",
        "url_scheme": "L'URL est invalide",
        "url_syntax_violation": "L'URL est invalide",
        "url_too_long": "L'URL est invalide",
        "url_type": "L'URL est invalide",
    }

    if pydantic_error and pydantic_error.errors():
        api_errors = ApiErrors()
        for error in pydantic_error.errors():
            if error["type"] in error_messages_by_error_type:
                message = error_messages_by_error_type[error["type"]].format(**error.get("ctx", {}))
            elif _is_email_error(error["msg"]):
                message = "Saisissez un email valide"
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


def check_date_in_future_v1(value: datetime.datetime | NOW_LITERAL | None) -> datetime.datetime | None:
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


def check_date_in_future_v2(value: datetime.datetime | NOW_LITERAL | None) -> datetime.datetime | None:
    if not value:
        return None
    if value == "now":
        return datetime.datetime.now(datetime.UTC)

    assert isinstance(value, datetime.datetime)  # to make mypy happy
    if value.tzinfo is None:
        raise PydanticError("The datetime must be timezone-aware.")
    no_tz_value = as_utc_without_timezone(value)
    if no_tz_value < datetime.datetime.now(datetime.UTC).replace(tzinfo=None):
        raise PydanticError("The datetime must be in the future.")
    return value


def check_date_in_future_and_remove_timezone_v1(value: datetime.datetime | NOW_LITERAL | None) -> datetime.datetime:
    if value == "now":
        return date_utils.get_naive_utc_now()

    assert isinstance(value, datetime.datetime)  # to make mypy happy

    if value.tzinfo is None:
        raise ValueError("The datetime must be timezone-aware.")
    no_tz_value = as_utc_without_timezone(value)
    if no_tz_value < date_utils.get_naive_utc_now():
        raise ValueError("The datetime must be in the future.")
    return no_tz_value


def check_date_in_future_and_remove_timezone_v2(value: datetime.datetime | NOW_LITERAL | None) -> datetime.datetime:
    if value == "now":
        return date_utils.get_naive_utc_now()

    assert isinstance(value, datetime.datetime)  # to make mypy happy

    if value.tzinfo is None:
        raise PydanticError("The datetime must be timezone-aware.")
    no_tz_value = as_utc_without_timezone(value)
    if no_tz_value < date_utils.get_naive_utc_now():
        raise PydanticError("The datetime must be in the future.")
    return no_tz_value


def check_url[T: (pydantic_v1.HttpUrl | pydantic_v2.HttpUrl | str | None)](
    value: T, pydantic_version: typing.Literal["v1"] | typing.Literal["v2"]
) -> T:
    ErrorClass = PydanticError if pydantic_version == "v2" else ValueError
    if not value:
        return value

    try:
        unquoted_url = parse.unquote(str(value))
    except Exception:
        raise ErrorClass("The url is invalid.")

    scheme, netloc, path, query, fragment = parse.urlsplit(unquoted_url)

    if "/../" in path:
        raise ErrorClass("Relative path are forbidden.")
    if not scheme or scheme.lower() not in ("https", "http"):
        raise ErrorClass("The protocol must be http:// or https://.")
    if not netloc:
        raise ErrorClass("Relative path are forbidden.")
    if "@" in netloc:
        raise ErrorClass("Authenticated urls are forbidden.")
    if "[" in netloc or "]" in netloc:
        raise ErrorClass("IP address are forbidden.")
    if "." not in netloc:
        raise ErrorClass("Top level domains are forbidden.")
    try:
        ipaddress.ip_address(netloc)
    except ValueError:
        pass
    else:
        raise ErrorClass("IP address are forbidden.")

    return value


def _check_datetime_in_future_and_format_to_utc_datetime(value: datetime.datetime) -> datetime.datetime:
    if value.tzinfo is None:
        raise PydanticError("The datetime must be timezone-aware.")
    if value < datetime.datetime.now(datetime.UTC):
        raise PydanticError("The datetime must be in the future.")
    return value.astimezone(datetime.UTC)


def validate_datetime(field_name: str, always: bool = False) -> classmethod:
    # TODO: (tcoudray-pass, 11/05/26) Should not accept `None` value
    def _check_if_not_none(value: datetime.datetime | NOW_LITERAL | None) -> datetime.datetime | None:
        if not value:
            return None
        return check_date_in_future_and_remove_timezone_v1(value)

    return pydantic_v1.validator(field_name, pre=False, allow_reuse=True, always=always)(_check_if_not_none)


def _validate_datetime(value: datetime.datetime) -> datetime.datetime:
    return check_date_in_future_and_remove_timezone_v2(value)


future_tz_aware_datetime = Annotated[datetime.datetime, pydantic_v2.AfterValidator(_validate_datetime)]
future_tz_aware_datetime_to_utc_datetime = Annotated[
    datetime.datetime,
    pydantic_v2.AfterValidator(_check_datetime_in_future_and_format_to_utc_datetime),
]


def validate_timezoned_datetime(field_name: str, always: bool = False) -> classmethod:
    return pydantic_v1.validator(field_name, pre=False, allow_reuse=True, always=always)(check_date_in_future_v1)


future_tz_aware_datetime_keep_tz = Annotated[datetime.datetime, pydantic_v2.AfterValidator(check_date_in_future_v2)]
future_tz_aware_datetime_or_now_keep_tz = Annotated[
    datetime.datetime | NOW_LITERAL, pydantic_v2.AfterValidator(check_date_in_future_v2)
]


def validate_phone_number(phone_number: str) -> str:
    try:
        return phone_number_utils.ParsedPhoneNumber(phone_number).phone_number
    except phone_number_utils.InvalidPhoneNumber:
        raise PydanticCustomError("invalid_phone_number", "Numéro de téléphone invalide")


def validate_phone_number_nullable(phone_number: str | None) -> str | None:
    if not phone_number:
        return None

    return validate_phone_number(phone_number)


def validate_url(field_name: str, always: bool = False) -> classmethod:
    validation_function = partial(check_url, pydantic_version="v1")
    return pydantic_v1.validator(field_name, pre=False, allow_reuse=True, always=always)(validation_function)


def parse_args_as_list(args: typing.Any) -> list[typing.Any] | None:
    if args is None or isinstance(args, list):
        return args

    return [args]


# use this validator for a query parameter that we need to parse as a list
ArgsAsListBeforeValidator = pydantic_v2.BeforeValidator(parse_args_as_list)


def _ensure_http_url(url: str) -> str:
    """Apply pydantic HttpUrl validation while still returning the original str"""
    pydantic_v2.TypeAdapter(pydantic_v2.HttpUrl).validate_python(url)
    return url


HttpUrlStr = typing.Annotated[str, pydantic_v2.AfterValidator(_ensure_http_url)]
ValidHttpUrl = typing.Annotated[
    pydantic_v2.HttpUrl, pydantic_v2.AfterValidator(partial(check_url, pydantic_version="v2"))
]
ValidHttpUrlStr = typing.Annotated[
    str,
    pydantic_v2.AfterValidator(_ensure_http_url),
    pydantic_v2.AfterValidator(partial(check_url, pydantic_version="v2")),
]

# by default a Decimal field will have number | string in the generated schema
# this allows us to keep only number
DecimalField = typing.Annotated[decimal.Decimal, pydantic_v2.WithJsonSchema({"type": "number"})]


def format_price(value: decimal.Decimal) -> decimal.Decimal:
    return value.quantize(decimal.Decimal("1.00"))


DecimalPrice = typing.Annotated[DecimalField, pydantic_v2.AfterValidator(format_price)]


def validate_siret(value: str) -> str:
    value = value.replace(" ", "")

    if not api_entreprise.is_valid_siret(value):
        raise PydanticError("Le SIRET est invalide")

    return value


SiretField = typing.Annotated[str, pydantic_v2.AfterValidator(validate_siret)]


# These three methods are used in legacy pydantic v1 models, do not use them for new code
def _validate_phone_number(number: str | None) -> str:
    try:
        parsed = phone_number_utils.parse_phone_number(number)
    except phone_number_utils.InvalidPhoneNumber:
        raise ValueError("Ce numéro de telephone ne semble pas valide")
    return phone_number_utils.get_formatted_phone_number(parsed)


def _validate_nullable_phone_number(number: str | None) -> str | None:
    if number is None:
        return None
    return _validate_phone_number(number)


def phone_number_validator(field_name: str, nullable: bool = False) -> classmethod:
    func = _validate_nullable_phone_number if nullable else _validate_phone_number
    return validator(field_name, allow_reuse=True)(func)
