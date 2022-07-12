import re
from typing import Any
from typing import Callable

from flask import Request
from flask import Response
from pydantic import MissingError
from pydantic import ValidationError
from pydantic import validator

from pcapi.models.api_errors import ApiErrors
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import dehumanize_ids_list
from pcapi.utils.human_ids import humanize


def to_camel(string: str) -> str:
    components = string.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def before_handler(
    request: Request,  # pylint: disable=unused-argument
    response: Response,  # pylint: disable=unused-argument
    pydantic_error: ValidationError | None,
    _: Any,
) -> None:
    """Raises an ``ApiErrors` exception if input validation fails.

    This handler is automatically called through the ``spectree_serialize()`` decorator.
    """
    error_messages = {
        "type_error.integer": "Saisissez un nombre valide",
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
        return humanize(id_to_humanize)

    return str(id_to_humanize)


def dehumanize_id(id_to_dehumanize: int | str | None) -> int | None:
    if id_to_dehumanize is None:
        return None

    # This is because dehumanize_id will be called on a str the first time
    # and then on ids already dehumanized. dehumanize can't work with int
    if isinstance(id_to_dehumanize, str):
        return dehumanize(id_to_dehumanize)

    return int(id_to_dehumanize)


def check_string_is_not_empty(string: str) -> str:
    if not string or string.isspace():
        raise MissingError()

    return string


def check_phone_number_format(string: str) -> str:
    spaceless_string = string.replace(" ", "")
    if not re.match(r"^0\d{9}$", spaceless_string):
        raise ValueError("Format de téléphone incorrect. Exemple de format correct : 06 06 06 06 06")

    return spaceless_string


# No functools.partial here as it has no __name__ and threfore is not compatible with pydantic
def check_string_length_wrapper(length: int) -> Callable:
    def check_string_length(string: str) -> str:
        if string and len(string) > length:
            raise ValueError(f"Le champ doit faire moins de {length} caractères")
        return string

    return check_string_length


def string_to_boolean(string: str) -> bool | None:
    try:
        return {"true": True, "false": False}[string]
    except KeyError:
        raise ValidationError("La valeur reçu doit être soit 'true' soit 'false'")  # type: ignore [call-arg]


def humanize_field(field_name: str) -> classmethod:
    return validator(field_name, pre=True, allow_reuse=True)(humanize_id)


def dehumanize_field(field_name: str) -> classmethod:
    return validator(field_name, pre=True, allow_reuse=True)(dehumanize_id)


def dehumanize_list_field(field_name: str) -> classmethod:
    return validator(field_name, pre=True, allow_reuse=True)(dehumanize_ids_list)


def validate_not_empty_string_when_provided(field_name: str) -> classmethod:
    return validator(field_name, pre=True, allow_reuse=True)(check_string_is_not_empty)


def validate_phone_number_format(field_name: str) -> classmethod:
    return validator(field_name, pre=True, allow_reuse=True)(check_phone_number_format)


def string_to_boolean_field(field_name: str) -> classmethod:
    return validator(field_name, pre=True, allow_reuse=True)(string_to_boolean)


def string_length_validator(field_name: str, *, length: int) -> classmethod:
    return validator(field_name, pre=False, allow_reuse=True)(check_string_length_wrapper(length=length))
