import pprint

from pcapi.models.api_errors import ApiErrors
from pcapi.utils import requests

from . import models


class FinanceException(Exception):
    pass


class NonCancellablePricingError(FinanceException):
    pass


class ReimbursementRuleValidationError(FinanceException):
    pass


class ConflictingReimbursementRule(ReimbursementRuleValidationError):
    def __init__(self, msg: str, conflicts: set) -> None:
        super().__init__(msg)
        self.conflicts = conflicts


class WrongDateForReimbursementRule(ReimbursementRuleValidationError):
    pass


class UnknownSubcategoryForReimbursementRule(ReimbursementRuleValidationError):
    pass


class NotPricingPointVenueForReimbursementRule(ReimbursementRuleValidationError):
    pass


class DepositTypeAlreadyGrantedException(ApiErrors):
    def __init__(self, deposit_type: models.DepositType) -> None:
        super().__init__({"user": [f'Cet utilisateur a déjà été crédité de la subvention "{deposit_type.name}".']})


class UserNotGrantable(FinanceException):
    pass


class UserCannotBeRecredited(FinanceException):
    pass


class UserHasNotFinishedSubscription(FinanceException):
    pass


class UserHasAlreadyActiveDeposit(UserNotGrantable):
    pass


class FinanceIncidentAlreadyCancelled(FinanceException):
    pass


class FinanceIncidentAlreadyValidated(FinanceException):
    pass


class FinanceIncidentAlreadyInvoiced(FinanceException):
    pass


class NoInvoiceToGenerate(FinanceException):
    pass


class VenueAlreadyLinkedToAnotherBankAccount(FinanceException):
    pass


class CommercialGestureOnMultipleStock(FinanceException):
    pass


class FinanceBackendApiError(FinanceException):
    pass


class FinanceBackendNotConfigured(FinanceException):
    pass


class FinanceBackendException(FinanceException):
    def __init__(self, response: requests.Response, message: str, include_body: bool = True) -> None:
        self.url = response.request.url
        self.method = response.request.method
        self.status_code = response.status_code
        if include_body:
            self.body = response.request.body
        self.response = response.content
        self.response_json = response.json() if "application/json" in response.headers.get("Content-Type", "") else None
        response_str = pprint.pformat(self.response_json) if self.response_json else self.response
        if include_body:
            message = (
                # using str() to help mypy
                f"{message}\n"
                f"{self.__class__.__name__}: Got status code: {self.status_code} when {self.method} url: {self.url}\n"
                f"body: {self.body!r}\n"
                f"response: {str(response_str)}"
            )
        else:
            message = (
                # using str() to help mypy
                f"{message}\n"
                f"{self.__class__.__name__}: Got status code: {self.status_code} when {self.method} url: {self.url}\n"
                f"response: {str(response_str)}"
            )
        super().__init__(message)


class FinanceBackendBadRequest(FinanceBackendException):
    pass


class FinanceBackendUnauthorized(FinanceBackendException):
    pass


class FinanceBackendInvalidCredentials(FinanceBackendException):
    def __init__(self, response: requests.Response, message: str) -> None:
        super().__init__(response, message, include_body=False)


class FinanceBackendUnexpectedResponse(FinanceBackendException):
    pass


class FinanceBackendBankAccountNotFound(FinanceBackendException):
    pass


class FinanceBackendInvoiceNotFound(FinanceBackendException):
    pass


class FinanceBackendInconsistentDistantData(FinanceBackendException):
    pass


class FinanceBackendInvoiceAlreadyExists(FinanceBackendException):
    pass
