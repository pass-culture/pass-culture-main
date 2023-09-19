import inspect
import typing

from pcapi.routes.public.united import blueprint
from pcapi.routes.public.united import errors
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import api_key_required


def public_api_route(path: str, method: str, tags: typing.Sequence[str]) -> typing.Callable:
    """Three decorators with one simple call:
      1. register a flask route
      2. enable api key authentification for it
      3. apply spec tree serialization and magic to it

    Use path arg like any flask route. Unlike Flask, only one HTTP
    method can be set. Tags will be used by spectree while building
    the openapi document.
    """

    def _pcroute(func: typing.Callable) -> typing.Callable:
        router = blueprint.public_api_blueprint.route(path, methods=[method])
        authenticater = api_key_required
        serializer = serialize(tags, method)
        return router(authenticater(serializer(func)))

    return _pcroute


def serialize(tags: typing.Sequence[str], method: str) -> typing.Callable:
    """Wrapper around spectree_serialize function.

    The main goal here is to provide a generic tool that will call
    spectree_serialize with appropriate data.

    To do so, we fetch some of the function's information to pass them
    to spectree_serialize, like the return model and the fist line of
    the docstring.
    """

    def _serialize(func: typing.Callable) -> typing.Callable:
        success_response_model = inspect.signature(func).return_annotation

        try:
            success_desc = func.__doc__.splitlines()[0]  # type: ignore[union-attr]
        except AttributeError:
            success_desc = ""

        spectree_response_kwargs = {
            "HTTP_401": (errors.AuthErrorResponseModel, "Authentication is mandatory"),
            "HTTP_404": (None, "Unknown resource"),
            "HTTP_410": (None, "Resource is unreachable"),
            "HTTP_204": (None, success_desc),
            "HTTP_201": (success_response_model, success_desc),
            "HTTP_200": (success_response_model, success_desc),
        }

        # save method and statuc code, to be accessed later (eg. during tests)
        # this can be useful to find the original function information
        # that will be hidden by decorators
        func.method = method  # type: ignore[attr-defined]

        name = func.__name__
        return_annotation = inspect.signature(func).return_annotation

        if return_annotation is inspect._empty or return_annotation is None:
            func.status_code = 204  # type: ignore[attr-defined]
        elif name.startswith("create") or name.startswith("build"):
            func.status_code = 201  # type: ignore[attr-defined]
        else:
            func.status_code = 200  # type: ignore[attr-defined]

        return spectree_serialize(
            api=blueprint.public_api_schema,
            resp=SpectreeResponse(**spectree_response_kwargs),
            tags=tags,
            on_success_status=func.status_code,  # type: ignore[attr-defined]
            on_empty_status=204,
        )(func)

    return _serialize
