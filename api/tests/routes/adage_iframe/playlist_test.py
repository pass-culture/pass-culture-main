from unittest.mock import patch

from flask import url_for
import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import assert_num_queries

# from pcapi.models import db
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


class GetNewTemplateOffersPlaylistQueryTest(SharedPlaylistsErrorTests):
    endpoint = "adage_iframe.new_template_offers_playlist"

    def test_new_template_offers_playlist(self, client):
        institution = educational_factories.EducationalInstitutionFactory()
        expected_distance = 10.0

        playlist_offers = educational_factories.CollectiveOfferTemplateFactory.create_batch(2)
        for offer in playlist_offers:
            offer.offerVenue = {
                "addressType": collective_offers_serialize.OfferAddressType.OFFERER_VENUE.value,
                "otherAddress": "",
                "venueId": offer.venueId,
            }

            educational_models.CollectivePlaylist(
                type=educational_models.PlaylistType.NEW_OFFER,
                distanceInKm=expected_distance,
                institution=institution,
                collective_offer_template=offer,
            )

        redactor = educational_factories.EducationalRedactorFactory(
            favoriteCollectiveOfferTemplates=[playlist_offers[0]]
        )

        educational_factories.CollectiveOfferTemplateFactory()

        iframe_client = _get_iframe_client(client, email=redactor.email, uai=institution.institutionId)

        # fetch institution (1 query)
        # fetch redactor (1 query)
        # fetch redactor's favorites (1 query)
        # fetch playlist data (1 query)
        with assert_num_queries(4):
            response = iframe_client.get(url_for(self.endpoint))

            assert response.status_code == 200
            assert len(response.json["collectiveOffers"]) == len(playlist_offers)

        response_offers = sorted(response.json["collectiveOffers"], key=lambda resp: resp["id"])
        playlist_offers = sorted(playlist_offers, key=lambda resp: resp.id)

        for idx, response_offer in enumerate(response_offers):
            assert response_offer["id"] == playlist_offers[idx].id
            assert response_offer["venue"]["distance"] == expected_distance
            assert response_offer["offerVenue"]["distance"] == expected_distance
            assert response_offer["isFavorite"] == (
                redactor.favoriteCollectiveOfferTemplates[0].id == response_offer["id"]
            )

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
        playlist_venues = offerers_factories.VenueFactory.create_batch(2)
        offerers_factories.VenueFactory()

        institution = educational_factories.EducationalInstitutionFactory()

        expected_distance = 10.0

        for venue in playlist_venues:
            educational_models.CollectivePlaylist(
                type=educational_models.PlaylistType.LOCAL_OFFERER,
                distanceInKm=expected_distance,
                institution=institution,
                venue=venue,
            )

        redactor = educational_factories.EducationalRedactorFactory()

        iframe_client = _get_iframe_client(client, email=redactor.email, uai=institution.institutionId)

        # fetch the institution (1 query)
        # fetch playlist items (1 query)
        # fetch venues (1 query)
        with assert_num_queries(3):
            response = iframe_client.get(url_for(self.endpoint))

        assert response.status_code == 200
        assert len(response.json["venues"]) == len(playlist_venues)

        response_venues = sorted(response.json["venues"], key=lambda resp: resp["id"])
        venues = sorted(playlist_venues, key=lambda venue: venue.id)

        for idx, response_venue in enumerate(response_venues):
            assert response_venue["id"] == venues[idx].id
            assert response_venue["distance"] == expected_distance

    def test_no_rows(self, client):
        institution = educational_factories.EducationalInstitutionFactory()
        redactor = educational_factories.EducationalRedactorFactory()
        iframe_client = _get_iframe_client(client, email=redactor.email, uai=institution.institutionId)

        response = iframe_client.get(url_for(self.endpoint))

        assert response.status_code == 200
        assert response.json == {"venues": []}


def _get_iframe_client(client, email=None, uai=None):
    if uai is None:
        uai = educational_factories.EducationalInstitutionFactory().institutionId

    if email is None:
        email = educational_factories.EducationalRedactorFactory().email

    return client.with_adage_token(email=email, uai=uai)
