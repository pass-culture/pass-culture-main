from unittest.mock import patch

import pytest

import pcapi.core.educational.api.playlists as playlist_api
import pcapi.core.educational.factories as educational_factories
import pcapi.core.educational.models as educational_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


def _get_offer_id(offer_id: int) -> str:
    return f"template-{offer_id}"


class SynchronizePlaylistsTest:
    @pytest.mark.parametrize(
        "playlist_type",
        (
            educational_models.PlaylistType.CLASSROOM,
            educational_models.PlaylistType.NEW_OFFER,
        ),
    )
    def test_synchronize_collective_playlist(self, playlist_type):
        initial_distance = 5.001234
        updated_distance = 10.001234
        institution = educational_factories.EducationalInstitutionFactory()
        # Create 3 offers:
        #  #1 will be on playlist and should not be updated
        #  #2 will be on playlist and should be updated
        #  #3 will be on playlist and should be removed
        #  #4 will not be on playlist and should be created
        offers = educational_factories.CollectiveOfferTemplateFactory.create_batch(4)

        for offer in offers[:3]:
            educational_factories.PlaylistFactory(
                type=playlist_type,
                distanceInKm=initial_distance,
                institution=institution,
                collective_offer_template=offer,
            )

        mock_path = "pcapi.connectors.big_query.TestingBackend.run_query"
        with patch(mock_path) as mock_run_query:
            mock_run_query.return_value = [
                {
                    "institution_id": str(institution.id),
                    "collective_offer_id": _get_offer_id(offers[0].id),
                    "distance_in_km": initial_distance,
                },
                {
                    "institution_id": str(institution.id),
                    "collective_offer_id": _get_offer_id(offers[1].id),
                    "distance_in_km": updated_distance,
                },
                {
                    "institution_id": str(institution.id),
                    "collective_offer_id": _get_offer_id(offers[3].id),
                    "distance_in_km": updated_distance,
                },
                {
                    "institution_id": str(institution.id),
                    # offer which does not exist: has been deleted
                    "collective_offer_id": _get_offer_id(offers[-1].id + 100),
                    "distance_in_km": updated_distance,
                },
            ]
            playlist_api.synchronize_collective_playlist(playlist_type)

        playlist_items = (
            db.session.query(educational_models.CollectivePlaylist)
            .order_by(educational_models.CollectivePlaylist.id)
            .all()
        )
        playlist_data = [
            {
                "type": item.type,
                "distance_in_km": item.distanceInKm,
                "offer_id": item.collectiveOfferTemplateId,
                "institution_id": item.institutionId,
            }
            for item in playlist_items
        ]

        assert playlist_data == [
            {
                "type": playlist_type,
                "distance_in_km": initial_distance,
                "offer_id": offers[0].id,
                "institution_id": institution.id,
            },
            {
                "type": playlist_type,
                "distance_in_km": updated_distance,
                "offer_id": offers[1].id,
                "institution_id": institution.id,
            },
            {
                "type": playlist_type,
                "distance_in_km": updated_distance,
                "offer_id": offers[3].id,
                "institution_id": institution.id,
            },
        ]

    def test_synchronize_local_offerer_playlist(self):
        initial_distance = 5.001234
        updated_distance = 10.001234
        institution = educational_factories.EducationalInstitutionFactory()
        # Create 4 venues:
        #  #1 will be on playlist and should not be updated
        #  #2 will be on playlist and should be updated
        #  #3 will be on playlist and should be removed
        #  #4 will not be on playlist and should be created
        venues = offerers_factories.VenueFactory.create_batch(4)

        playlist_type = educational_models.PlaylistType.LOCAL_OFFERER

        for venue in venues[:3]:
            educational_factories.PlaylistFactory(
                type=playlist_type,
                distanceInKm=initial_distance,
                institution=institution,
                collective_offer_template=None,
                venue=venue,
            )

        mock_path = "pcapi.connectors.big_query.TestingBackend.run_query"
        with patch(mock_path) as mock_run_query:
            mock_run_query.return_value = [
                {
                    "institution_id": str(institution.id),
                    "venue_id": str(venues[0].id),
                    "distance_in_km": initial_distance,
                },
                {
                    "institution_id": str(institution.id),
                    "venue_id": str(venues[1].id),
                    "distance_in_km": updated_distance,
                },
                {
                    "institution_id": str(institution.id),
                    "venue_id": str(venues[3].id),
                    "distance_in_km": updated_distance,
                },
                {
                    "institution_id": str(institution.id),
                    "venue_id": str(venues[-1].id + 100),  # venue which does not exist:; has been deleted
                    "distance_in_km": initial_distance,
                },
            ]
            playlist_api.synchronize_collective_playlist(playlist_type)

        playlist_items = (
            db.session.query(educational_models.CollectivePlaylist)
            .order_by(educational_models.CollectivePlaylist.id)
            .all()
        )
        playlist_data = [
            {
                "type": item.type,
                "distance_in_km": item.distanceInKm,
                "venue_id": item.venueId,
                "institution_id": item.institutionId,
            }
            for item in playlist_items
        ]

        assert playlist_data == [
            {
                "type": playlist_type,
                "distance_in_km": initial_distance,
                "venue_id": venues[0].id,
                "institution_id": institution.id,
            },
            {
                "type": playlist_type,
                "distance_in_km": updated_distance,
                "venue_id": venues[1].id,
                "institution_id": institution.id,
            },
            {
                "type": playlist_type,
                "distance_in_km": updated_distance,
                "venue_id": venues[3].id,
                "institution_id": institution.id,
            },
        ]
