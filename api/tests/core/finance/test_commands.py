import decimal

import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
from pcapi.utils import human_ids

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
            "--offer-humanized-id", human_ids.humanize(offer.id),
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
        assert rule.amount == decimal.Decimal("12.34")

    @clean_database
    def test_warnings(self, app):
        stock = offers_factories.StockFactory(price=24.68)
        offer = stock.offer
        # fmt: off
        result = run_command(
            app,
            "add_custom_offer_reimbursement_rule",
            "--offer-humanized-id", human_ids.humanize(offer.id),
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
            "--offer-humanized-id", human_ids.humanize(offer.id),
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
        assert rule.amount == decimal.Decimal("12.34")


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
