from pydantic import ValidationError
from typing import Optional, Any
from flask import Response, Request

from pcapi.models import ApiErrors

def to_camel(string: str) -> str:
    components = string.split("_")
    return components[0] + "".join(x.title() for x in components[1:])

def before_handler(
    request: Request, response: Response, pydantic_error: Optional[ValidationError], _: Any
) -> None:
    """Raises an ``ApiErrors` exception if input validation fails.

    This handler is automatically called through the ``spectree_serialize()`` decorator.
    """
    if pydantic_error and pydantic_error.errors():
        api_errors = ApiErrors()
        for error in pydantic_error.errors():
            if error["type"] == "value_error.extra":
                api_errors.add_error(
                    error["loc"][0], "Vous ne pouvez pas changer cette information"
                )
            elif error["type"] == "value_error.missing":
                api_errors.add_error(error["loc"][0], "Ce champ est obligatoire")
            else:
                api_errors.add_error(error["loc"][0], error["msg"])
        raise api_errors
