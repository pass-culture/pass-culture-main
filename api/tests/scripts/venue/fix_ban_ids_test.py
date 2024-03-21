import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.scripts.venue.fix_ban_ids import main


@pytest.mark.usefixtures("db_session")
class FixBanIdsTest:
    # TODO:
    def test_1(self, client, db_session):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user.pro@test.com")
        offerers_factories.CollectiveVenueFactory(
            name="L'encre et la plume",
            managingOfferer=user_offerer.offerer,
            collectiveDescription="Description du lieu",
        )
        main()
