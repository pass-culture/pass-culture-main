from collections.abc import Callable
import contextlib
import typing

from flask import url_for
from pydantic.v1 import BaseModel
from pydantic.v1 import ValidationError
import pytest

from pcapi.core.testing import assert_num_queries


class Context(BaseModel):
    """Use to validate test classes' attributes"""

    controller: Callable
    method: str
    status_code: int
    path_kwargs: dict[str, int | str]
    num_queries: int | None


class PublicApiBaseTest:
    @contextlib.contextmanager
    def assert_valid_response(self, client, path=None, length=None, payload=None):
        """Validate response's length, data, status code and format it.

        Args:
            client: can be any client, depending on the test context
                (authenticated or not).
            path: can be used to override the one automatically build
                from the context, eg. inside parameterized tests.
            length: expected response data length (to be used only when
                it is expected to be an iterable).
            payload: data to send.

        Returns:
            generator: JSON response as a dict.

        Raises:
            AssertionError: the http status was not the expected one.
        """
        path = path if path else self.path

        if self.ctx.num_queries is not None:
            with assert_num_queries(self.ctx.num_queries):
                response = self._send_request(client, path, payload)
        else:
            response = self._send_request(client, path, payload)

        error_msg = f"found: {response.status_code}, expected: {self.ctx.status_code}. "
        if response.json:
            error_msg += f"JSON is: {response.json}"
        else:
            error_msg += f"Because: {response.data}"

        assert response.status_code == self.ctx.status_code, error_msg

        if response.status_code < 300:
            # 2xx response -> validate the response's data
            yield self.validate_response_length(response.json, length)
        else:
            # error or redirection -> return the raw data
            yield response.json

    def validate_response_length(self, data, length=None):
        """Check response's (json) length and return it"""
        if length is None:
            return data

        if not isinstance(data, typing.Sequence):
            pytest.fail(reason="Can't set length parameter if response if not a sequence")

        try:
            assert len(data) == length
        except TypeError:
            pytest.fail(reason="Not a Size object")

        try:
            res = data[0] if length == 1 else data
        except IndexError:
            pytest.fail(reason="Unexpected index error while validating response data length")

        return res  # makes pylint happy...(inconsistent return statements)

    @classmethod
    def setup_class(cls):
        """Validate mandatory and optional class args defined inside the
        Context class.

        This method relies heavily on the actions made by the
        `public_api_route` decorator (like computing and saving the
        expected http status code).

        Notes:
            - `status_code` is read from the controller's saved fields,
            unless the class defined a specific value (eg. an error
            code);
            - if anything goes wrong during this setup, each test will
            automatically fail.
        """
        try:
            controller = getattr(cls, "controller")
        except AttributeError as exc:
            pytest.fail(reason=f"Config: missing '{exc.name}'")

        try:
            method = controller.method.lower()
        except AttributeError:
            pytest.fail(reason="Config: could not extract HTTP method from controller")

        status_code = getattr(cls, "status_code", None)
        if not status_code:
            try:
                status_code = controller.status_code
            except AttributeError:
                reason = "Config: no user-defined status code and could not extract HTTP status code from controller"
                pytest.fail(reason=reason)

        try:
            cls.ctx = Context(
                controller=controller,
                method=method,
                status_code=status_code,
                path_kwargs=getattr(cls, "path_kwargs", {}),
                num_queries=getattr(cls, "num_queries", None),
            )
        except ValidationError as exc:
            pytest.fail(reason=f"Config: {exc}")

    @property
    def path(self):
        return self.build_path(**self.ctx.path_kwargs)

    def build_path(self, **kwargs):
        return url_for(f"public_api.{self.ctx.controller.__name__}", **kwargs)

    def _send_request(self, client, path, payload=None):
        if self.ctx.method in ("post", "patch"):
            return getattr(client, self.ctx.method)(path, json=payload)
        return getattr(client, self.ctx.method)(path)


class BadRequestBaseTest(PublicApiBaseTest):
    status_code = 400


class UnauthorizedBaseTest(PublicApiBaseTest):
    status_code = 403


class NotFoundBaseTest(PublicApiBaseTest):
    status_code = 404


class UnauthenticatedMixin:
    def test_unauthenticated(self, client):
        # warning: the client parameter is a pytest fixture. Do not
        # change it. It is expected to be the default client fixture,
        # hence without any specific authentication.
        response = getattr(client, self.ctx.method)(self.path)
        assert response.status_code == 401


class UnknownResourceMixin:
    def test_unknown_resource(self, api_client):
        # warning: the api_client parameter is a pytest fixture. Do not
        # change it. It is expected to be the authenticated client
        # fixture.
        response = getattr(api_client, self.ctx.method)(self.path)
        assert response.status_code == 404
