from pcapi import settings
from pcapi.core.finance import exceptions as finance_exceptions
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.backend.base import BaseFinanceBackend
from pcapi.core.finance.backend.cegid import CegidFinanceBackend
from pcapi.core.finance.backend.dummy import DummyFinanceBackend
from pcapi.models import db
from pcapi.utils.module_loading import import_string


_backends = [
    DummyFinanceBackend,
    CegidFinanceBackend,
]


def push_invoice(invoice_id: int) -> dict | None:
    backend = _get_backend()
    invoice = db.session.query(finance_models.Invoice).get(invoice_id)
    return backend.push_invoice(invoice)


def push_bank_account(bank_account_id: int) -> dict | None:
    backend = _get_backend()
    bank_account = (
        db.session.query(finance_models.BankAccount)
        .filter_by(id=bank_account_id)
        .join(finance_models.BankAccount.offerer)
        .one()
    )
    return backend.push_bank_account(bank_account)


def get_bank_account(bank_account_id: int) -> dict | None:
    backend = _get_backend()
    return backend.get_bank_account(bank_account_id)


def get_invoice(reference: str) -> dict | None:
    backend = _get_backend()
    return backend.get_invoice(reference)


def get_time_to_sleep_between_two_sync_requests() -> int:
    backend = _get_backend()
    return backend.time_to_sleep_between_two_sync_requests


def get_backend_name() -> str:
    backend = _get_backend()
    return backend.__class__.__name__


def _get_backend() -> BaseFinanceBackend:
    backend_class = import_string(settings.FINANCE_BACKEND)
    backend = backend_class()
    if not backend.is_configured:
        backend_name = backend.__class__.__name__
        raise finance_exceptions.FinanceBackendNotConfigured(
            f"Finance backend `{backend_name}` not correctly configured"
        )
    return backend
