import pytest

from pcapi.core.finance.models import BankAccountApplicationStatus
from pcapi.core.offerers import factories as offerers_factories
from pcapi.routes.serialization.venues_serialize import SimplifiedBankAccountStatus
from pcapi.routes.serialization.venues_serialize import parse_venue_bank_account_status


pytestmark = pytest.mark.usefixtures("db_session")


def build_bank_account_link(**kwargs):
    if "status" in kwargs:
        kwargs["status"] = BankAccountApplicationStatus[kwargs["status"]]
    kwargs = {f"bankAccount__{k}": v for k, v in kwargs.items()}
    return offerers_factories.VenueBankAccountLinkFactory(**kwargs)


class ParseVenueBankAccountStatusTest:
    @pytest.mark.parametrize(
        "build_status, expected_status",
        [
            pytest.param("DRAFT", SimplifiedBankAccountStatus.PENDING, id="draft-pending"),
            pytest.param("ON_GOING", SimplifiedBankAccountStatus.PENDING, id="ongoing-pending"),
            pytest.param("ACCEPTED", SimplifiedBankAccountStatus.VALID, id="accepted-valid"),
            pytest.param("REFUSED", None, id="refused-none"),
            pytest.param("WITHOUT_CONTINUATION", None, id="refused-none"),
            pytest.param(
                "WITH_PENDING_CORRECTIONS",
                SimplifiedBankAccountStatus.PENDING_CORRECTIONS,
                id="with_pending_corrections-pending_corrections",
            ),
        ],
    )
    def test_venue_with_bank_account_status_returns_expected_value(self, build_status, expected_status):
        venue = offerers_factories.VenueFactory(bankAccountLinks=[build_bank_account_link(status=build_status)])
        assert parse_venue_bank_account_status(venue) == expected_status

    def test_venue_without_bank_account_returns_none(self):
        venue = offerers_factories.VenueFactory(bankAccountLinks=[])
        assert not parse_venue_bank_account_status(venue)

    def test_venue_with_inactive_bank_account_returns_none(self):
        venue = offerers_factories.VenueFactory(
            bankAccountLinks=[build_bank_account_link(status="DRAFT", isActive=False)]
        )
        assert not parse_venue_bank_account_status(venue)
