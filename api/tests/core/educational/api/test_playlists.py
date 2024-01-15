from unittest.mock import patch

import pytest

import pcapi.core.educational.api.playlists as playlist_api
import pcapi.core.educational.factories as educational_factories
import pcapi.core.educational.models as educational_models


pytestmark = pytest.mark.usefixtures("db_session")


class SynchronizePlaylistsTest:
    def test_synchronize_classroom_playlists(self):
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
                type=educational_models.PlaylistType.CLASSROOM,
                distanceInKm=initial_distance,
                institution=institution,
                collective_offer_template=offer,
            )

        mock_path = "pcapi.connectors.big_query.TestingBackend.run_query"
        with patch(mock_path) as mock_run_query:
            mock_run_query.return_value = [
                {"collective_offer_id": str(offers[0].id), "distance_in_km": initial_distance},
                {"collective_offer_id": str(offers[1].id), "distance_in_km": updated_distance},
                {"collective_offer_id": str(offers[3].id), "distance_in_km": updated_distance},
            ]
            playlist_api.synchronize_classroom_playlists()

        playlist_items = educational_models.CollectivePlaylist.query.order_by(
            educational_models.CollectivePlaylist.id
        ).all()
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
                "type": educational_models.PlaylistType.CLASSROOM,
                "distance_in_km": initial_distance,
                "offer_id": offers[0].id,
                "institution_id": institution.id,
            },
            {
                "type": educational_models.PlaylistType.CLASSROOM,
                "distance_in_km": updated_distance,
                "offer_id": offers[1].id,
                "institution_id": institution.id,
            },
            {
                "type": educational_models.PlaylistType.CLASSROOM,
                "distance_in_km": updated_distance,
                "offer_id": offers[3].id,
                "institution_id": institution.id,
            },
        ]
