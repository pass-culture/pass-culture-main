import json
from typing import Optional


class ApiErrors(Exception):
    status_code: int = 400

    def __init__(self, errors: dict = None, status_code: Optional[int] = None):
        self.errors = errors if errors else {}
        if status_code:
            self.status_code = status_code
        super().__init__()

    def add_error(self, field: str, error: str) -> None:
        if field in self.errors:
            self.errors[field].append(error)
        else:
            self.errors[field] = [error]

    def check_min_length(self, field: str, value: str, length: int) -> None:
        if len(value) < length:
            self.add_error(field, "Tu dois saisir au moins " + str(length) + " caractères.")

    def check_email(self, field: str, value: str) -> None:
        if not "@" in value:
            self.add_error(field, "L’e-mail doit contenir un @.")

    def maybe_raise(self) -> None:
        if len(self.errors) > 0:
            raise self

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
    www_authenticate = None
    realm = None

    def __init__(self, www_authenticate=None, realm=None, **kwargs):
        self.www_authenticate = www_authenticate
        self.realm = realm
        super().__init__(**kwargs)


class DecimalCastError(ApiErrors):
    status_code = 400


class DateTimeCastError(ApiErrors):
    status_code = 400


class UuidCastError(ApiErrors):
    status_code = 400
