from unittest.mock import patch

from flask import url_for
import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.routes.serialization import collective_offers_serialize


pytestmark = pytest.mark.usefixtures("db_session")


class SharedPlaylistsErrorTests:
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


class GetClassroomPlaylistTest(SharedPlaylistsErrorTests):
    endpoint = "adage_iframe.get_classroom_playlist"

    def test_get_classroom_playlist(self, client):
        expected_distance = 10.0
        expected_distance_prior_rounding = expected_distance + 0.001234

        institution = educational_factories.EducationalInstitutionFactory()
        institution2 = educational_factories.EducationalInstitutionFactory()

        offers = educational_factories.CollectiveOfferTemplateFactory.create_batch(2)
        for offer in offers:
            educational_models.CollectivePlaylist(
                type=educational_models.PlaylistType.CLASSROOM,
                distanceInKm=expected_distance_prior_rounding,
                institution=institution,
                collective_offer_template=offer,
            )
        educational_models.CollectivePlaylist(
            type=educational_models.PlaylistType.CLASSROOM,
            distanceInKm=expected_distance_prior_rounding,
            institution=institution2,
            collective_offer_template=offers[0],
        )

        iframe_client = _get_iframe_client(client, uai=institution.institutionId)

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

    def test_unknown_redactor(self, client):
        iframe_client = _get_iframe_client(client, email="unknown@example.com")
        response = iframe_client.get(url_for(self.endpoint))
        assert response.status_code == 403
        assert "auth" in response.json


class GetNewTemplateOffersPlaylistTest(SharedPlaylistsErrorTests):
    endpoint = "adage_iframe.new_template_offers_playlist"

    def test_new_template_offers_playlist(self, client):
        offers = educational_factories.CollectiveOfferTemplateFactory.create_batch(3)
        for offer in offers:
            offer.offerVenue = {
                "addressType": collective_offers_serialize.OfferAddressType.OFFERER_VENUE.value,
                "otherAddress": "",
                "venueId": offer.venueId,
            }
        redactor = educational_factories.EducationalRedactorFactory()

        expected_distance = 10.0

        iframe_client = _get_iframe_client(client, email=redactor.email)

        favs = [
            educational_models.CollectiveOfferTemplateEducationalRedactor(
                educationalRedactorId=redactor.id,
                collectiveOfferTemplateId=offers[1].id,
            ),
            educational_models.CollectiveOfferTemplateEducationalRedactor(
                educationalRedactorId=redactor.id,
                collectiveOfferTemplateId=offers[2].id,
            ),
        ]
        db.session.add(favs[0])
        db.session.add(favs[1])
        db.session.flush()

        mock_path = "pcapi.connectors.big_query.TestingBackend.run_query"
        with patch(mock_path) as mock_run_query:
            mock_run_query.return_value = [
                {"collective_offer_id": str(offers[0].id), "distance_in_km": expected_distance},
                {"collective_offer_id": str(offers[1].id), "distance_in_km": expected_distance},
                {"collective_offer_id": str(offers[2].id), "distance_in_km": expected_distance},
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
                    assert response_offer["offerVenue"]["distance"] == expected_distance
                    assert response_offer["isFavorite"] == bool(idx)

    def test_no_rows(self, client):
        iframe_client = _get_iframe_client(client)

        mock_path = "pcapi.connectors.big_query.TestingBackend.run_query"
        with patch(mock_path) as mock_run_query:
            mock_run_query.return_value = []
            response = iframe_client.get(url_for(self.endpoint))

            assert response.status_code == 200
            assert response.json == {"collectiveOffers": []}

    def test_unknown_redactor(self, client):
        iframe_client = _get_iframe_client(client, email="unknown@example.com")
        response = iframe_client.get(url_for(self.endpoint))
        assert response.status_code == 403
        assert "auth" in response.json


class GetLocalOfferersPlaylistTest(SharedPlaylistsErrorTests):
    endpoint = "adage_iframe.get_local_offerers_playlist"

    def test_get_local_offerers_playlist(self, client):
        venues = sorted(offerers_factories.VenueFactory.create_batch(2), key=lambda v: v.id)
        expected_distance = 10

        iframe_client = _get_iframe_client(client)

        mock_path = "pcapi.connectors.big_query.TestingBackend.run_query"
        with (
            patch(mock_path) as mock_run_query,
            patch("pcapi.routes.adage_iframe.playlists._get_max_range_for_local_venues") as mock_max_range,
        ):
            mock_run_query.return_value = [
                {"venue_id": venues[0].id, "distance_in_km": expected_distance},
                {"venue_id": venues[1].id, "distance_in_km": expected_distance},
            ]
            mock_max_range.return_value = 60

            # fetch the institution (1 query)
            # fetch venues data (1 query)
            with assert_num_queries(2):
                response = iframe_client.get(url_for(self.endpoint))

            assert response.status_code == 200
            assert len(response.json["venues"]) == 2

            for idx, response_venue in enumerate(sorted(response.json["venues"], key=lambda v: v["id"])):
                assert response_venue["id"] == venues[idx].id
                assert response_venue["distance"] == expected_distance

    def test_no_rows(self, client):
        iframe_client = _get_iframe_client(client)

        mock_path = "pcapi.connectors.big_query.TestingBackend.run_query"
        with patch(mock_path) as mock_run_query:
            mock_run_query.return_value = []
            response = iframe_client.get(url_for(self.endpoint))

            assert response.status_code == 200
            assert response.json == {"venues": []}


def _get_iframe_client(client, email=None, uai=None):
    if uai is None:
        uai = educational_factories.EducationalInstitutionFactory().institutionId

    if email is None:
        email = educational_factories.EducationalRedactorFactory().email

    return client.with_adage_token(email=email, uai=uai)
