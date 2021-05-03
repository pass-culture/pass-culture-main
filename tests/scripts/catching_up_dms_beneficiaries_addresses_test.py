import io

import pytest

import pcapi.core.users.factories as users_factories
from pcapi.scripts.catching_up_dms_beneficiaries_addresses import _read_file


CSV = """beneficiary_id,application_id,source,user_address
1,808563,demarches_simplifiees,13 Rue du test 99999 Testing
2,808564,demarches_simplifiees,26 Avenue du test 99999 Testing
"""


@pytest.mark.usefixtures("db_session")
class CatchingUpDMSBeneficiariesAddressesTest:
    def test_catching_up_dms_beneficiaries_addresses(self):
        alice = users_factories.UserFactory(id=1, firstName="Alice", address=None)
        bob = users_factories.UserFactory(id=2, firstName="Bob", address=None)
        assert alice.address is None
        assert bob.address is None

        csv_file = io.StringIO(CSV)
        _read_file(csv_file)

        assert alice.address == "13 Rue du test 99999 Testing"
        assert bob.address == "26 Avenue du test 99999 Testing"
