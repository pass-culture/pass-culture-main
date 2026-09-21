from unittest.mock import patch

import pytest

from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.scripts.acceslibre_sync import main


pytestmark = pytest.mark.usefixtures("db_session")


def test_acceslibre_sync():
    address = geography_factories.AddressFactory()
    for _ in range(3):
        venue = offerers_factories.VenueFactory(
            isOpenToPublic=True,
            accessibilityProvider=offerers_factories.AccessibilityProviderFactory(),
            offererAddress__address=address,
        )
        assert venue.offererAddress.address

    # 1. COUNT (=3 venues)
    # 2. SELECT batch 1
    # 3. SELECT batch 2
    expected_queries_sync = 3

    with assert_num_queries(expected_queries_sync):
        main._synchronize_accessibility_with_acceslibre(
            apply=True,
            force_sync=False,
            batch_size=2,
            start_from_batch=1,
        )


@patch("pcapi.connectors.acceslibre.get_accessibility_infos")
@patch("pcapi.connectors.acceslibre.find_new_entries_by_activity")
def test_acceslibre_match(
    mock_find_new_entries,
    mock_get_accessibility_infos,
):
    mock_get_accessibility_infos.return_value = (None, None)
    mock_find_new_entries.return_value = []

    address = geography_factories.AddressFactory()
    for _ in range(5):
        venue = offerers_factories.VenueFactory(
            isOpenToPublic=True,
            accessibilityProvider=offerers_factories.AccessibilityProviderFactory(),
            offererAddress__address=address,
        )
        assert venue.offererAddress.address

    for _ in range(15):  # 15 venues sans synchro acceslibre
        venue = offerers_factories.VenueFactory(
            isOpenToPublic=True, accessibilityProvider=None, offererAddress__address=address
        )
        assert venue.offererAddress.address

    # nombre de query pour _synchronize_accessibility_with_acceslibre
    # 1. COUNT venues synchro avant matching
    # 2. COUNT venues sans acceslibre
    # 3. SELECT batch 1 venues + joinedload offererAddress + joinedload address
    # 4. SELECT batch 2 venues + joinedload offererAddress + joinedload address
    # 5. COUNT venues synchro après matching

    expected_queries_matching = 5

    with assert_num_queries(expected_queries_matching):
        main._acceslibre_matching(
            batch_size=10,
            apply=True,
            start_from_batch=1,
            n_days_to_fetch=7,
        )
