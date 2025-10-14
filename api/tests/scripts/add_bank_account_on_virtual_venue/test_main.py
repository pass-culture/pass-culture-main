import pytest

from pcapi.core.finance import factories as finance_factories
from pcapi.core.history import models as history_models
from pcapi.core.history.models import ActionType
from pcapi.core.offerers import factories as offerers_factories
from pcapi.models import db
from pcapi.scripts.add_bank_account_on_virtual_venue import main


pytestmark = pytest.mark.usefixtures("db_session")


def test_add_bank_account_virtual_venue():
    virtual_venue = offerers_factories.VirtualVenueFactory.create(id=485)
    ba = finance_factories.BankAccountFactory.create()
    offerers_factories.VenueBankAccountLinkFactory.create(
        venue=virtual_venue,
        bankAccount=ba,
    )

    new_ba = finance_factories.BankAccountFactory.create(id=50836)
    main.main(not_dry=True)
    assert virtual_venue.current_bank_account == new_ba
    action_deprecated_ba = (
        db.session.query(history_models.ActionHistory)
        .filter_by(
            actionType=ActionType.LINK_VENUE_BANK_ACCOUNT_DEPRECATED,
            venueId=virtual_venue.id,
            bankAccountId=ba.id,
            comment="PC-38354",
        )
        .one()
    )
    assert action_deprecated_ba is not None
    action_created_ba = (
        db.session.query(history_models.ActionHistory)
        .filter_by(
            actionType=ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
            venueId=virtual_venue.id,
            bankAccountId=new_ba.id,
            comment="PC-38354",
        )
        .one()
    )
    assert action_created_ba is not None


def test_add_bank_account_virtual_venue_no_previous_ba():
    virtual_venue = offerers_factories.VirtualVenueFactory.create(id=485)

    new_ba = finance_factories.BankAccountFactory.create(id=50836)
    main.main(not_dry=True)
    assert virtual_venue.current_bank_account == new_ba
    action_created_ba = (
        db.session.query(history_models.ActionHistory)
        .filter_by(
            actionType=ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
            venueId=virtual_venue.id,
            bankAccountId=new_ba.id,
            comment="PC-38354",
        )
        .one()
    )
    assert action_created_ba is not None
