import datetime
import typing

import flask
import pydantic
import pytz

from pcapi.models.api_errors import ApiErrors
from pcapi.utils import human_ids


def to_camel(string: str) -> str:
    components = string.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def before_handler(
    request: flask.Request,  # pylint: disable=unused-argument
    response: flask.Response,  # pylint: disable=unused-argument
    pydantic_error: pydantic.ValidationError | None,
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


def humanize_id(id_to_humanize: int | str | None) -> str | None:
    if id_to_humanize is None:
        return None

    # This is because humanize_id will be called on a int the first time
    # and then on ids already humanized. humanize can't work with string
    if isinstance(id_to_humanize, int):
        return human_ids.humanize(id_to_humanize)

    return str(id_to_humanize)


def dehumanize_id(id_to_dehumanize: int | str | None) -> int | None:
    if id_to_dehumanize is None:
        return None

    # This is because dehumanize_id will be called on a str the first time
    # and then on ids already dehumanized. dehumanize can't work with int
    if isinstance(id_to_dehumanize, str):
        return human_ids.dehumanize(id_to_dehumanize)

    return int(id_to_dehumanize)


def check_string_is_not_empty(string: str) -> str:
    if not string or string.isspace():
        raise pydantic.MissingError()

    return string


# No functools.partial here as it has no __name__ and threfore is not compatible with pydantic
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
        raise pydantic.ValidationError("La valeur reçu doit être soit 'true' soit 'false'")  # type: ignore [call-arg]


def humanize_field(field_name: str) -> classmethod:
    return pydantic.validator(field_name, pre=True, allow_reuse=True)(humanize_id)


def dehumanize_field(field_name: str) -> classmethod:
    return pydantic.validator(field_name, pre=True, allow_reuse=True)(dehumanize_id)


def dehumanize_list_field(field_name: str) -> classmethod:
    return pydantic.validator(field_name, pre=True, allow_reuse=True)(human_ids.dehumanize_ids_list)


def validate_not_empty_string_when_provided(field_name: str) -> classmethod:
    return pydantic.validator(field_name, pre=True, allow_reuse=True)(check_string_is_not_empty)


def string_to_boolean_field(field_name: str) -> classmethod:
    return pydantic.validator(field_name, pre=True, allow_reuse=True)(string_to_boolean)


def string_length_validator(field_name: str, *, length: int) -> classmethod:
    return pydantic.validator(field_name, pre=False, allow_reuse=True)(check_string_length_wrapper(length=length))


def as_utc_without_timezone(d: datetime.datetime) -> datetime.datetime:
    # FIXME (dbaty, 2020-11-25): We need this ugly workaround because
    # the api users send us datetimes like "2020-12-03T14:00:00Z"
    # (note the "Z" suffix). Pydantic deserializes it as a datetime
    # *with* a timezone. However, datetimes are stored in the database
    # as UTC datetimes *without* any timezone. We need to remove the timezone to prevent from errors like:
    # - wrongly detection of a change for a datetime field
    # - we compare this "timezone aware" datetime with another one that is not
    return d.astimezone(pytz.utc).replace(tzinfo=None)


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
    return pydantic.validator(field_name, pre=False, allow_reuse=True)(check_date_in_future_and_remove_timezone)
