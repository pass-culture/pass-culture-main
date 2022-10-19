import decimal

import pcapi.core.finance.models as finance_models
import pcapi.core.offers.factories as offers_factories
from pcapi.utils import human_ids

from tests.conftest import clean_database


class AddCustomOfferReimbursementRuleTest:
    def _run_command(self, app, *args):
        runner = app.test_cli_runner()
        args = ("add_custom_offer_reimbursement_rule",) + args
        return runner.invoke(args=args)

    @clean_database
    def test_basics(self, app):
        stock = offers_factories.StockFactory(price=24.68)
        offer = stock.offer
        offer_id = offer.id
        # fmt: off
        result = self._run_command(
            app,
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
        result = self._run_command(
            app,
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
        result = self._run_command(
            app,
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
