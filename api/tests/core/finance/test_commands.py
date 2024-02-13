from unittest.mock import patch

import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings

from tests.conftest import clean_database
from tests.test_utils import run_command


class AddCustomOfferReimbursementRuleTest:
    @clean_database
    def test_basics(self, app):
        stock = offers_factories.StockFactory(price=24.68)
        offer = stock.offer
        offer_id = offer.id
        # fmt: off
        result = run_command(
            app,
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
        rule = finance_models.CustomReimbursementRule.query.one()
        assert rule.offer.id == offer_id
        assert rule.amount == 1234

    @clean_database
    def test_warnings(self, app):
        stock = offers_factories.StockFactory(price=24.68)
        offer = stock.offer
        # fmt: off
        result = run_command(
            app,
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
        assert finance_models.CustomReimbursementRule.query.count() == 0

    @clean_database
    def test_force_with_warnings(self, app):
        stock = offers_factories.StockFactory(price=24.68)
        offer = stock.offer
        offer_id = offer.id

        # fmt: off
        result = run_command(
            app,
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
        rule = finance_models.CustomReimbursementRule.query.one()
        assert rule.offer.id == offer_id
        assert rule.amount == 1234


@clean_database
def test_move_siret(app):
    offerer = offerers_factories.OffererFactory()
    siret = offerer.siren + "00001"

    src_venue_id = offerers_factories.VenueFactory(siret=siret, managingOfferer=offerer).id
    dst_venue_id = offerers_factories.VenueWithoutSiretFactory(managingOfferer=offerer).id

    result = run_command(
        app,
        "move_siret",
        "--src-venue-id",
        src_venue_id,
        "--dst-venue-id",
        dst_venue_id,
        "--siret",
        siret,
        "--comment",
        "test move siret",
        "--apply-changes",
    )

    src_venue = offerers_models.Venue.query.get(src_venue_id)
    dst_venue = offerers_models.Venue.query.get(dst_venue_id)

    assert "Siret has been moved." in result.stdout

    assert not src_venue.siret
    assert dst_venue.siret == siret


@override_settings(SLACK_GENERATE_INVOICES_FINISHED_CHANNEL="channel")
@override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
@clean_database
def test_generate_invoices_internal_notification(app, css_font_http_request_mock):
    venue = offerers_factories.VenueFactory()
    batch = finance_factories.CashflowBatchFactory()
    finance_factories.CashflowFactory.create_batch(
        size=3,
        batch=batch,
        reimbursementPoint=venue,
        status=finance_models.CashflowStatus.UNDER_REVIEW,
    )
    finance_factories.BankInformationFactory(venue=venue)

    with patch("pcapi.core.finance.commands.send_internal_message") as mock_send_internal_message:
        run_command(
            app,
            "generate_invoices",
            "--batch-id",
            str(batch.id),
        )

    assert mock_send_internal_message.call_count == 1
    call_kwargs = mock_send_internal_message.call_args.kwargs
    assert len(call_kwargs["blocks"]) == 1
    call_block = call_kwargs["blocks"][0]
    assert call_block["text"]["text"] == f"La Génération de factures ({batch.label}) est terminée avec succès"
    assert call_block["text"]["type"] == "mrkdwn"
    assert call_block["type"] == "section"

    assert call_kwargs["channel"] == "channel"
    assert call_kwargs["icon_emoji"] == ":large_green_circle:"
