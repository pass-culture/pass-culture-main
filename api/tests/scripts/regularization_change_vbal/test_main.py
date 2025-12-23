from unittest.mock import patch

import pytest

from pcapi.core.finance import factories as finance_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.models import db
from pcapi.scripts.regularization_change_vbal.main import main
from pcapi.utils import date as date_utils


pytestmark = pytest.mark.usefixtures("db_session")


def test_clean_action_history():
    venue_0 = offerers_factories.VenueFactory()
    venue_1 = offerers_factories.VenueFactory()
    venue_2 = offerers_factories.VenueFactory(managingOfferer=venue_1.managingOfferer)

    bank_account = finance_factories.BankAccountFactory()
    wrong_bank_account = finance_factories.BankAccountFactory()
    current_timerange = (date_utils.get_naive_utc_now(), None)
    current_vbal = offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_0, bankAccount=bank_account, timespan=current_timerange
    )
    deprecated_vbal = offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_1, bankAccount=wrong_bank_account, timespan=current_timerange
    )
    db.session.add(deprecated_vbal)
    db.session.refresh(deprecated_vbal)
    db.session.commit()

    mock_csv_rows = [
        {
            "venue_id": str(venue_0.id),
            "bank_account_id": str(bank_account.id),
        },  # already linked
        {
            "venue_id": str(venue_1.id),
            "bank_account_id": str(bank_account.id),
        },
        {
            "venue_id": str(venue_2.id),
            "bank_account_id": str(bank_account.id),
        },
        {
            "venue_id": str(venue_2.id),
            "bank_account_id": str(bank_account.id),
        },  # introduce some mistake in the file : should not create new vbal
    ]

    with patch("pcapi.scripts.regularization_change_vbal.main._read_csv_file", return_value=iter(mock_csv_rows)):
        main(not_dry=True, filename="test_file")

    assert current_vbal.timespan.upper is None
    assert deprecated_vbal.timespan.upper is not None
    assert venue_0.current_bank_account == bank_account
    assert venue_1.current_bank_account == bank_account
    assert venue_2.current_bank_account == bank_account
