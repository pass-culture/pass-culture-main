import datetime

import pytest

# from pcapi.core.fraud import models as fraud_models  # noqa: F401 to avoid circular import
import pcapi.core.offerers.factories as offerers_factories
import pcapi.utils.db as db_utils
from pcapi.core.finance import factories
from pcapi.scripts.move_specific_bank_account.main import main


pytestmark = pytest.mark.usefixtures("db_session")


def test_move_specific_bank_account():
    user_offerer = offerers_factories.UserOffererFactory()
    venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    bank_account1 = factories.BankAccountFactory(offerer=user_offerer.offerer)
    bank_account2 = factories.BankAccountFactory(offerer=user_offerer.offerer)

    current_link = offerers_factories.VenueBankAccountLinkFactory(
        venue=venue,
        bankAccount=bank_account1,
        timespan=(datetime.datetime.utcnow(),),
    )
    assert venue.current_bank_account == bank_account1
    main(not_dry=True, venue_id=venue.id, bank_account_id=bank_account2.id)
    assert current_link.timespan.upper is not None
    assert venue.current_bank_account == bank_account2
