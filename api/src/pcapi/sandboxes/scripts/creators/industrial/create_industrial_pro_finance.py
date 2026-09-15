import datetime
import logging

from pcapi.core.finance import factories
from pcapi.core.finance import models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
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

    user = users_factories.ProFactory.create(email="pro_finance@example.com")

    create_various_settlements(user=user)

    create_rejected_settlement(user=user)

    create_rejected_and_processed_settlement(user=user)

    create_rejected_and_solved_settlement(user=user)


@log_func_duration
def create_various_settlements(user: users_models.User) -> None:
    now = date_utils.get_naive_utc_now()

    offerer = offerers_factories.OffererFactory.create(name="Entité pro finance avec virements")
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
    # settlement on first batch, first bank account, 3 invoices
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


@log_func_duration
def create_rejected_settlement(user: users_models.User) -> None:
    """Create a rejected settlement with venues detached from the bank account"""

    now = date_utils.get_naive_utc_now()

    offerer = offerers_factories.OffererFactory.create(name="Entité pro finance avec rejet")
    offerers_factories.UserOffererFactory.create(offerer=offerer, user=user)

    # the bank account is refused and the venue link is valid until 5 days ago
    venue = offerers_factories.VenueFactory.create(
        name="Structure pro finance 3", managingOfferer=offerer, pricing_point="self"
    )
    bank_account = factories.BankAccountFactory.create(
        label="Compte bancaire 3 refusé", offerer=offerer, status=models.BankAccountApplicationStatus.REFUSED
    )
    offerers_factories.VenueBankAccountLinkFactory.create(
        venue=venue,
        bankAccount=bank_account,
        timespan=[now - datetime.timedelta(days=365), now - datetime.timedelta(days=5)],
    )

    # the batch occurred 5 days ago and the settlement is rejected, in sync with the bank account status
    batch = factories.SettlementBatchFactory.create(name="VIR10", dateValidated=now - datetime.timedelta(days=5))
    invoice = factories.InvoiceFactory.create(amount=-10000, bankAccount=bank_account, date=batch.dateValidated)
    factories.SettlementFactory.create(
        status=models.SettlementStatus.REJECTED, amount=10000, bankAccount=bank_account, batch=batch, invoices=[invoice]
    )


@log_func_duration
def create_rejected_and_processed_settlement(user: users_models.User) -> None:
    """A rejected settlement is considered 'processed' if the structures previously linked to the rejected bank account are linked to a valid bank account"""

    now = date_utils.get_naive_utc_now()

    offerer = offerers_factories.OffererFactory.create(name="Entité pro finance avec rejet traité")
    offerers_factories.UserOffererFactory.create(offerer=offerer, user=user)

    # the bank account is refused and the venue link is valid until 5 days ago
    venue = offerers_factories.VenueFactory.create(
        name="Structure pro finance 4", managingOfferer=offerer, pricing_point="self"
    )
    bank_account = factories.BankAccountFactory.create(
        label="Compte bancaire 4 refusé", offerer=offerer, status=models.BankAccountApplicationStatus.REFUSED
    )
    offerers_factories.VenueBankAccountLinkFactory.create(
        venue=venue,
        bankAccount=bank_account,
        timespan=[now - datetime.timedelta(days=365), now - datetime.timedelta(days=5)],
    )

    # the batch occurred 5 days ago and the settlement is rejected, in sync with the bank account status
    batch = factories.SettlementBatchFactory.create(name="VIR11", dateValidated=now - datetime.timedelta(days=5))
    invoice = factories.InvoiceFactory.create(amount=-10000, bankAccount=bank_account, date=batch.dateValidated)
    factories.SettlementFactory.create(
        status=models.SettlementStatus.REJECTED, amount=10000, bankAccount=bank_account, batch=batch, invoices=[invoice]
    )

    # another valid bank account is now linked to the venue
    new_bank_account = factories.BankAccountFactory.create(label="Compte bancaire 5", offerer=offerer)
    offerers_factories.VenueBankAccountLinkFactory.create(
        venue=venue, bankAccount=new_bank_account, timespan=[now - datetime.timedelta(days=4), None]
    )


@log_func_duration
def create_rejected_and_solved_settlement(user: users_models.User) -> None:
    """
    A rejected settlement is considered 'solved' if
    - the structures previously linked to the rejected bank account are linked to a valid bank account
    - a new settlement is executed and is linked to the rejected settlement invoices
    """

    now = date_utils.get_naive_utc_now()

    offerer = offerers_factories.OffererFactory.create(name="Entité pro finance avec rejet résolu")
    offerers_factories.UserOffererFactory.create(offerer=offerer, user=user)

    # the bank account is refused and the venue link is valid until 5 days ago
    venue = offerers_factories.VenueFactory.create(
        name="Structure pro finance 5", managingOfferer=offerer, pricing_point="self"
    )
    bank_account = factories.BankAccountFactory.create(
        label="Compte bancaire 5 refusé", offerer=offerer, status=models.BankAccountApplicationStatus.REFUSED
    )
    offerers_factories.VenueBankAccountLinkFactory.create(
        venue=venue,
        bankAccount=bank_account,
        timespan=[now - datetime.timedelta(days=365), now - datetime.timedelta(days=5)],
    )

    # the batch occurred 5 days ago and the settlement is rejected, in sync with the bank account status
    batch = factories.SettlementBatchFactory.create(name="VIR12", dateValidated=now - datetime.timedelta(days=5))
    invoice = factories.InvoiceFactory.create(amount=-10000, bankAccount=bank_account, date=batch.dateValidated)
    factories.SettlementFactory.create(
        status=models.SettlementStatus.REJECTED, amount=10000, bankAccount=bank_account, batch=batch, invoices=[invoice]
    )

    # another valid bank account is now linked to the venue
    new_bank_account = factories.BankAccountFactory.create(label="Compte bancaire 6", offerer=offerer)
    offerers_factories.VenueBankAccountLinkFactory.create(
        venue=venue, bankAccount=new_bank_account, timespan=[now - datetime.timedelta(days=4), None]
    )

    # a new settlement is executed on the new bank account, linked to the first rejected settlement invoice
    new_batch = factories.SettlementBatchFactory.create(name="VIR13", dateValidated=now - datetime.timedelta(days=3))
    factories.SettlementFactory.create(
        status=models.SettlementStatus.EXECUTED,
        amount=10000,
        bankAccount=new_bank_account,
        batch=new_batch,
        invoices=[invoice],
    )
