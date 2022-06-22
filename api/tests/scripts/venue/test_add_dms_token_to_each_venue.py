import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
from pcapi.scripts.venue.add_dms_token_to_each_venue import add_dmsToken_to_each_venue


class AddDmsTokenToEachVenueTest:
    @pytest.mark.usefixtures("db_session")
    def test_add_dmsToken_to_each_venue(self):
        offerers_factories.VenueFactory.create_batch(size=3)
        offerers_models.Venue.query.update({"dmsToken": None}, synchronize_session=False)
        offerers_factories.VenueFactory()
        assert offerers_models.Venue.query.filter(offerers_models.Venue.dmsToken.is_(None)).count() == 3

        add_dmsToken_to_each_venue(batch_size=2)

        assert offerers_models.Venue.query.filter(offerers_models.Venue.dmsToken.is_(None)).count() == 0
