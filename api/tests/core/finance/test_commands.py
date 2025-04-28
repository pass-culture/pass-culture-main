import datetime
from decimal import Decimal
import logging
from unittest.mock import patch

import pytest
import time_machine

from pcapi import settings
from pcapi.connectors.dms import factories as dms_factories
from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.users import factories as users_factories
from pcapi.models import db


pytestmark = [
    pytest.mark.features(WIP_ENABLE_NEW_FINANCE_WORKFLOW=True),
]


class AddCustomOfferReimbursementRuleTest:
    def test_basics(self, run_command):
        stock = offers_factories.StockFactory(price=24.68)
        offer = stock.offer
        offer_id = offer.id
        # fmt: off
        result = run_command(
            "add_custom_offer_reimbursement_rule",
            "--offer-id", offer.id,
            "--offer-original-amount", "24,68",
            "--offerer-id", str(offer.venue.managingOffererId),
            "--reimbursed-amount", "12.34",
            "--valid-from", "2030-01-01",
            "--valid-until", "2030-01-02",
        )

        # fmt: on
        assert "Created new rule" in result.output
        rule = db.session.query(finance_models.CustomReimbursementRule).one()
        assert rule.offer.id == offer_id
        assert rule.amount == 1234

    def test_warnings(self, run_command):
        stock = offers_factories.StockFactory(price=24.68)
        offer = stock.offer
        # fmt: off
        result = run_command(
            "add_custom_offer_reimbursement_rule",
            "--offer-id", offer.id,
            "--offer-original-amount", "0,34",  # wrong amount
            "--offerer-id", str(offer.venue.managingOffererId + 7),
            "--reimbursed-amount", "12.34",
            "--valid-from", "2030-01-01",
            "--valid-until", "2030-01-02",
        )
        # fmt: on
        assert "Command has failed" in result.output
        assert "Mismatch on offerer" in result.output
        assert "Mismatch on original amount" in result.output
        assert db.session.query(finance_models.CustomReimbursementRule).count() == 0

    def test_force_with_warnings(self, run_command):
        stock = offers_factories.StockFactory(price=24.68)
        offer = stock.offer
        offer_id = offer.id

        # fmt: off
        result = run_command(
            "add_custom_offer_reimbursement_rule",
            "--offer-id", offer.id,
            "--offer-original-amount", "0,34",  # wrong amount
            "--offerer-id", str(offer.venue.managingOffererId + 7),
            "--reimbursed-amount", "12.34",
            "--valid-from", "2030-01-01",
            "--valid-until", "2030-01-02",
            "--force",
        )
        # fmt: on
        assert "Created new rule" in result.output
        rule = db.session.query(finance_models.CustomReimbursementRule).one()
        assert rule.offer.id == offer_id
        assert rule.amount == 1234


def test_generate_invoices_warning(run_command, caplog):
    caplog.at_level(logging.WARNING, logger="pcapi.core.finance.commands")
    offerer = offerers_factories.OffererFactory()
    bank_account = finance_factories.BankAccountFactory(offerer=offerer)
    batch = finance_factories.CashflowBatchFactory()
    finance_factories.CashflowFactory.create_batch(
        size=3,
        batch=batch,
        bankAccount=bank_account,
        status=finance_models.CashflowStatus.UNDER_REVIEW,
    )

    run_command(
        "generate_invoices",
        "--batch-id",
        str(batch.id),
    )
    assert len(caplog.records) == 1
    log_record = caplog.records[0]
    assert log_record.message == (
        "Standalone `generate_invoices` command is deprecated. "
        "It's integrated in `generate_cashflows_and_payment_files` command."
    )


@pytest.mark.usefixtures("css_font_http_request_mock")
def test_generate_cashflows_calls_generate_invoices(run_command):
    offerer = offerers_factories.OffererFactory()
    bank_account = finance_factories.BankAccountFactory(offerer=offerer)
    venue = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point="self", bank_account=bank_account)
    past = datetime.datetime.utcnow() - datetime.timedelta(days=1)

    with time_machine.travel(past):
        user = users_factories.BeneficiaryGrant18Factory()
        booking = bookings_factories.BookingFactory(
            user=user,
            quantity=13,
            stock__price=Decimal("5.0"),
            stock__offer__venue=venue,
        )
        bookings_api.mark_as_used(
            booking=booking,
            validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
        )
        assert len(booking.finance_events) == 1

        pricing = finance_api.price_event(booking.finance_events[0])
    run_command("generate_cashflows_and_payment_files", raise_on_error=True)

    db.session.add(pricing)
    db.session.flush()
    assert len(pricing.cashflows) == 1
    cashflow = pricing.cashflows[0]
    assert cashflow.status == finance_models.CashflowStatus.PENDING_ACCEPTANCE


@pytest.mark.usefixtures("db_session")
class ImportDsBankInformationApplicationsTest:
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_pro_bank_nodes_states")
    def test_import_ds_bank_information_applications(self, mock_get_pro_bank_nodes_states, run_command):
        latest_import_date = dms_factories.LatestDmsImportFactory(
            procedureId=settings.DS_BANK_ACCOUNT_PROCEDURE_ID
        ).latestImportDatetime

        run_command("import_ds_bank_information_applications", raise_on_error=True)

        mock_get_pro_bank_nodes_states.assert_called_once_with(
            procedure_number=int(settings.DS_BANK_ACCOUNT_PROCEDURE_ID),
            since=latest_import_date,
        )

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_pro_bank_nodes_states")
    def test_import_ds_bank_information_applications_ignore_previous(self, mock_get_pro_bank_nodes_states, run_command):
        dms_factories.LatestDmsImportFactory(procedureId=settings.DS_BANK_ACCOUNT_PROCEDURE_ID)

        run_command("import_ds_bank_information_applications", "--ignore_previous", raise_on_error=True)

        mock_get_pro_bank_nodes_states.assert_called_once_with(
            procedure_number=int(settings.DS_BANK_ACCOUNT_PROCEDURE_ID),
            since=None,
        )

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_pro_bank_nodes_states")
    def test_import_ds_bank_information_applications_since(self, mock_get_pro_bank_nodes_states, run_command):
        dms_factories.LatestDmsImportFactory(procedureId=settings.DS_BANK_ACCOUNT_PROCEDURE_ID)

        run_command("import_ds_bank_information_applications", "--since", "2024-01-01", raise_on_error=True)

        mock_get_pro_bank_nodes_states.assert_called_once_with(
            procedure_number=int(settings.DS_BANK_ACCOUNT_PROCEDURE_ID),
            since=datetime.datetime(2024, 1, 1, 0, 0, 0),
        )
