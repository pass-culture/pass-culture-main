import pytest

from pcapi.core import testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
from pcapi.utils import human_ids


pytestmark = pytest.mark.usefixtures("db_session")


class Returns201Test:
    @testing.override_features(ENABLE_NEW_BANK_INFORMATIONS_CREATION=True)
    def test_no_pre_existing_link(self, client):
        venue = offerers_factories.VenueFactory(siret=None, comment="no siret")
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=venue.managingOfferer)
        pricing_point = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        data = {"pricingPointId": pricing_point.id}

        response = client.with_session_auth("user@example.com").post(
            f"/venues/{human_ids.humanize(venue.id)}/pricing-point", json=data
        )

        assert response.status_code == 204
        new_link = offerers_models.VenuePricingPointLink.query.one()
        assert new_link.venue == venue
        assert new_link.pricingPoint == pricing_point
        assert new_link.timespan.upper is None


class Returns400Test:
    @testing.override_features(ENABLE_NEW_BANK_INFORMATIONS_CREATION=True)
    def test_pricing_point_does_not_exist(self, client):
        venue = offerers_factories.VenueFactory(siret=None, comment="no siret")
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=venue.managingOfferer)
        pricing_point_1 = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        offerers_factories.VenuePricingPointLinkFactory(venue=venue, pricingPoint=pricing_point_1)
        pre_existing_link = offerers_models.VenuePricingPointLink.query.one()
        pricing_point_2 = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        data = {"pricingPointId": pricing_point_2.id}

        response = client.with_session_auth("user@example.com").post(
            f"/venues/{human_ids.humanize(venue.id)}/pricing-point", json=data
        )
        assert response.status_code == 400
        assert response.json["code"] == "CANNOT_LINK_VENUE_TO_PRICING_POINT"
        assert offerers_models.VenuePricingPointLink.query.one() == pre_existing_link
