import datetime

from sqlalchemy import orm as sa_orm

from pcapi import settings
from pcapi.core.finance import exceptions as finance_exceptions
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.backend.base import BaseFinanceBackend
from pcapi.core.finance.backend.base import SettlementPayload
from pcapi.core.finance.backend.cegid import CegidFinanceBackend
from pcapi.core.finance.backend.dummy import DummyFinanceBackend
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils.module_loading import import_string


_backends = [
    DummyFinanceBackend,
    CegidFinanceBackend,
]


def push_invoice(invoice_id: int) -> dict | None:
    backend = _get_backend()
    invoice = db.session.get(finance_models.Invoice, invoice_id)
    assert invoice  # helps mypy
    return backend.push_invoice(invoice)


def push_bank_account(bank_account_id: int) -> dict | None:
    backend = _get_backend()
    bank_account = (
        db.session.query(finance_models.BankAccount)
        .filter_by(id=bank_account_id)
        .options(
            sa_orm.joinedload(finance_models.BankAccount.offerer, innerjoin=True).load_only(
                offerers_models.Offerer.name, offerers_models.Offerer.siren
            )
        )
        .one()
    )
    return backend.push_bank_account(bank_account)


def get_bank_account(bank_account_id: int) -> dict | None:
    backend = _get_backend()
    return backend.get_bank_account(bank_account_id)


def get_invoice(reference: str) -> dict | None:
    backend = _get_backend()
    return backend.get_invoice(reference)


def get_settlements(from_date: datetime.date | None, to_date: datetime.date | None) -> list[SettlementPayload]:
    backend = _get_backend()
    return backend.get_settlements(from_date, to_date)


def get_time_to_sleep_between_two_sync_requests() -> int:
    backend = _get_backend()
    return backend.time_to_sleep_between_two_sync_requests


def check_can_push_invoice() -> bool:
    backend = _get_backend()
    return backend.check_can_push_invoice()


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
