import datetime
from unittest.mock import patch

import pytest
import time_machine

from pcapi.core.finance import external
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.backend.base import SettlementPayload
from pcapi.core.finance.backend.base import SettlementType
from pcapi.core.finance.backend.dummy import DummyFinanceBackend
from pcapi.core.finance.backend.dummy import bank_accounts as dummy_bank_accounts
from pcapi.core.finance.backend.dummy import invoices as dummy_invoices
from pcapi.core.offerers import factories as offerers_factories
from pcapi.models import db
from pcapi.utils import date as date_utils


pytestmark = [
    pytest.mark.usefixtures("db_session", "clean_dummy_backend_data"),
    pytest.mark.features(
        WIP_ENABLE_NEW_FINANCE_WORKFLOW=True,
        ENABLE_BANK_ACCOUNT_SYNC=True,
        ENABLE_INVOICE_SYNC=True,
    ),
]


class ExternalFinanceTest:
    def test_push_bank_accounts(self):
        offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318459")
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        assert bank_account.lastCegidSyncDate is None

        now = date_utils.get_naive_utc_now()
        with time_machine.travel(now, tick=False):
            external.push_bank_accounts(10)
        db.session.flush()
        db.session.refresh(bank_account)
        assert bank_account.lastCegidSyncDate == now
        assert len(dummy_bank_accounts) == 1
        assert dummy_bank_accounts[0] == bank_account

    def test_push_invoices(self):
        invoice1 = finance_factories.InvoiceFactory(
            status=finance_models.InvoiceStatus.PENDING, cashflows=[finance_factories.CashflowFactory()]
        )
        invoice2 = finance_factories.InvoiceFactory(
            status=finance_models.InvoiceStatus.PAID, cashflows=[finance_factories.CashflowFactory()]
        )
        invoice3 = finance_factories.InvoiceFactory(
            status=finance_models.InvoiceStatus.PENDING_PAYMENT, cashflows=[finance_factories.CashflowFactory()]
        )
        invoice4 = finance_factories.InvoiceFactory(
            status=finance_models.InvoiceStatus.REJECTED, cashflows=[finance_factories.CashflowFactory()]
        )

        external.push_invoices(10)
        db.session.flush()
        db.session.refresh(invoice1)
        db.session.refresh(invoice2)
        db.session.refresh(invoice3)
        db.session.refresh(invoice4)
        assert invoice1.status == finance_models.InvoiceStatus.PAID
        assert invoice2.status == finance_models.InvoiceStatus.PAID
        assert invoice3.status == finance_models.InvoiceStatus.PENDING_PAYMENT
        assert invoice4.status == finance_models.InvoiceStatus.REJECTED

        assert len(dummy_invoices) == 1
        assert dummy_invoices[0] == invoice1

    @pytest.mark.settings(SLACK_GENERATE_INVOICES_FINISHED_CHANNEL="channel")
    @patch("pcapi.core.finance.external.send_internal_message")
    def test_push_invoices_sends_slack_notification(self, mock_send_internal_message):
        invoices = finance_factories.InvoiceFactory.create_batch(
            5, status=finance_models.InvoiceStatus.PENDING, cashflows=[finance_factories.CashflowFactory()]
        )

        external.push_invoices(10)
        batch = invoices[0].cashflows[0].batch
        assert mock_send_internal_message.call_count == 1

        call_kwargs = mock_send_internal_message.call_args.kwargs
        assert len(call_kwargs["blocks"]) == 1
        call_block = call_kwargs["blocks"][0]
        assert (
            call_block["text"]["text"]
            == f"L'envoi des factures du ({batch.label}) sur l'outil comptable est terminé avec succès"
        )
        assert call_block["text"]["type"] == "mrkdwn"
        assert call_block["type"] == "section"

        assert call_kwargs["channel"] == "channel"
        assert call_kwargs["icon_emoji"] == ":large_green_circle:"

    @pytest.mark.parametrize(
        "check_value,expected_status",
        [
            (False, finance_models.InvoiceStatus.PENDING),
            (True, finance_models.InvoiceStatus.PAID),
        ],
    )
    def test_push_invoices_doesnt_run_during_work_hours(self, monkeypatch, check_value, expected_status):
        invoice = finance_factories.InvoiceFactory(
            status=finance_models.InvoiceStatus.PENDING, cashflows=[finance_factories.CashflowFactory()]
        )

        def check_can_push_invoice(self):
            return check_value

        monkeypatch.setattr(DummyFinanceBackend, "check_can_push_invoice", check_can_push_invoice)

        external.push_invoices(0)
        db.session.flush()
        db.session.refresh(invoice)

        assert invoice.status == expected_status

    def test_get_settlements(self):
        first_bank_account = finance_factories.BankAccountFactory()
        second_bank_account = finance_factories.BankAccountFactory()
        other_bank_account = finance_factories.BankAccountFactory()
        invoice = finance_factories.InvoiceFactory(bankAccount=first_bank_account)
        other_invoice = finance_factories.InvoiceFactory(bankAccount=other_bank_account)
        another_invoice = finance_factories.InvoiceFactory(bankAccount=other_bank_account)
        additional_bank_account = finance_factories.BankAccountFactory()
        additional_invoice = finance_factories.InvoiceFactory(bankAccount=additional_bank_account)
        existing_settlement = finance_factories.SettlementFactory(bankAccount=additional_bank_account, amount=10000)

        now = date_utils.get_naive_utc_now()

        mock_get_settlements_payload = [
            SettlementPayload(
                bank_account_id=first_bank_account.id,
                external_settlement_id="0032596",
                invoice_external_reference=invoice.reference,
                settlement_type=SettlementType.VOIDED_PAYMENT,
                settlement_batch_name=existing_settlement.batch.name,
                settlement_batch_label=existing_settlement.batch.label,
                settlement_date=now.date(),
                amount=-98280,
            ),
            SettlementPayload(
                bank_account_id=first_bank_account.id,
                external_settlement_id="0032596",
                invoice_external_reference=invoice.reference,
                settlement_type=SettlementType.PAYMENT,
                settlement_batch_name=existing_settlement.batch.name,
                settlement_batch_label=existing_settlement.batch.label,
                settlement_date=now.date(),
                amount=98280,
            ),
            SettlementPayload(
                bank_account_id=second_bank_account.id,
                external_settlement_id="0032598",
                invoice_external_reference=invoice.reference,
                settlement_type=SettlementType.PAYMENT,
                settlement_batch_name=existing_settlement.batch.name,
                settlement_batch_label=existing_settlement.batch.label,
                settlement_date=now.date(),
                amount=98280,
            ),
            SettlementPayload(
                bank_account_id=other_bank_account.id,
                external_settlement_id="0052634",
                invoice_external_reference=other_invoice.reference,
                settlement_type=SettlementType.PAYMENT,
                settlement_batch_name=existing_settlement.batch.name,
                settlement_batch_label=existing_settlement.batch.label,
                settlement_date=now.date(),
                amount=45000,
            ),
            SettlementPayload(
                bank_account_id=other_bank_account.id,
                external_settlement_id="0052634",
                invoice_external_reference=another_invoice.reference,
                settlement_type=SettlementType.PAYMENT,
                settlement_batch_name=existing_settlement.batch.name,
                settlement_batch_label=existing_settlement.batch.label,
                settlement_date=now.date(),
                amount=45000,
            ),
            SettlementPayload(
                bank_account_id=additional_bank_account.id,
                external_settlement_id=existing_settlement.externalSettlementId,
                invoice_external_reference=additional_invoice.reference,
                settlement_type=SettlementType.VOIDED_PAYMENT,
                settlement_batch_name=existing_settlement.batch.name,
                settlement_batch_label=existing_settlement.batch.label,
                settlement_date=now.date(),
                amount=-30000,
            ),
        ]

        with patch(
            "pcapi.core.finance.backend.dummy.DummyFinanceBackend.get_settlements",
            return_value=mock_get_settlements_payload,
        ):
            external.sync_settlements(datetime.date.today(), datetime.date.today())

        assert db.session.query(finance_models.SettlementBatch).count() == 1
        settlement_batch = db.session.query(finance_models.SettlementBatch).one()

        assert db.session.query(finance_models.Settlement).count() == 4

        first_settlement = (
            db.session.query(finance_models.Settlement)
            .filter(
                finance_models.Settlement.externalSettlementId == "0032596",
                finance_models.Settlement.bankAccountId == first_bank_account.id,
            )
            .one()
        )
        assert first_settlement.invoices == [invoice]
        assert first_settlement.settlementDate == datetime.date.today()
        assert first_settlement.dateImported.timestamp() == pytest.approx(now.timestamp(), rel=1)
        assert first_settlement.dateRejected.timestamp() == pytest.approx(now.timestamp(), rel=1)
        assert first_settlement.amount == 98280
        assert first_settlement.status == finance_models.SettlementStatus.REJECTED
        assert first_settlement.batch == settlement_batch

        second_settlement = (
            db.session.query(finance_models.Settlement)
            .filter(
                finance_models.Settlement.externalSettlementId == "0032598",
                finance_models.Settlement.bankAccountId == second_bank_account.id,
            )
            .one()
        )
        assert second_settlement.invoices == [invoice]
        assert second_settlement.settlementDate == datetime.date.today()
        assert second_settlement.dateImported.timestamp() == pytest.approx(now.timestamp(), rel=1)
        assert second_settlement.dateRejected == None
        assert second_settlement.amount == 98280
        assert second_settlement.status == finance_models.SettlementStatus.PENDING
        assert second_settlement.batch == settlement_batch

        other_settlement = (
            db.session.query(finance_models.Settlement)
            .filter(
                finance_models.Settlement.externalSettlementId == "0052634",
                finance_models.Settlement.bankAccountId == other_bank_account.id,
            )
            .one()
        )
        assert set(other_settlement.invoices) == {other_invoice, another_invoice}
        assert other_settlement.settlementDate == datetime.date.today()
        assert other_settlement.dateImported.timestamp() == pytest.approx(now.timestamp(), rel=1)
        assert other_settlement.dateRejected == None
        assert other_settlement.amount == 45000
        assert other_settlement.status == finance_models.SettlementStatus.PENDING
        assert other_settlement.batch == settlement_batch

        assert existing_settlement.dateRejected.timestamp() == pytest.approx(now.timestamp(), rel=1)
        assert existing_settlement.status == finance_models.SettlementStatus.REJECTED

    def test_get_settlements_ignore_when_no_bank_account_found(self, caplog):
        invoice = finance_factories.InvoiceFactory()
        settlement_batch = finance_factories.SettlementBatchFactory()

        now = date_utils.get_naive_utc_now()

        mock_get_settlements_payload = [
            SettlementPayload(
                bank_account_id=12345678,
                external_settlement_id="0032596",
                invoice_external_reference=invoice.reference,
                settlement_type=SettlementType.PAYMENT,
                settlement_batch_name=settlement_batch.name,
                settlement_batch_label=settlement_batch.label,
                settlement_date=now.date(),
                amount=30000,
            )
        ]

        with patch(
            "pcapi.core.finance.backend.dummy.DummyFinanceBackend.get_settlements",
            return_value=mock_get_settlements_payload,
        ):
            external.sync_settlements(datetime.date.today(), datetime.date.today())

        assert db.session.query(finance_models.Settlement).count() == 0

        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "WARNING"
        assert caplog.records[0].message == "No bank account found on our side for this bank account id"

    def test_get_settlements_ignore_when_no_invoice_found(self, caplog):
        bank_account = finance_factories.BankAccountFactory()
        settlement_batch = finance_factories.SettlementBatchFactory()

        now = date_utils.get_naive_utc_now()

        mock_get_settlements_payload = [
            SettlementPayload(
                bank_account_id=bank_account.id,
                external_settlement_id="0032597",
                invoice_external_reference="FINCONNUE",
                settlement_type=SettlementType.PAYMENT,
                settlement_batch_name=settlement_batch.name,
                settlement_batch_label=settlement_batch.label,
                settlement_date=now.date(),
                amount=30000,
            )
        ]

        with patch(
            "pcapi.core.finance.backend.dummy.DummyFinanceBackend.get_settlements",
            return_value=mock_get_settlements_payload,
        ):
            external.sync_settlements(datetime.date.today(), datetime.date.today())

        assert db.session.query(finance_models.Settlement).count() == 0

        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "WARNING"
        assert caplog.records[0].message == "No invoice found on our side for this reference"

    def test_get_settlements_ignore_when_no_batch_found(self, caplog):
        bank_account = finance_factories.BankAccountFactory()
        invoice = finance_factories.InvoiceFactory(bankAccount=bank_account)

        now = date_utils.get_naive_utc_now()

        mock_get_settlements_payload = [
            SettlementPayload(
                bank_account_id=bank_account.id,
                external_settlement_id="0032597",
                invoice_external_reference=invoice.reference,
                settlement_type=SettlementType.PAYMENT,
                settlement_batch_name=None,
                settlement_batch_label=None,
                settlement_date=now.date(),
                amount=30000,
            )
        ]

        with patch(
            "pcapi.core.finance.backend.dummy.DummyFinanceBackend.get_settlements",
            return_value=mock_get_settlements_payload,
        ):
            external.sync_settlements(datetime.date.today(), datetime.date.today())

        assert db.session.query(finance_models.Settlement).count() == 0

        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "WARNING"
        assert caplog.records[0].message == "No settlement batch in the payload"

    def test_get_settlements_ignore_when_no_payment_settlement_found(self, caplog):
        bank_account = finance_factories.BankAccountFactory()
        invoice = finance_factories.InvoiceFactory(bankAccount=bank_account)
        settlement_batch = finance_factories.SettlementBatchFactory()

        now = date_utils.get_naive_utc_now()

        mock_get_settlements_payload = [
            SettlementPayload(
                bank_account_id=bank_account.id,
                external_settlement_id="0032597",
                invoice_external_reference=invoice.reference,
                settlement_type=SettlementType.VOIDED_PAYMENT,
                settlement_batch_name=settlement_batch.name,
                settlement_batch_label=settlement_batch.label,
                settlement_date=now.date(),
                amount=-30000,
            )
        ]

        with patch(
            "pcapi.core.finance.backend.dummy.DummyFinanceBackend.get_settlements",
            return_value=mock_get_settlements_payload,
        ):
            external.sync_settlements(datetime.date.today(), datetime.date.today())

        assert db.session.query(finance_models.Settlement).count() == 0

        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "WARNING"
        assert caplog.records[0].message == "No settlement to cancel found"


class ExternalFinanceCommandTest:
    def test_push_bank_accounts_command(self, run_command, mocker):
        push_bank_accounts_mock = mocker.patch("pcapi.core.finance.external.push_bank_accounts")
        run_command("push_bank_accounts", raise_on_error=True)

        assert push_bank_accounts_mock.call_count == 1

    @pytest.mark.features(ENABLE_BANK_ACCOUNT_SYNC=False)
    def test_push_bank_accounts_command_feature_toggle(self, run_command, mocker):
        push_bank_accounts_mock = mocker.patch("pcapi.core.finance.external.push_bank_accounts")
        run_command("push_bank_accounts", raise_on_error=True)

        assert push_bank_accounts_mock.call_count == 0

    @pytest.mark.features(ENABLE_INVOICE_SYNC=False)
    def test_push_invoices_command_feature_toggle(self, run_command, mocker):
        push_invoices_mock = mocker.patch("pcapi.core.finance.external.push_invoices")
        run_command("push_invoices", raise_on_error=True)

        assert push_invoices_mock.call_count == 0

    def test_push_invoices_command(self, run_command, mocker):
        push_invoices_mock = mocker.patch("pcapi.core.finance.external.push_invoices")
        run_command("push_invoices", raise_on_error=True)

        assert push_invoices_mock.call_count == 1

    def test_sync_settlements_command(self, run_command, mocker):
        sync_settlements_mock = mocker.patch("pcapi.core.finance.external.sync_settlements")
        run_command("sync_settlements", raise_on_error=True)

        assert sync_settlements_mock.call_count == 1
