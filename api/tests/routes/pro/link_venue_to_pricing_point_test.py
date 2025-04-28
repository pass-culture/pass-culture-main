import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class Returns201Test:
    def test_no_pre_existing_link(self, client):
        venue = offerers_factories.VenueWithoutSiretFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=venue.managingOfferer)
        pricing_point = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        data = {"pricingPointId": pricing_point.id}

        response = client.with_session_auth("user@example.com").post(f"/venues/{venue.id}/pricing-point", json=data)

        assert response.status_code == 204
        new_link = db.session.query(offerers_models.VenuePricingPointLink).one()
        assert new_link.venue == venue
        assert new_link.pricingPoint == pricing_point
        assert new_link.timespan.upper is None


class Returns400Test:
    def test_pricing_point_does_not_exist(self, client):
        venue = offerers_factories.VenueWithoutSiretFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=venue.managingOfferer)
        pricing_point_1 = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        offerers_factories.VenuePricingPointLinkFactory(venue=venue, pricingPoint=pricing_point_1)
        pre_existing_link = db.session.query(offerers_models.VenuePricingPointLink).one()
        pricing_point_2 = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        data = {"pricingPointId": pricing_point_2.id}

        response = client.with_session_auth("user@example.com").post(f"/venues/{venue.id}/pricing-point", json=data)
        assert response.status_code == 400
        assert response.json["code"] == "CANNOT_LINK_VENUE_TO_PRICING_POINT"
        assert db.session.query(offerers_models.VenuePricingPointLink).one() == pre_existing_link
