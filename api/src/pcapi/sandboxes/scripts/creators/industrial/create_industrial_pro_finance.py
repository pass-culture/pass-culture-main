import datetime
import logging

from pcapi.core.finance import factories
from pcapi.core.finance import models
from pcapi.core.object_storage import store_public_object
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration
from pcapi.utils import date as date_utils
from pcapi.utils.pdf import generate_pdf_from_html


logger = logging.getLogger(__name__)


@log_func_duration
def create_industrial_pro_finance() -> None:
    """
    Here we create some finance objects to test their behavior on PC Pro
    We do not create cashflows, pricings or stocks as they are not needed to display the settlements / invoices / bank accounts
    """

    logger.info("create_industrial_pro_finance")

    user = users_factories.ProFactory.create(email="pro_finance@example.com")

    create_various_settlements(user=user)

    create_rejected_settlement(user=user)

    create_rejected_processed_solved_settlements(user=user)


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
    refused_bank_account = factories.BankAccountFactory.create(
        label="Compte bancaire refusé", offerer=offerer, status=models.BankAccountApplicationStatus.REFUSED
    )
    bank_account_2 = factories.BankAccountFactory.create(
        label="Compte bancaire 2", offerer=offerer, status=models.BankAccountApplicationStatus.ACCEPTED
    )
    offerers_factories.VenueBankAccountLinkFactory.create(
        venue=venue_1,
        bankAccount=refused_bank_account,
        timespan=[now - datetime.timedelta(days=365), now - datetime.timedelta(days=5)],
    )
    offerers_factories.VenueBankAccountLinkFactory.create(
        venue=venue_1, bankAccount=bank_account_1, timespan=[now - datetime.timedelta(days=3), None]
    )
    offerers_factories.VenueBankAccountLinkFactory.create(venue=venue_2, bankAccount=bank_account_2)

    # settlement batch
    batch_1 = factories.SettlementBatchFactory.create(name="VIR1", dateValidated=now - datetime.timedelta(days=3))
    batch_2 = factories.SettlementBatchFactory.create(name="VIR2", dateValidated=now - datetime.timedelta(days=2))
    batch_3 = factories.SettlementBatchFactory.create(name="VIR3-1", dateValidated=now - datetime.timedelta(days=1))
    batch_4 = factories.SettlementBatchFactory.create(name="VIR4", dateValidated=now - datetime.timedelta(days=5))

    # settlement on batch 1, bank account 1, two invoices (positive and negative amount)
    settlement_1 = factories.SettlementFactory.create(
        status=models.SettlementStatus.EXECUTED,
        amount=10000,
        bankAccount=bank_account_1,
        batch=batch_1,
        invoices=[
            factories.InvoiceFactory.create(amount=-15000, bankAccount=bank_account_1, date=batch_1.dateValidated),
            factories.InvoiceFactory.create(amount=5000, bankAccount=bank_account_1, date=batch_1.dateValidated),
        ],
    )
    _generate_fake_invoice_pdfs(settlement_1)
    # settlement on batch 1, bank account 1, three invoices
    settlement_2 = factories.SettlementFactory.create(
        status=models.SettlementStatus.EXECUTED,
        amount=30000,
        bankAccount=bank_account_1,
        batch=batch_1,
        invoices=[
            factories.InvoiceFactory.create(amount=-5000, bankAccount=bank_account_1, date=batch_1.dateValidated),
            factories.InvoiceFactory.create(amount=-10000, bankAccount=bank_account_1, date=batch_2.dateValidated),
            factories.InvoiceFactory.create(amount=-15000, bankAccount=bank_account_1, date=batch_3.dateValidated),
        ],
    )
    _generate_fake_invoice_pdfs(settlement_2)
    # settlement on batch 2, bank account 2, two invoices, one is not PAID
    settlement_3 = factories.SettlementFactory.create(
        status=models.SettlementStatus.EXECUTED,
        amount=5000,
        bankAccount=bank_account_2,
        batch=batch_2,
        invoices=[
            factories.InvoiceFactory.create(amount=-3000, bankAccount=bank_account_1, date=batch_2.dateValidated),
            factories.InvoiceFactory.create(
                amount=-2000,
                bankAccount=bank_account_2,
                date=batch_2.dateValidated,
                status=models.InvoiceStatus.PENDING_PAYMENT,
            ),
        ],
    )
    _generate_fake_invoice_pdfs(settlement_3)
    # settlement on batch 3, bank account 2, one invoice
    settlement_4 = factories.SettlementFactory.create(
        status=models.SettlementStatus.EXECUTED,
        amount=4000,
        bankAccount=bank_account_2,
        batch=batch_3,
        invoices=[
            factories.InvoiceFactory.create(amount=-4000, bankAccount=bank_account_2, date=batch_2.dateValidated),
        ],
    )
    _generate_fake_invoice_pdfs(settlement_4)
    # settlement on batch 3, bank account 2, no invoice
    settlement_5 = factories.SettlementFactory.create(
        status=models.SettlementStatus.EXECUTED,
        amount=5000,
        bankAccount=bank_account_2,
        batch=batch_3,
    )
    _generate_fake_invoice_pdfs(settlement_5)

    # rejected settlement on batch 4, refused bank account
    # when a settlement is rejected, the bank account is refused and the linked venues are detached
    settlement_6 = factories.SettlementFactory.create(
        status=models.SettlementStatus.REJECTED,
        amount=30000,
        bankAccount=refused_bank_account,
        batch=batch_4,
        invoices=[
            factories.InvoiceFactory.create(
                amount=-30000, bankAccount=refused_bank_account, date=batch_4.dateValidated
            ),
        ],
    )
    _generate_fake_invoice_pdfs(settlement_6)


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
    settlement = factories.SettlementFactory.create(
        status=models.SettlementStatus.REJECTED, amount=10000, bankAccount=bank_account, batch=batch, invoices=[invoice]
    )
    _generate_fake_invoice_pdfs(settlement)


@log_func_duration
def create_rejected_processed_solved_settlements(user: users_models.User) -> None:
    """
    A rejected settlement is considered 'processed' if the structures previously linked to the rejected bank account are linked to a valid bank account
    A rejected settlement is considered 'solved' if a new settlement is executed and is linked to the rejected settlement invoices
    """

    now = date_utils.get_naive_utc_now()

    offerer = offerers_factories.OffererFactory.create(name="Entité pro finance avec rejets traités")
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

    # the batch occurred 5 days ago with 2 rejected settlements, in sync with the bank account status
    batch = factories.SettlementBatchFactory.create(name="VIR11", dateValidated=now - datetime.timedelta(days=5))
    invoice_1 = factories.InvoiceFactory.create(amount=-10000, bankAccount=bank_account, date=batch.dateValidated)
    settlement_1 = factories.SettlementFactory.create(
        status=models.SettlementStatus.REJECTED,
        amount=10000,
        bankAccount=bank_account,
        batch=batch,
        invoices=[invoice_1],
    )
    _generate_fake_invoice_pdfs(settlement_1)
    invoice_2 = factories.InvoiceFactory.create(amount=-5000, bankAccount=bank_account, date=batch.dateValidated)
    settlement_2 = factories.SettlementFactory.create(
        status=models.SettlementStatus.REJECTED,
        amount=5000,
        bankAccount=bank_account,
        batch=batch,
        invoices=[invoice_2],
    )
    _generate_fake_invoice_pdfs(settlement_2)

    # another valid bank account is now linked to the venue
    new_bank_account = factories.BankAccountFactory.create(label="Compte bancaire 5", offerer=offerer)
    offerers_factories.VenueBankAccountLinkFactory.create(
        venue=venue, bankAccount=new_bank_account, timespan=[now - datetime.timedelta(days=4), None]
    )

    # a new settlement is executed on the new bank account, linked to the second rejected settlement invoice
    new_batch = factories.SettlementBatchFactory.create(name="VIR13", dateValidated=now - datetime.timedelta(days=3))
    factories.SettlementFactory.create(
        status=models.SettlementStatus.EXECUTED,
        amount=5000,
        bankAccount=new_bank_account,
        batch=new_batch,
        invoices=[invoice_2],
    )


def _generate_fake_invoice_pdfs(settlement: models.Settlement) -> None:
    for invoice in settlement.invoices:
        pdf_title = f"Justificatif n°{invoice.reference}"
        invoice_settlements = [s.batch.get_displayed_name() for s in invoice.settlements]
        invoice_pdf = "<h1>{title}</h1><h2>Virements associés</h2><ul>{settlement_list}</ul>".format(
            title=pdf_title,
            settlement_list="".join([f"<li>{settlement_label}</li>" for settlement_label in invoice_settlements]),
        )
        store_public_object(
            folder="invoices",
            object_id=invoice.storage_object_id,
            blob=generate_pdf_from_html(invoice_pdf),
            content_type="application/pdf",
        )
