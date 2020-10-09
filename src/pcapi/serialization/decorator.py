from flask import request, make_response, Response
from functools import wraps
from pydantic import BaseModel
from typing import Callable, Any
from spectree import Response as SpectreeResponse

from pcapi.flask_app import api
from pcapi.routes.serialization.serializer import serialize


def _make_json_response(
    content: BaseModel,
    status_code: int,
    by_alias: bool,
    exclude_none: bool = False,
) -> Response:
    """serializes model, creates JSON response with given status code"""
    json_content = content.json(exclude_none=exclude_none, by_alias=by_alias)

    response = make_response(json_content, status_code)
    response.mimetype = "application/json"
    return response


def spectree_serialize(
    query: BaseModel = None,
    headers: BaseModel = None,
    cookies: BaseModel = None,
    response_model: BaseModel = None,
    tags: tuple = (),
    before: Callable = None,
    after: Callable = None,
    response_by_alias: bool = True,
    exclude_none: bool = False,
    on_success_status: int = 200,
) -> Callable[[Any], Any]:
    """A decorator that serialize/deserialize and validate input/output

    Args:
        query (pydantic.BaseModel, optional): Pydantic Model that describes the query params. Defaults to None.
        headers (pydantic.BaseModel, optional): Pydantic Model that describes the headers. Defaults to None.
        cookies (pydantic.BaseModel, optional): Pydantic Model that describes the cookies. Defaults to None.
        response_model (pydantic.BaseModel, optional): Pydantic Model that describes the http response Model. Defaults to None.
        tags (tuple, optional): list of tags’ string. Defaults to ().
        before (Callable, optional): hook executed before the spectree validation. Defaults to None.
        after (Callable, optional): hook executed after the spectree validation. Defaults to None.
        response_by_alias (bool, optional): whether or not the alias generator will be used. Defaults to True.
        exclude_none (bool, optional): whether or not to remove the none values. Defaults to False.
        on_success_status (int, optional): status returned when the validation is a success. Defaults to 200.
    """

    def decorate_validation(route: Callable[..., Any]) -> Callable[[Any], Any]:
        body_in_kwargs = route.__annotations__.get("body")
        query_in_kwargs = route.__annotations__.get("query")
        spectree_response_success_code = f"HTTP_{on_success_status}"
        spectree_response = SpectreeResponse("HTTP_403")
        spectree_response.code_models[spectree_response_success_code] = response_model

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
        )
        def sync_validate(*args: dict, **kwargs: dict) -> Response:
            body_params = request.get_json()
            query_params = request.args
            if body_in_kwargs:
                kwargs["body"] = body_in_kwargs(**body_params)
            if query_in_kwargs:
                kwargs["query"] = query_in_kwargs(**query_params)

            result = route(*args, **kwargs)
            return _make_json_response(result, on_success_status, response_by_alias)

        return sync_validate

    return decorate_validation
