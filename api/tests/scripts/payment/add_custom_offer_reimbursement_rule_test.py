import decimal

import pytest

import pcapi.core.offers.factories as offers_factories
import pcapi.core.payments.models as payments_models
from pcapi.utils import human_ids


pytestmark = pytest.mark.usefixtures("db_session")


def _run_command(app, *args):
    runner = app.test_cli_runner()
    args = ("add_custom_offer_reimbursement_rule",) + args
    return runner.invoke(args=args)


def test_basics(app):
    stock = offers_factories.StockFactory(price=24.68)
    offer = stock.offer
    # fmt: off
    result = _run_command(
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
    rule = payments_models.CustomReimbursementRule.query.one()
    assert rule.offer.id == offer.id
    assert rule.amount == decimal.Decimal("12.34")


def test_warnings(app):
    stock = offers_factories.StockFactory(price=24.68)
    offer = stock.offer
    # fmt: off
    result = _run_command(
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
    assert payments_models.CustomReimbursementRule.query.count() == 0


def test_force_with_warnings(app):
    stock = offers_factories.StockFactory(price=24.68)
    offer = stock.offer
    # fmt: off
    result = _run_command(
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
    rule = payments_models.CustomReimbursementRule.query.one()
    assert rule.offer.id == offer.id
    assert rule.amount == decimal.Decimal("12.34")
