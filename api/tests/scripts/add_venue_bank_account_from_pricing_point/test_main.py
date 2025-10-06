import typing

import pytest

from pcapi.core.finance import factories as finance_factories
from pcapi.core.history import models as history_models
from pcapi.core.history.models import ActionType
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as finance_models
from pcapi.models import db
from pcapi.scripts.add_venue_bank_account_from_pricing_point import main


pytestmark = pytest.mark.usefixtures("db_session")


def fake_iterator(origin_venue_id) -> typing.Iterator[dict]:
    yield {"origin_venue_id": str(origin_venue_id)}


def test_add_bank_account_to_venue_without_bank_account(monkeypatch):
    origin_venue = offerers_factories.VenueFactory.create()
    pricing_point_venue = offerers_factories.VenueFactory.create()
    bank_account = finance_factories.BankAccountFactory.create()
    offerers_factories.VenueBankAccountLinkFactory.create(
        venue=pricing_point_venue,
        bankAccount=bank_account,
    )
    offerers_factories.VenuePricingPointLinkFactory.create(
        venue=origin_venue,
        pricingPoint=pricing_point_venue,
    )
    offerers_factories.VenuePricingPointLinkFactory.create(
        venue=pricing_point_venue,
        pricingPoint=pricing_point_venue,
    )

    monkeypatch.setattr(main, "_get_rows", lambda: fake_iterator(origin_venue.id))

    main.main(not_dry=True)

    link = (
        db.session.query(finance_models.VenueBankAccountLink)
        .filter_by(venueId=origin_venue.id, bankAccountId=bank_account.id)
        .first()
    )
    assert link is not None

    action = (
        db.session.query(history_models.ActionHistory)
        .filter_by(
            actionType=ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
            venueId=origin_venue.id,
            bankAccountId=bank_account.id,
        )
        .first()
    )
    assert action is not None


def test_add_bank_account_to_venue_with_bank_account(monkeypatch):
    origin_venue = offerers_factories.VenueFactory()
    bank_account = finance_factories.BankAccountFactory()
    offerers_factories.VenueBankAccountLinkFactory(
        venue=origin_venue,
        bankAccountId=bank_account,
    )

    pricing_point_venue = offerers_factories.VenueFactory()
    bank_account_2 = finance_factories.BankAccountFactory()
    offerers_factories.VenueBankAccountLinkFactory(
        venue=pricing_point_venue,
        bankAccount=bank_account_2,
    )
    offerers_factories.VenuePricingPointLinkFactory.create(
        venue=origin_venue,
        pricingPoint=pricing_point_venue,
    )
    offerers_factories.VenuePricingPointLinkFactory.create(
        venue=pricing_point_venue,
        pricingPoint=pricing_point_venue,
    )

    monkeypatch.setattr(main, "_get_rows", lambda: fake_iterator(origin_venue.id))

    main.main(not_dry=True)

    link = (
        db.session.query(finance_models.VenueBankAccountLink)
        .filter_by(venueId=origin_venue.id, bankAccountId=bank_account_2.id)
        .first()
    )
    assert link is None
