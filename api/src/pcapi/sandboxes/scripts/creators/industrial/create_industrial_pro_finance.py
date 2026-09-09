import datetime
import logging

from pcapi.core.finance import factories
from pcapi.core.finance import models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


@log_func_duration
def create_industrial_pro_finance() -> None:
    """
    Here we create some finance objects to test their behavior on PC Pro
    We do not create cashflows, pricings or stocks as they are not needed to display the settlements / invoices / banck accounts
    """

    logger.info("create_industrial_pro_finance")
    now = date_utils.get_naive_utc_now()

    # offerer, user, user offerer
    offerer = offerers_factories.OffererFactory.create(name="Entité pro finance")
    user = users_factories.ProFactory.create(email="pro_finance@example.com")
    offerers_factories.UserOffererFactory.create(offerer=offerer, user=user)

    # venue, bank account and link
    venue_1 = offerers_factories.VenueFactory.create(
        name="Structure pro finance 1", managingOfferer=offerer, pricing_point="self"
    )
    venue_2 = offerers_factories.VenueFactory.create(
        name="Structure pro finance 2", managingOfferer=offerer, pricing_point="self"
    )
    bank_account_1 = factories.BankAccountFactory.create(
        label="Compte bancaire 1", offerer=offerer, status=models.BankAccountApplicationStatus.ACCEPTED
    )
    bank_account_2 = factories.BankAccountFactory.create(
        label="Compte bancaire 2", offerer=offerer, status=models.BankAccountApplicationStatus.ACCEPTED
    )
    offerers_factories.VenueBankAccountLinkFactory.create(venue=venue_1, bankAccount=bank_account_1)
    offerers_factories.VenueBankAccountLinkFactory.create(venue=venue_2, bankAccount=bank_account_2)

    # settlement batch
    batch_1 = factories.SettlementBatchFactory.create(name="VIR1", dateValidated=now - datetime.timedelta(days=3))
    batch_2 = factories.SettlementBatchFactory.create(name="VIR2", dateValidated=now - datetime.timedelta(days=2))
    batch_3 = factories.SettlementBatchFactory.create(name="VIR3-1", dateValidated=now - datetime.timedelta(days=1))

    # settlement on first batch, first bank account, 2 invoices (positive and negative amount)
    factories.SettlementFactory.create(
        status=models.SettlementStatus.EXECUTED,
        amount=10000,
        bankAccount=bank_account_1,
        batch=batch_1,
        invoices=[
            factories.InvoiceFactory.create(amount=-15000, bankAccount=bank_account_1, date=batch_1.dateValidated),
            factories.InvoiceFactory.create(amount=5000, bankAccount=bank_account_1, date=batch_1.dateValidated),
        ],
    )
    # settlement on first batch, first bank account, two invoices
    factories.SettlementFactory.create(
        status=models.SettlementStatus.EXECUTED,
        amount=30000,
        bankAccount=bank_account_1,
        batch=batch_1,
        invoices=[
            factories.InvoiceFactory.create(amount=-10000, bankAccount=bank_account_1, date=batch_1.dateValidated),
            factories.InvoiceFactory.create(amount=-10000, bankAccount=bank_account_1, date=batch_2.dateValidated),
            factories.InvoiceFactory.create(amount=-10000, bankAccount=bank_account_1, date=batch_3.dateValidated),
        ],
    )
    # settlement on second batch, second bank account, two invoices, one is not PAID
    factories.SettlementFactory.create(
        status=models.SettlementStatus.EXECUTED,
        amount=5000,
        bankAccount=bank_account_2,
        batch=batch_2,
        invoices=[
            factories.InvoiceFactory.create(amount=-2500, bankAccount=bank_account_1, date=batch_2.dateValidated),
            factories.InvoiceFactory.create(
                amount=-2500,
                bankAccount=bank_account_1,
                date=batch_2.dateValidated,
                status=models.InvoiceStatus.PENDING_PAYMENT,
            ),
        ],
    )
    # settlement on third batch, second bank account, one invoice
    factories.SettlementFactory.create(
        status=models.SettlementStatus.EXECUTED,
        amount=4000,
        bankAccount=bank_account_2,
        batch=batch_3,
        invoices=[
            factories.InvoiceFactory.create(amount=-4000, bankAccount=bank_account_1, date=batch_2.dateValidated),
        ],
    )
    # settlement on third batch, second bank account, no invoice
    factories.SettlementFactory.create(
        status=models.SettlementStatus.EXECUTED,
        amount=5000,
        bankAccount=bank_account_2,
        batch=batch_3,
    )
    # rejected settlement on third batch
    factories.SettlementFactory.create(
        status=models.SettlementStatus.REJECTED,
        amount=30000,
        bankAccount=bank_account_1,
        batch=batch_3,
    )
