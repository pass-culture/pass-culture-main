import io

import pytest

import pcapi.core.users.factories as users_factories
from pcapi.scripts.catching_up_dms_beneficiaries_addresses import _process_file


CSV = """,email,adresse
1,bob@example.com,26 Avenue du test 99999 Testing
2,georges@example.com,36 Avenue de nulle part 99999 Testing
3,alice@example.com,13 Rue du test 99999 Testing
"""


@pytest.mark.usefixtures("db_session")
class CatchingUpDMSBeneficiariesAddressesTest:
    def test_catching_up_dms_beneficiaries_addresses(self):
        # Given
        alice = users_factories.BeneficiaryFactory(id=1, firstName="Alice", email="alice@example.com", address=None)
        bob = users_factories.BeneficiaryFactory(id=2, firstName="Bob", email="bob@example.com", address=None)

        csv_file = io.StringIO(CSV)

        # When
        _process_file(csv_file)

        # Then
        assert alice.address == "13 Rue du test 99999 Testing"
        assert bob.address == "26 Avenue du test 99999 Testing"
