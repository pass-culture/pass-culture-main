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


class AuthError:
    def test_unknown_redactor(self, client):
        iframe_client = _get_iframe_client(client, email="unknown@example.com")
        response = iframe_client.get(url_for(self.endpoint))
        assert response.status_code == 403
        assert "auth" in response.json


class GetClassroomPlaylistTest(SharedPlaylistsErrorTests, AuthError):
    endpoint = "adage_iframe.get_classroom_playlist"

    def test_get_classroom_playlist(self, client):
        expected_distance = 10.0
        expected_distance_prior_rounding = expected_distance + 0.001234

        institution = educational_factories.EducationalInstitutionFactory()
        institution2 = educational_factories.EducationalInstitutionFactory()

        offers = educational_factories.CollectiveOfferTemplateFactory.create_batch(3)
        for offer in offers[:-1]:
            educational_models.CollectivePlaylist(
                type=educational_models.PlaylistType.CLASSROOM,
                distanceInKm=expected_distance_prior_rounding,
                institution=institution,
                collective_offer_template=offer,
            )
        # This item is to make sure that we issue an extended search if we have less than
        # 10 offers in the default search radius
        educational_models.CollectivePlaylist(
            type=educational_models.PlaylistType.CLASSROOM,
            distanceInKm=150,
            institution=institution,
            collective_offer_template=offers[-1],
        )
        # this should not appear in the playlist because it is for a different institution
        educational_models.CollectivePlaylist(
            type=educational_models.PlaylistType.CLASSROOM,
            distanceInKm=expected_distance_prior_rounding,
            institution=institution2,
            collective_offer_template=offers[0],
        )

        iframe_client = _get_iframe_client(client, uai=institution.institutionId)

        # fetch institution (1 query)
        # fetch redactor (1 query)
        # fetch playlist data (1 query)
        # fetch playlist data if below 10 items (1 query)
        # fetch redactor's favorites (1 query)
        with assert_num_queries(5):
            response = iframe_client.get(url_for(self.endpoint))

            assert response.status_code == 200

            assert len(response.json["collectiveOffers"]) == len(offers)
            response_offers = sorted(response.json["collectiveOffers"], key=lambda o: o["id"])

            for idx, response_offer in enumerate(response_offers):
                assert response_offer["id"] == offers[idx].id
                # Ensure we rounded the distance
                if idx == 2:
                    assert response_offer["venue"]["distance"] == 150
                else:
                    assert response_offer["venue"]["distance"] == expected_distance

    def test_no_rows(self, client):
        iframe_client = _get_iframe_client(client)

        mock_path = "pcapi.connectors.big_query.TestingBackend.run_query"
        with patch(mock_path) as mock_run_query:
            mock_run_query.return_value = []
            response = iframe_client.get(url_for(self.endpoint))

            assert response.status_code == 200
            assert response.json == {"collectiveOffers": []}

    def test_get_classroom_playlist_random_order(self, client):
        expected_distance = 10.0
        institution = educational_factories.EducationalInstitutionFactory()

        offers = educational_factories.CollectiveOfferTemplateFactory.create_batch(15)
        for offer in offers:
            educational_models.CollectivePlaylist(
                type=educational_models.PlaylistType.CLASSROOM,
                distanceInKm=expected_distance,
                institution=institution,
                collective_offer_template=offer,
            )

        iframe_client = _get_iframe_client(client, uai=institution.institutionId)
        response = iframe_client.get(url_for(self.endpoint))
        assert response.status_code == 200

        playlist_order_1 = [o["id"] for o in response.json["collectiveOffers"]]
        # To avoid flackyness, let's give it 5 tries.
        # If none are different, we can be confident enough that's not a false negative
        max_try = 5
        while max_try > 0:
            response = iframe_client.get(url_for(self.endpoint))
            assert response.status_code == 200
            playlist_order_2 = [o["id"] for o in response.json["collectiveOffers"]]
            if playlist_order_1 != playlist_order_2:
                return
            max_try -= 1
        assert playlist_order_1 != playlist_order_2


class GetNewTemplateOffersPlaylistQueryTest(SharedPlaylistsErrorTests, AuthError):
    endpoint = "adage_iframe.new_template_offers_playlist"

    def test_new_template_offers_playlist(self, client):
        institution = educational_factories.EducationalInstitutionFactory()
        expected_distance = 10.0

        playlist_offers = educational_factories.CollectiveOfferTemplateFactory.create_batch(3)
        for offer in playlist_offers[:-1]:
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

        # This item is to make sure that we issue an extended search if we have less than
        # 10 offers in the default search radius
        playlist_offers[-1].offerVenue = {
            "addressType": collective_offers_serialize.OfferAddressType.OFFERER_VENUE.value,
            "otherAddress": "",
            "venueId": playlist_offers[-1].venueId,
        }
        educational_models.CollectivePlaylist(
            type=educational_models.PlaylistType.NEW_OFFER,
            distanceInKm=150,
            institution=institution,
            collective_offer_template=playlist_offers[-1],
        )

        redactor = educational_factories.EducationalRedactorFactory(
            favoriteCollectiveOfferTemplates=[playlist_offers[0]]
        )

        educational_factories.CollectiveOfferTemplateFactory()

        iframe_client = _get_iframe_client(client, email=redactor.email, uai=institution.institutionId)

        # fetch institution (1 query)
        # fetch redactor (1 query)
        # fetch playlist data (1 query)
        # fetch playlist data if below 10 items (1 query)
        # fetch redactor's favorites (1 query)
        with assert_num_queries(5):
            response = iframe_client.get(url_for(self.endpoint))

            assert response.status_code == 200
            assert len(response.json["collectiveOffers"]) == len(playlist_offers)

        response_offers = sorted(response.json["collectiveOffers"], key=lambda resp: resp["id"])
        playlist_offers = sorted(playlist_offers, key=lambda resp: resp.id)

        for idx, response_offer in enumerate(response_offers):
            assert response_offer["id"] == playlist_offers[idx].id
            assert response_offer["venue"]["distance"] == expected_distance if idx < 2 else 150
            assert response_offer["offerVenue"]["distance"] == expected_distance if idx < 2 else 150
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


class SharedOfferersPlaylistTests:
    def test_get_playlist_data(self, client):
        IMAGE_URL = "http://localhost/image.png"

        institution = educational_factories.EducationalInstitutionFactory(
            ruralLevel=educational_models.InstitutionRuralLevel.URBAIN_DENSE
        )

        expected_distance = 2.5

        items = educational_factories.PlaylistFactory.create_batch(
            10,
            type=self.playlist_type,
            distanceInKm=expected_distance,
            institution=institution,
            venue___bannerUrl=IMAGE_URL,
        )
        playlist_venues = [item.venue for item in items]

        # This one should not be part of the playlist - outside the distance limit
        educational_factories.PlaylistFactory(
            type=self.playlist_type,
            distanceInKm=150,
            institution=institution,
        )

        redactor = educational_factories.EducationalRedactorFactory()

        iframe_client = _get_iframe_client(client, email=redactor.email, uai=institution.institutionId)

        # fetch the institution (1 query)
        # fetch playlist items (1 query)
        with assert_num_queries(2):
            response = iframe_client.get(url_for(self.endpoint))

        assert response.status_code == 200
        assert len(response.json["venues"]) == len(playlist_venues)

        response_venues = sorted(response.json["venues"], key=lambda resp: resp["id"])
        venues = sorted(playlist_venues, key=lambda venue: venue.id)

        for idx, response_venue in enumerate(response_venues):
            assert response_venue["id"] == venues[idx].id
            assert response_venue["distance"] == expected_distance
            assert response_venue["imgUrl"] == IMAGE_URL

    def test_get_playlist_data_without_enough_items_at_first(self, client):
        IMAGE_URL = "http://localhost/image.png"
        playlist_venues = offerers_factories.VenueFactory.create_batch(3, _bannerUrl=IMAGE_URL)
        offerers_factories.VenueFactory()

        institution = educational_factories.EducationalInstitutionFactory(
            ruralLevel=educational_models.InstitutionRuralLevel.URBAIN_DENSE
        )

        expected_distance = 2.5

        for venue in playlist_venues[:2]:
            educational_models.CollectivePlaylist(
                type=self.playlist_type,
                distanceInKm=expected_distance,
                institution=institution,
                venue=venue,
            )

        # This one should be part of the playlist: there is not enough
        # items at first and a second query requesting more distant
        # ones should be triggered
        educational_models.CollectivePlaylist(
            type=self.playlist_type,
            distanceInKm=150,
            institution=institution,
            venue=playlist_venues[-1],
        )

        redactor = educational_factories.EducationalRedactorFactory()

        iframe_client = _get_iframe_client(client, email=redactor.email, uai=institution.institutionId)

        # fetch the institution (1 query)
        # fetch playlist items (1 query)
        # fetch other playlist items because first request did not fetched enough (1 query)
        with assert_num_queries(3):
            response = iframe_client.get(url_for(self.endpoint))

        assert response.status_code == 200
        assert len(response.json["venues"]) == 3

        response_venues = sorted(response.json["venues"], key=lambda resp: resp["id"])
        venues = sorted(playlist_venues, key=lambda venue: venue.id)

        # items within the standard distance
        for idx, response_venue in enumerate(response_venues[:-1]):
            assert response_venue["id"] == venues[idx].id
            assert response_venue["distance"] == expected_distance
            assert response_venue["imgUrl"] == IMAGE_URL

        # item above
        assert response_venues[-1]["id"] == venues[-1].id
        assert response_venues[-1]["distance"] == 150
        assert response_venues[-1]["imgUrl"] == IMAGE_URL

    def test_no_data(self, client):
        iframe_client = _get_iframe_client(client)
        response = iframe_client.get(url_for(self.endpoint))

        assert response.status_code == 200
        assert response.json == {"venues": []}

    def test_get_playlist_data_random_order(self, client):
        playlist_venues = offerers_factories.VenueFactory.create_batch(15)
        offerers_factories.VenueFactory()

        institution = educational_factories.EducationalInstitutionFactory(
            ruralLevel=educational_models.InstitutionRuralLevel.URBAIN_DENSE
        )

        for venue in playlist_venues:
            educational_models.CollectivePlaylist(
                type=self.playlist_type,
                distanceInKm=2.5,
                institution=institution,
                venue=venue,
            )

        redactor = educational_factories.EducationalRedactorFactory()
        iframe_client = _get_iframe_client(client, email=redactor.email, uai=institution.institutionId)

        response = iframe_client.get(url_for(self.endpoint))
        assert response.status_code == 200

        playlist_order_1 = [o["id"] for o in response.json["venues"]]
        # To avoid flackyness, let's give it 5 tries.
        # If none are different, we can be confident enough that's not a false negative
        max_try = 5
        while max_try > 0:
            response = iframe_client.get(url_for(self.endpoint))
            assert response.status_code == 200
            playlist_order_2 = [o["id"] for o in response.json["venues"]]
            if playlist_order_1 != playlist_order_2:
                return
            max_try -= 1
        assert playlist_order_1 != playlist_order_2


class GetLocalOfferersPlaylistTest(SharedOfferersPlaylistTests, SharedPlaylistsErrorTests):
    endpoint = "adage_iframe.get_local_offerers_playlist"
    playlist_type = educational_models.PlaylistType.LOCAL_OFFERER


class GetNewOfferersPlaylistTest(SharedOfferersPlaylistTests, SharedPlaylistsErrorTests):
    endpoint = "adage_iframe.get_new_offerers_playlist"
    playlist_type = educational_models.PlaylistType.NEW_OFFERER


def _get_iframe_client(client, email=None, uai=None):
    if uai is None:
        uai = educational_factories.EducationalInstitutionFactory().institutionId

    if email is None:
        email = educational_factories.EducationalRedactorFactory().email

    return client.with_adage_token(email=email, uai=uai)
