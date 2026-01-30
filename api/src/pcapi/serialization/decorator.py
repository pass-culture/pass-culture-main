import logging
import typing
from collections import defaultdict
from functools import wraps

import flask
import pydantic.v1
import spectree
from pydantic import RootModel
from werkzeug.datastructures import MultiDict
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import UnsupportedMediaType

from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.routes.apis import api as default_api
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import HttpBodyModel
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse

from .spec_tree import add_feature_flag


logger = logging.getLogger(__name__)


def _make_json_response(
    content: BaseModel | HttpBodyModel | None,
    status_code: int,
    by_alias: bool,
    exclude_none: bool = False,
    headers: dict | None = None,
) -> flask.Response:
    """serializes model, creates JSON response with given status code"""
    if status_code == 204:
        return flask.make_response("", 204)

    if not content:
        raise ApiErrors({"configuration": "You need to provide a response body model if the status code is not 204"})

    json_content = content.json(exclude_none=exclude_none, by_alias=by_alias)

    response = flask.make_response(json_content, status_code, headers or {})
    response.mimetype = "application/json"
    return response


def _make_string_response(
    content: BaseModel | HttpBodyModel | None, status_code: int, headers: dict | None = None
) -> flask.Response:
    """serializes model, creates JSON response with given status code"""
    if status_code == 204:
        return flask.make_response("", 204)

    if not content:
        raise ApiErrors({"configuration": "You need to provide a response body model if the status code is not 204"})

    response = flask.make_response(content, status_code, headers or {})
    return response


def _transform_query_args_to_dict(query_params: MultiDict, use_as_list: list[str]) -> dict:
    result = defaultdict(list)
    for key, value in query_params.items(multi=True):
        if key in use_as_list:
            result[key].append(value)
        else:
            result[key] = value
    return dict(result)


# When using this decorator, you should pass the following arguments when necessary:
# - query: the query parameters
# - body : the body of the request
# - form : the form data
# You should type these arguments as pydantic models.
def spectree_serialize(
    *,
    headers: type[BaseModel] | None = None,
    cookies: type[BaseModel] | None = None,
    response_model: type[BaseModel] | type[HttpBodyModel] | type[RootModel] | None = None,
    tags: typing.Sequence = (),
    before: typing.Callable | None = None,
    after: typing.Callable | None = None,
    response_by_alias: bool = True,
    exclude_none: bool = False,
    on_success_status: int = 200,
    on_empty_status: int | None = None,
    on_error_statuses: list[int] | None = None,
    api: spectree.SpecTree = default_api,
    json_format: bool = True,
    raw_response: bool = False,
    response_headers: dict[str, str] | None = None,
    resp: SpectreeResponse | None = None,
    deprecated: bool = False,
    query_params_as_list: list[str] | None = None,
) -> typing.Callable[[typing.Any], typing.Any]:
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
        raw_response: transmit the route response without touching it. Defaults to False.
        response_headers: a dict of headers to be added to the response. defaults to {}.
        resp: a Spectree.Response explicitly listing the possible responses.
        query_params_as_list: a list of query parameters that will be cast to a list. Defaults to None.

    Returns:
        typing.Callable[[Any], typing.Any]: [description]
    """

    on_error_statuses = on_error_statuses or []
    response_headers = response_headers or {}
    on_empty_status = on_empty_status or on_success_status

    def decorate_validation(route: typing.Callable[..., typing.Any]) -> typing.Callable[[typing.Any], typing.Any]:
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

        @wraps(route)
        @api.validate(
            after=after,
            before=before,
            cookies=cookies,
            deprecated=deprecated,
            form=form_in_kwargs,
            headers=headers,
            json=body_in_kwargs,
            query=query_in_kwargs,
            resp=spectree_response,
            tags=tags,
        )
        def sync_validate(*args: typing.Any, **kwargs: typing.Any) -> flask.Response:
            query_params = flask.request.args
            form = flask.request.form
            if body_in_kwargs:
                try:
                    body_params = flask.request.get_json()
                except UnsupportedMediaType:
                    return flask.make_response(
                        'Please send a "Content-Type: application/json" HTTP header',
                        400,
                    )
                except BadRequest:
                    # Since pydantic validator is applied before this method and use a silent json parser,
                    # the only case we should end here is with an PATCH/POST with no validator for body params
                    # or a GET request with a invalid body.
                    raise
                try:
                    kwargs["body"] = body_in_kwargs(**(body_params or {}))
                except pydantic.v1.ValidationError:
                    # If we end up here, it means that the client did
                    # not send the correct HTTP header. Otherwise, the
                    # validation error would have been caught by the
                    # `before` handler in `api.validate()` decorator.
                    return flask.make_response(
                        'Please send a "Content-Type: application/json" HTTP header',
                        400,
                    )

            if query_in_kwargs:
                content: dict | MultiDict
                if query_params_as_list:
                    content = _transform_query_args_to_dict(query_params, query_params_as_list)
                else:
                    content = query_params
                kwargs["query"] = query_in_kwargs(**content)

            if form_in_kwargs:
                try:
                    kwargs["form"] = form_in_kwargs(**form)
                except pydantic.v1.ValidationError:
                    return flask.make_response(
                        'Please send a "Content-Type: application/x-www-form-urlencoded" HTTP header', 400
                    )

            result = route(*args, **kwargs)
            if raw_response:
                return result
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


def feature_flag_required(feature_flag: FeatureToggle) -> typing.Callable:
    """
    Decorator to link a route to a feature flag

    If the feature flag is not active :
        - calls to the route return a HTTP 404 response
        - the route does not appear in the openapi.json generated by spectree
    """

    def route_decorator(route_function: typing.Callable) -> typing.Callable:
        add_feature_flag(route_function, feature_flag=feature_flag)

        @wraps(route_function)
        def wrapper(*args: typing.Any, **kwds: typing.Any) -> flask.Response:
            if not feature_flag.is_active():
                flask.abort(404)

            return route_function(*args, **kwds)

        return wrapper

    return route_decorator
