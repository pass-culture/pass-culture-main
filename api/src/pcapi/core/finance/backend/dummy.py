from pcapi.core.finance import models as finance_models
from pcapi.core.finance.backend.base import BaseFinanceBackend


invoices: list[finance_models.Invoice] = []
bank_accounts: list[finance_models.BankAccount] = []


class DummyFinanceBackend(BaseFinanceBackend):
    def push_invoice(self, invoice: finance_models.Invoice) -> dict:
        invoices.append(invoice)
        return invoice.__dict__

    def push_bank_account(self, bank_account: finance_models.BankAccount) -> dict:
        bank_accounts.append(bank_account)
        return bank_account.__dict__

    def get_invoice(self, reference: str) -> dict:
        invoice = finance_models.Invoice.query.filter(finance_models.Invoice.reference == reference).first()
        return invoice.__dict__

    def get_bank_account(self, bank_account_id: int) -> dict:
        bank_account = finance_models.BankAccount.query.get(bank_account_id)
        return bank_account.__dict__

    @property
    def is_configured(self) -> bool:
        return True


def clear_invoices() -> None:
    invoices.clear()


def clear_bank_accounts() -> None:
    bank_accounts.clear()
