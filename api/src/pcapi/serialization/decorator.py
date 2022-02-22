from copy import deepcopy
from functools import wraps
import logging
from typing import Any
from typing import Callable
from typing import Iterable
from typing import Optional
from typing import Type

from flask import Response
from flask import make_response
from flask import request
import pydantic
from werkzeug.exceptions import BadRequest

from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import api as default_api
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.serialization.spec_tree import ExtendedSpecTree


logger = logging.getLogger(__name__)


def _make_json_response(
    content: Optional[BaseModel],
    status_code: int,
    by_alias: bool,
    exclude_none: bool = False,
    headers: dict = None,
) -> Response:
    """serializes model, creates JSON response with given status code"""
    if status_code == 204:
        return make_response("", 204)

    if not content:
        raise ApiErrors({"configuration": "You need to provide a response body model if the status code is not 204"})

    json_content = content.json(exclude_none=exclude_none, by_alias=by_alias)

    response = make_response(json_content, status_code, headers or {})
    response.mimetype = "application/json"
    return response


def _make_string_response(content: Optional[BaseModel], status_code: int, headers: dict = None) -> Response:
    """serializes model, creates JSON response with given status code"""
    if status_code == 204:
        return make_response("", 204)

    if not content:
        raise ApiErrors({"configuration": "You need to provide a response body model if the status code is not 204"})

    response = make_response(content, status_code, headers or {})
    return response


def spectree_serialize(
    headers: Type[BaseModel] = None,
    cookies: Type[BaseModel] = None,
    response_model: Type[BaseModel] = None,
    tags: Iterable = (),
    before: Callable = None,
    after: Callable = None,
    response_by_alias: bool = True,
    exclude_none: bool = False,
    on_success_status: int = 200,
    on_empty_status: Optional[int] = None,
    on_error_statuses: Optional[list[int]] = None,
    api: ExtendedSpecTree = default_api,
    json_format: bool = True,
    response_headers: Optional[dict[str, str]] = None,
    resp: Optional[SpectreeResponse] = None,
) -> Callable[[Any], Any]:
    """A decorator that serialize/deserialize and validate input/output

    Args:
        cookies: Describes the cookies. Defaults to None.
        response_model: Describes the http response Model. Defaults to None.
        tags: list of tags’ string. Defaults to ().
        before: hook executed before the spectree validation. Defaults to None.
        after: hook executed after the spectree validation. Defaults to None.
        response_by_alias: whether or not the alias generator will be used. Defaults to True.
        exclude_none: whether or not to remove the none values. Defaults to False.
        on_success_status: status returned when the validation is a success. Defaults to 200.
        on_error_statuses: list of possible error statuses. Defaults to [].
        api: [description]. Defaults to default_api.
        json_format: JSON format response if true, else text format response. Defaults to True.
        response_headers: a dict of headers to be added to the response. defaults to {}.
        resp: a Spectree.Response explicitely listing the possible responses.

    Returns:
        Callable[[Any], Any]: [description]
    """

    on_error_statuses = on_error_statuses or []
    response_headers = response_headers or {}
    on_empty_status = on_empty_status or on_success_status

    def decorate_validation(route: Callable[..., Any]) -> Callable[[Any], Any]:
        body_in_kwargs = route.__annotations__.get("body")
        query_in_kwargs = route.__annotations__.get("query")
        form_in_kwargs = route.__annotations__.get("form")

        if 403 not in on_error_statuses:
            on_error_statuses.append(403)

        response_codes = {f"HTTP_{on_success_status}": response_model} | {
            f"HTTP_{on_error_status}": None for on_error_status in on_error_statuses
        }

        if resp:
            spectree_response = resp
        else:
            spectree_response = SpectreeResponse(**response_codes)

        security = deepcopy(getattr(route, "requires_authentication", None))

        @wraps(route)
        @api.validate(
            query=query_in_kwargs,
            headers=headers,
            cookies=cookies,
            resp=spectree_response,
            tags=tags,
            before=before,
            after=after,
            json=body_in_kwargs,
            security=security,
        )
        def sync_validate(*args: dict, **kwargs: dict) -> Response:
            try:
                body_params = request.get_json()
            except BadRequest as error:
                logger.info(
                    "Error when decoding request body: %s",
                    error,
                    extra={"contentTypeHeader": request.headers.get("Content-Type"), "path": request.path},
                )
                body_params = None
            query_params = request.args
            form = request.form
            if body_in_kwargs:
                kwargs["body"] = body_in_kwargs(**(body_params or {}))
            if query_in_kwargs:
                kwargs["query"] = query_in_kwargs(**query_params)
            if form_in_kwargs:
                try:
                    kwargs["form"] = form_in_kwargs(**form)
                except pydantic.ValidationError as validation_errors:
                    error_dict = {}
                    for errors in validation_errors.errors():
                        error_dict[errors["loc"][0]] = errors["msg"]
                    raise ApiErrors(error_dict)

            result = route(*args, **kwargs)
            if json_format:
                return _make_json_response(
                    content=result,
                    status_code=on_success_status if result else on_empty_status,
                    by_alias=response_by_alias,
                    exclude_none=exclude_none,
                    headers=response_headers,
                )

            return _make_string_response(content=result, status_code=on_success_status, headers=response_headers)

        return sync_validate

    return decorate_validation
