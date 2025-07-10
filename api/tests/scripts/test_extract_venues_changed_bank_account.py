import csv
import datetime

import pytest

from pcapi.core.finance import api as finance_api
from pcapi.core.finance import factories as finance_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories
from pcapi.utils import human_ids


pytestmark = [
    pytest.mark.usefixtures("db_session"),
]


def test_extract_venues_changed_bank_account(monkeypatch, tmp_path):
    from pcapi.scripts.extract_venues_changed_bank_account.main import extract

    monkeypatch.setenv("OUTPUT_DIRECTORY", str(tmp_path))
    offerer = offerers_factories.OffererFactory()
    user = users_factories.UserFactory()
    bank_account1, bank_account2 = finance_factories.BankAccountFactory.create_batch(2, offerer=offerer)
    bank_account3, bank_account4, bank_account5 = finance_factories.BankAccountFactory.create_batch(3, offerer=offerer)

    venue1 = offerers_factories.VenueFactory(bank_account=bank_account1, managingOfferer=offerer, pricing_point="self")
    venue2 = offerers_factories.VenueFactory(bank_account=bank_account3, managingOfferer=offerer, pricing_point="self")

    finance_api.update_bank_account_venues_links(user=user, bank_account=bank_account1, venues_ids=set())
    finance_api.update_bank_account_venues_links(user=user, bank_account=bank_account2, venues_ids={venue1.id})

    finance_api.update_bank_account_venues_links(user=user, bank_account=bank_account3, venues_ids=set())
    finance_api.update_bank_account_venues_links(user=user, bank_account=bank_account4, venues_ids={venue2.id})
    finance_api.update_bank_account_venues_links(user=user, bank_account=bank_account4, venues_ids=set())
    finance_api.update_bank_account_venues_links(user=user, bank_account=bank_account5, venues_ids={venue2.id})

    extract(datetime.datetime.utcnow().year)

    files = list(tmp_path.iterdir())
    assert len(files) == 1
    csv_file = files[0]
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) == 2
    row1 = rows[0]
    row2 = rows[1]
    assert row1 == {
        "venue_id": str(venue1.id),
        "venue_name": venue1.name,
        "old_bank_account_id": str(bank_account1.id),
        "old_bank_account_humanized_id": human_ids.humanize(bank_account1.id),
        "old_bank_account_iban": bank_account1.iban,
        "new_bank_account1_id": str(bank_account2.id),
        "new_bank_account1_humanized_id": human_ids.humanize(bank_account2.id),
        "new_bank_account1_iban": bank_account2.iban,
        "new_bank_account2_id": "",
        "new_bank_account2_humanized_id": "",
        "new_bank_account2_iban": "",
    }
    assert row2 == {
        "venue_id": str(venue2.id),
        "venue_name": venue2.name,
        "old_bank_account_id": str(bank_account3.id),
        "old_bank_account_humanized_id": human_ids.humanize(bank_account3.id),
        "old_bank_account_iban": bank_account3.iban,
        "new_bank_account1_id": str(bank_account4.id),
        "new_bank_account1_humanized_id": human_ids.humanize(bank_account4.id),
        "new_bank_account1_iban": bank_account4.iban,
        "new_bank_account2_id": str(bank_account5.id),
        "new_bank_account2_humanized_id": human_ids.humanize(bank_account5.id),
        "new_bank_account2_iban": bank_account5.iban,
    }
