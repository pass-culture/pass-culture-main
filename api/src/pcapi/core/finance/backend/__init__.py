import datetime
import typing

from sqlalchemy import orm as sa_orm

from pcapi import settings
from pcapi.core.finance import exceptions as finance_exceptions
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import utils as finance_utils
from pcapi.core.finance.backend.base import ExternalType
from pcapi.core.finance.backend.base import InvoicePayload
from pcapi.core.finance.backend.base import SettlementPayload
from pcapi.core.finance.backend.cegid import CegidFinanceBackend
from pcapi.core.finance.backend.dummy import DummyFinanceBackend
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils import date as date_utils


type Backend = CegidFinanceBackend | DummyFinanceBackend

BACKEND_BY_KEY: typing.Final[dict[str, type[Backend]]] = {
    "CegidFinanceBackend": CegidFinanceBackend,
    "DummyFinanceBackend": DummyFinanceBackend,
}


def _get_backend() -> Backend:
    backend = BACKEND_BY_KEY[settings.FINANCE_BACKEND]()
    if not backend.is_configured:
        backend_name = backend.__class__.__name__
        raise finance_exceptions.FinanceBackendNotConfigured(
            f"Finance backend `{backend_name}` not correctly configured"
        )
    return backend


def push_invoice(invoice_id: int) -> dict | None:
    backend = _get_backend()
    invoice = db.session.get(finance_models.Invoice, invoice_id)
    assert invoice  # helps mypy

    invoice_external_type = ExternalType.ADR if invoice.reference.startswith("A") else ExternalType.INV
    invoice_batch = invoice.cashflows[0].batch
    start_date, end_date = finance_utils.get_invoice_daterange(invoice_batch.cutoff)
    invoice_description = f"{invoice_batch.label} - {start_date:%d/%m}-{end_date:%d/%m}"

    payload = InvoicePayload.build(invoice, invoice_external_type, invoice_description)
    return backend.push_invoice(payload)


def push_invoice_debt_cancellation(invoice_id: int, old_bank_account_id: int, bank_account_id: int) -> dict | None:
    backend = _get_backend()
    invoice = (
        db.session.query(finance_models.Invoice)
        .filter(finance_models.Invoice.id == invoice_id)
        .options(sa_orm.joinedload(finance_models.Invoice.settlements))
    ).one()

    invoice_external_type = ExternalType.ACR if invoice.reference.startswith("A") else ExternalType.ADR
    invoice_description = f"REC_{invoice.reference} - Changement BA de {old_bank_account_id} à {bank_account_id}"
    settlements_nb = len(invoice.settlements)
    reference_suffix = "_R" * (settlements_nb - 1) + "_A"

    payload = InvoicePayload.build(
        invoice=invoice,
        invoice_external_type=invoice_external_type,
        invoice_description=invoice_description,
        reference=invoice.reference + reference_suffix,
        bank_account_id=str(old_bank_account_id),
        invoice_date=date_utils.get_naive_utc_now(),
    )
    return backend.push_invoice(payload)


def push_invoice_debt_recreation(invoice_id: int, old_bank_account_id: int, bank_account_id: int) -> dict | None:
    backend = _get_backend()
    invoice = (
        db.session.query(finance_models.Invoice)
        .filter(finance_models.Invoice.id == invoice_id)
        .options(sa_orm.joinedload(finance_models.Invoice.settlements))
    ).one()

    invoice_external_type = ExternalType.ADR if invoice.reference.startswith("A") else ExternalType.ACR
    invoice_description = f"REC_{invoice.reference} - Changement BA de {old_bank_account_id} à {bank_account_id}"
    settlements_nb = len(invoice.settlements)
    reference_suffix = "_R" * settlements_nb

    payload = InvoicePayload.build(
        invoice=invoice,
        invoice_external_type=invoice_external_type,
        invoice_description=invoice_description,
        reference=invoice.reference + reference_suffix,
        bank_account_id=str(bank_account_id),
        invoice_date=date_utils.get_naive_utc_now(),
    )
    return backend.push_invoice(payload)


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
