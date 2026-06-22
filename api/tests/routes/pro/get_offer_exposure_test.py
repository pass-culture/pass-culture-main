import datetime
from unittest.mock import patch

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core import testing
from pcapi.core.offers.constants import ExposureEventType
from pcapi.routes.serialization import offer_exposure_serialize


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    @patch("pcapi.routes.serialization.offer_exposure_serialize.GetOfferExposureResponseModel.build")
    def test_get_offer_exposure(self, mock_build_offer_exposure, client):
        mock_build_offer_exposure.return_value = offer_exposure_serialize.GetOfferExposureResponseModel(
            events=[
                offer_exposure_serialize.ExposureEventResponseModel(
                    type=ExposureEventType.HIGHLIGHT,
                    name="Mock Name",
                    start_date=datetime.datetime(2026, 2, 1),
                    end_date=datetime.datetime(2026, 2, 20),
                ),
                offer_exposure_serialize.ExposureEventResponseModel(
                    type=ExposureEventType.HEADLINE,
                    name=None,
                    start_date=datetime.datetime(2026, 1, 1),
                    end_date=None,
                ),
            ]
        )
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(venue=venue)

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id

        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select offer + venue + pro_advice
        num_queries += 1  # select headline offers
        num_queries += 1  # select criteria + highlights
        num_queries += 1  # check user has rights on offerer
        with testing.assert_num_queries(num_queries):
            response = auth_client.get(f"/offers/{offer_id}/exposure")
            assert response.status_code == 200

        mock_build_offer_exposure.assert_called_once()
        assert mock_build_offer_exposure.call_args.args[0].id == offer_id
        assert response.json == {
            "events": [
                {
                    "type": "HIGHLIGHT",
                    "name": "Mock Name",
                    "startDate": "2026-02-01T00:00:00Z",
                    "endDate": "2026-02-20T00:00:00Z",
                },
                {
                    "type": "HEADLINE",
                    "name": None,
                    "startDate": "2026-01-01T00:00:00Z",
                    "endDate": None,
                },
            ]
        }


@pytest.mark.usefixtures("db_session")
class Returns401Test:
    def test_unauthenticated(self, client):
        offer = offers_factories.OfferFactory()

        response = client.get(f"/offers/{offer.id}/exposure")

        assert response.status_code == 401


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def test_offer_not_found(self, client):
        pro_user = users_factories.ProFactory()

        auth_client = client.with_session_auth(email=pro_user.email)
        response = auth_client.get("/offers/99999999/exposure")

        assert response.status_code == 404

    def test_unauthorized_user(self, client):
        pro_user = users_factories.ProFactory()
        offer = offers_factories.OfferFactory()

        auth_client = client.with_session_auth(email=pro_user.email)
        response = auth_client.get(f"/offers/{offer.id}/exposure")

        assert response.status_code == 404
