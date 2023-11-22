from unittest.mock import patch

from flask import url_for
import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.testing import assert_num_queries


pytestmark = pytest.mark.usefixtures("db_session")


class GetClassroomPlaylistTest:
    endpoint = "adage_iframe.get_classroom_playlist"

    def test_get_classroom_playlist(self, client):
        stocks = educational_factories.CollectiveStockFactory.create_batch(2)
        offers = sorted([stock.collectiveOffer for stock in stocks], key=lambda o: o.id)

        expected_distance = 10

        iframe_client = _get_iframe_client(client)

        mock_path = "pcapi.connectors.big_query.TestingBackend.run_query"
        with patch(mock_path) as mock_run_query:
            mock_run_query.return_value = [
                {"offer_id": offers[0].id, "distance_in_km": expected_distance},
                {"offer_id": offers[1].id, "distance_in_km": expected_distance},
            ]

            # fetch institution (1 query)
            # fetch redactor (1 query)
            # fetch redactor's favorites (1 query)
            # fetch playlist data (1 query)
            with assert_num_queries(4):
                response = iframe_client.get(url_for(self.endpoint))

            assert response.status_code == 200

            assert len(response.json["collectiveOffers"]) == len(offers)
            response_offers = sorted(response.json["collectiveOffers"], key=lambda o: o["id"])

            for idx, response_offer in enumerate(response_offers):
                assert response_offer["id"] == offers[idx].id
                assert response_offer["venue"]["distance"] == expected_distance

    def test_no_rows(self, client):
        iframe_client = _get_iframe_client(client)

        mock_path = "pcapi.connectors.big_query.TestingBackend.run_query"
        with patch(mock_path) as mock_run_query:
            mock_run_query.return_value = []
            response = iframe_client.get(url_for(self.endpoint))

            assert response.status_code == 200
            assert response.json == {"collectiveOffers": []}

    def test_no_uai(self, client):
        iframe_client = _get_iframe_client(client, uai="")
        response = iframe_client.get(url_for(self.endpoint))
        assert response.status_code == 403
        assert "message" in response.json

    def test_unknown_institution(self, client):
        iframe_client = _get_iframe_client(client, uai="UAI123")
        response = iframe_client.get(url_for(self.endpoint))
        assert response.status_code == 403
        assert "message" in response.json

    def test_unknown_redactor(self, client):
        iframe_client = _get_iframe_client(client, email="unknown@example.com")
        response = iframe_client.get(url_for(self.endpoint))
        assert response.status_code == 403
        assert "auth" in response.json


def _get_iframe_client(client, email=None, uai=None):
    if uai is None:
        uai = educational_factories.EducationalInstitutionFactory().institutionId

    if email is None:
        email = educational_factories.EducationalRedactorFactory().email

    return client.with_adage_token(email=email, uai=uai)
