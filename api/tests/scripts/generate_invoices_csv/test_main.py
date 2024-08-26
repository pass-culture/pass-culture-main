import logging
from unittest.mock import patch

from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import override_settings
from pcapi.scripts.generate_invoices_csv.main import generate_invoices_csv

from tests.conftest import clean_database
from tests.test_utils import run_command


@override_settings(SLACK_GENERATE_INVOICES_FINISHED_CHANNEL="channel")
@clean_database
def test_run(caplog, app, css_font_http_request_mock):
    venue = offerers_factories.VenueFactory()
    batch = finance_factories.CashflowBatchFactory()
    bank_account = finance_factories.BankAccountFactory(offerer=venue.managingOfferer)
    finance_factories.CashflowFactory.create_batch(
        size=3,
        batch=batch,
        bankAccount=bank_account,
        status=finance_models.CashflowStatus.UNDER_REVIEW,
    )
    offerers_factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=bank_account)

    with patch("pcapi.core.finance.commands.send_internal_message") as mock_send_internal_message:
        run_command(
            app,
            "generate_invoices",
            "--batch-id",
            str(batch.id),
        )

    assert mock_send_internal_message.call_count == 1

    caplog.clear()
    with caplog.at_level(logging.INFO):
        generate_invoices_csv(batch.id)
        assert "Generated CSV invoices file" in caplog.text
        assert "Finance file has been uploaded to Google Drive" in caplog.text
        assert "Uploaded CSV invoices file to Google Drive" in caplog.text
