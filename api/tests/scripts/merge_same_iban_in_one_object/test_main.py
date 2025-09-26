from datetime import datetime

import pytest

import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.factories as offerer_factories
from pcapi.models import db
from pcapi.scripts.merge_same_iban_in_one_object.main import main


pytestmark = pytest.mark.usefixtures("db_session")


IBAN = "FR7630004000500060007000800"
OTHER_IBAN = "FR7630004000500060007000899"


def test_merge_multiple_bank_account_with_unique_iban():
    offerer = offerer_factories.OffererFactory()
    venues = offerer_factories.VenueFactory.create_batch(5, managingOfferer=offerer)
    for venue in venues[:-1]:
        bank_account_link = offerer_factories.VenueBankAccountLinkFactory.create(
            venue=venue,
            bankAccount__iban=IBAN,
            timespan=(datetime(2020, 1, 1), datetime(2022, 1, 1)),
        )
        offerer_factories.VenueBankAccountLinkFactory.create(
            venue=venue,
            bankAccount=bank_account_link.bankAccount,
        )
    assert db.session.query(finance_models.BankAccount).count() == 4
    assert venues[0].current_bank_account.iban == IBAN

    main(dry_run=False, offerer_ids=[offerer.id])

    # We only have 1 active IBAN left
    assert db.session.query(finance_models.BankAccount).filter(finance_models.BankAccount.isActive == True).count() == 1
    # Ensure all venues have active bank account
    for venue in venues[:-1]:
        db.session.refresh(venue)
        for bank_account_link in venue.bankAccountLinks:
            db.session.refresh(bank_account_link)
        assert venue.current_bank_account.iban == IBAN
        assert venue.current_bank_account.isActive
    # Ensure all venues share the same bank account
    assert len({venue.current_bank_account.id for venue in venues[:-1]}) == 1
    # Last venue should not have any bank account
    assert venues[-1].current_bank_account is None


def test_merge_multiple_ibans_should_fail():
    offerer = offerer_factories.OffererFactory()
    venues = offerer_factories.VenueFactory.create_batch(3, managingOfferer=offerer)
    offerer_factories.VenueBankAccountLinkFactory.create(
        venue=venues[0],
        bankAccount__iban=IBAN,
    )
    offerer_factories.VenueBankAccountLinkFactory.create(
        venue=venues[1],
        bankAccount__iban=OTHER_IBAN,
    )
    offerer_factories.VenueBankAccountLinkFactory.create(
        venue=venues[2],
        bankAccount__iban=IBAN,
    )
    assert db.session.query(finance_models.BankAccount).count() == 3
    assert (
        db.session.query(finance_models.BankAccount).with_entities(finance_models.BankAccount.iban).distinct().count()
        == 2
    )

    main(dry_run=False, offerer_ids=[offerer.id])

    assert db.session.query(finance_models.BankAccount).count() == 3
