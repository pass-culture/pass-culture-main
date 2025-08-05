import json
import typing

from pcapi.core.core_exception import ClientError
from pcapi.core.core_exception import CoreException


class ApiErrors(Exception):
    status_code: int = 400

    def __init__(self, errors: dict | None = None, status_code: int | None = None):
        self.errors = errors if errors else {}
        if status_code:
            self.status_code = status_code
        super().__init__()

    def add_error(self, field: str, error: str) -> None:
        if field in self.errors:
            self.errors[field].append(error)
        else:
            self.errors[field] = [error]

    def add_client_error(self, client_error: ClientError | CoreException) -> None:
        self.errors |= client_error.errors

    def check_min_length(self, field: str, value: str, length: int) -> None:
        if len(value) < length:
            self.add_error(field, "Tu dois saisir au moins " + str(length) + " caractères.")

    def check_email(self, field: str, value: str) -> None:
        if "@" not in value:
            self.add_error(field, "L’email doit contenir un @.")

    def __str__(self) -> str:
        if self.errors:
            return json.dumps(self.errors, indent=2)
        return super().__str__()


class ResourceGoneError(ApiErrors):
    status_code = 410


class ResourceNotFoundError(ApiErrors):
    status_code = 404


class ForbiddenError(ApiErrors):
    status_code = 403


class UnauthorizedError(ApiErrors):
    status_code = 401
    www_authenticate: str | None = None
    realm: str | None = None

    def __init__(
        self,
        www_authenticate: str | None = None,
        realm: str | None = None,
        **kwargs: typing.Any,
    ) -> None:
        self.www_authenticate = www_authenticate
        self.realm = realm
        super().__init__(**kwargs)


class DecimalCastError(ApiErrors):
    status_code = 400


class DateTimeCastError(ApiErrors):
    status_code = 400


class UuidCastError(ApiErrors):
    status_code = 400
