import datetime
from unittest.mock import patch

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core.offers import repository as offers_repository


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.features(WIP_INDIVIDUAL_OFFERS_LIST_V2=True),
]


def _create_pro_with_venue():
    pro = users_factories.ProFactory()
    venue = offerers_factories.VenueFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=venue.managingOfferer)
    return pro, venue


class Returns200Test:
    def test_returns_the_counts(self, client):
        pro, venue = _create_pro_with_venue()
        offers_factories.ThingOfferFactory(venue=venue)
        offers_factories.EventOfferFactory(venue=venue)

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/offers/counts?venueId={venue.id}")

        assert response.status_code == 200
        assert response.json == {
            "things": {"total": 1, "totalIsCapped": False, "statusCounts": None},
            "events": {"total": 1, "totalIsCapped": False, "statusCounts": None},
        }

    @patch("pcapi.core.offers.constants.OFFERS_COUNT_MAX", 1)
    def test_total_is_capped(self, client):
        pro, venue = _create_pro_with_venue()
        offers_factories.ThingOfferFactory.create_batch(2, venue=venue)

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/offers/counts?venueId={venue.id}")

        assert response.status_code == 200
        assert response.json["things"] == {"total": 1, "totalIsCapped": True, "statusCounts": None}

    @patch(
        "pcapi.routes.pro.offers.offers_repository.get_offers_counts",
        return_value=offers_repository.OffersCounts(
            things=offers_repository.OffersCount(total=0, status_counts=None),
            events=offers_repository.OffersCount(total=0, status_counts=None),
        ),
    )
    def test_passes_the_filters_to_the_repository(self, mocked_get_offers_counts, client):
        pro, venue = _create_pro_with_venue()

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(
            f"/offers/counts?venueId={venue.id}&nameOrEan=potter&creationMode=manual&isDigital=true"
            "&periodBeginningDate=2030-01-01&periodEndingDate=2030-01-31"
        )

        assert response.status_code == 200

        mocked_get_offers_counts.assert_called_once_with(
            venue_id=venue.id,
            name_keywords_or_ean="potter",
            creation_mode="manual",
            is_digital=True,
            period_beginning_date=datetime.date(2030, 1, 1),
            period_ending_date=datetime.date(2030, 1, 31),
        )


class Returns400Test:
    def test_invalid_creation_mode(self, client):
        pro, venue = _create_pro_with_venue()

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/offers/counts?venueId={venue.id}&creationMode=NOPE")

        assert response.status_code == 400
        assert "creationMode" in response.json


class Returns401Test:
    def test_user_is_not_logged_in(self, client):
        venue = offerers_factories.VenueFactory()

        response = client.get(f"/offers/counts?venueId={venue.id}")

        assert response.status_code == 401


class Returns404Test:
    def test_user_has_no_access_to_the_venue(self, client):
        pro = users_factories.ProFactory()
        venue = offerers_factories.VenueFactory()

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/offers/counts?venueId={venue.id}")

        assert response.status_code == 404

    @pytest.mark.features(WIP_INDIVIDUAL_OFFERS_LIST_V2=False)
    def test_feature_flag_is_disabled(self, client):
        pro, venue = _create_pro_with_venue()

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/offers/counts?venueId={venue.id}")

        assert response.status_code == 404
