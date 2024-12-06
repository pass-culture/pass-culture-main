from pcapi.core.finance import models as finance_models


class BaseFinanceBackend:
    def push_invoice(self, invoice: finance_models.Invoice) -> dict | None:
        raise NotImplementedError()

    def push_bank_account(self, bank_account: finance_models.BankAccount) -> dict | None:
        raise NotImplementedError()

    def get_bank_account(self, bank_account_id: int) -> dict | None:
        raise NotImplementedError()

    def get_invoice(self, reference: str) -> dict | None:
        raise NotImplementedError()

    @property
    def is_configured(self) -> bool:
        raise NotImplementedError()
