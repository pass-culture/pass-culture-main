import logging
import uuid
from unittest.mock import patch

import pytest
from sqlalchemy import exc as sa_exc

import pcapi.core.artist.models as artist_models
import pcapi.core.offers.factories as offers_factories
from pcapi.connectors.big_query.importer.artist import ArtistImporter
from pcapi.connectors.big_query.importer.artist import ArtistProductLinkImporter
from pcapi.connectors.big_query.importer.artist_score import ArtistScoresImporter
from pcapi.connectors.big_query.queries.artist import ArtistScoresModel
from pcapi.connectors.big_query.queries.artist import DeltaAction
from pcapi.connectors.big_query.queries.artist import DeltaArtistModel
from pcapi.connectors.big_query.queries.artist import DeltaArtistProductLinkModel
from pcapi.core.artist import commands
from pcapi.core.artist.factories import ArtistFactory
from pcapi.core.artist.factories import ArtistProductLinkFactory
from pcapi.core.artist.models import Artist
from pcapi.core.artist.models import ArtistProductLink
from pcapi.core.offers.factories import ProductFactory
from pcapi.core.search import redis_queues
from pcapi.core.search.models import IndexationReason
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class UpdateArtistsFromDeltaTest:
    @patch("pcapi.connectors.big_query.importer.artist.copy_file_between_storage_backends")
    @patch("pcapi.connectors.big_query.queries.artist.ArtistDeltaQuery.execute")
    def test_updates_and_creates_artists(self, mock_artist_delta_query, mock_copy_file):
        artist_to_delete_id = str(uuid.uuid4())
        artist_to_delete = ArtistFactory(id=artist_to_delete_id, mediation_uuid="old-uuid")
        new_artist_id = str(uuid.uuid4())
        mock_artist_delta_query.return_value = [
            DeltaArtistModel(
                id=new_artist_id,
                name="Nouvel Artiste",
                description="Description du nouvel artiste",
                biography="Biographie du nouvel artiste",
                wikipedia_url="Wikipedia du nouvel artiste",
                wikidata_id="Q123456",
                mediation_uuid="new-uuid",
                action=DeltaAction.ADD,
            ),
            DeltaArtistModel(id=artist_to_delete.id, action=DeltaAction.REMOVE, name="Artist to Delete"),
        ]
        mock_copy_file.side_effect = lambda file_id, **kwargs: file_id

        ArtistImporter().run_delta_update()

        new_artist = db.session.query(Artist).filter_by(id=new_artist_id).first()
        assert db.session.query(Artist).filter_by(id=artist_to_delete_id).first() is None
        assert db.session.query(Artist).count() == 1
        assert new_artist is not None
        assert new_artist.id == new_artist_id
        assert new_artist.name == "Nouvel Artiste"
        assert new_artist.description == "Description du nouvel artiste"
        assert new_artist.biography == "Biographie du nouvel artiste"
        assert new_artist.wikipedia_url == "Wikipedia du nouvel artiste"
        assert new_artist.wikidata_id == "Q123456"
        assert new_artist.mediation_uuid == "new-uuid"

    @patch("pcapi.connectors.big_query.queries.artist.ArtistProductLinkDeltaQuery.execute")
    def test_updates_and_creates_artist_product_links(self, mock_link_delta_query):
        artist = ArtistFactory()
        product = ProductFactory()
        product2 = ProductFactory()

        link_to_delete = ArtistProductLinkFactory(
            artist_id=artist.id, product_id=product.id, artist_type=artist_models.ArtistType.AUTHOR
        )
        link_to_keep = ArtistProductLinkFactory(
            artist_id=artist.id, product_id=product.id, artist_type=artist_models.ArtistType.PERFORMER
        )
        link_to_delete_id = link_to_delete.id

        mock_link_delta_query.return_value = [
            DeltaArtistProductLinkModel(
                artist_id=artist.id,
                product_id=product2.id,
                artist_type=artist_models.ArtistType.AUTHOR.value,
                action=DeltaAction.ADD,
            ),
            DeltaArtistProductLinkModel(
                artist_id=link_to_delete.artist_id,
                product_id=link_to_delete.product_id,
                artist_type=artist_models.ArtistType.AUTHOR.value,
                action=DeltaAction.REMOVE,
            ),
        ]

        ArtistProductLinkImporter().run_delta_update()

        assert db.session.query(ArtistProductLink).filter_by(id=link_to_keep.id).first() is not None
        assert (
            db.session.query(ArtistProductLink)
            .filter_by(artist_id=artist.id, product_id=product2.id, artist_type=artist_models.ArtistType.AUTHOR)
            .first()
            is not None
        )
        assert db.session.query(ArtistProductLink).filter_by(id=link_to_delete_id).first() is None
        assert db.session.query(ArtistProductLink).count() == 2

    @patch("pcapi.connectors.big_query.importer.artist.copy_file_between_storage_backends")
    @patch("pcapi.connectors.big_query.queries.artist.ArtistDeltaQuery.execute")
    def test_update_action_modifies_existing_artist(self, mock_artist_delta_query, mock_copy_file):
        artist_to_update = ArtistFactory(name="Richard Paul Astley", description="chanteur")
        mediation_uuid = str(uuid.uuid4())
        mock_artist_delta_query.return_value = [
            DeltaArtistModel(
                id=artist_to_update.id,
                name="Rick Astley",
                description="Chanteur britannique",
                wikidata_id="Q219237",
                wikipedia_url="https://fr.wikipedia.org/wiki/Rick_Astley",
                biography="Rick Astley est un chanteur britannique né le 6 février 1966 à Newton-le-Willows...",
                mediation_uuid=mediation_uuid,
                action=DeltaAction.UPDATE,
            ),
        ]
        mock_copy_file.side_effect = lambda file_id, **kwargs: file_id

        ArtistImporter().run_delta_update()

        assert artist_to_update.name == "Rick Astley"
        assert artist_to_update.description == "Chanteur britannique"
        assert artist_to_update.wikidata_id == "Q219237"
        assert artist_to_update.wikipedia_url == "https://fr.wikipedia.org/wiki/Rick_Astley"
        assert (
            artist_to_update.biography
            == "Rick Astley est un chanteur britannique né le 6 février 1966 à Newton-le-Willows..."
        )
        assert artist_to_update.mediation_uuid == mediation_uuid

    @patch("pcapi.connectors.big_query.queries.artist.ArtistDeltaQuery.execute")
    def test_update_action_does_nothing_for_non_existent_artist(self, mock_artist_delta_query):
        ArtistFactory()
        initial_artist_count = db.session.query(Artist).count()
        non_existent_id = str(uuid.uuid4())
        mock_artist_delta_query.return_value = [
            DeltaArtistModel(id=non_existent_id, name="Artiste Fantôme", action=DeltaAction.UPDATE),
        ]

        ArtistImporter().run_delta_update()

        assert db.session.query(Artist).filter_by(id=non_existent_id).first() is None
        assert db.session.query(Artist).count() == initial_artist_count

    @patch("pcapi.connectors.big_query.queries.artist.ArtistDeltaQuery.execute")
    def test_add_action_skips_artist_if_wikidata_id_exists(self, mock_artist_delta_query, caplog):
        ArtistFactory(wikidata_id="Q123456")
        new_artist_id = str(uuid.uuid4())
        mock_artist_delta_query.return_value = [
            DeltaArtistModel(
                id=new_artist_id,
                name="Duplicate Wikidata Artist",
                wikidata_id="Q123456",
                action=DeltaAction.ADD,
            ),
        ]

        with caplog.at_level(logging.INFO):
            ArtistImporter().run_delta_update()

        assert db.session.query(Artist).filter_by(id=new_artist_id).first() is None
        assert "Artists skipped (duplicate wikidata_id) in batch" in caplog.text

    @patch("pcapi.connectors.big_query.importer.artist.copy_file_between_storage_backends")
    @patch("pcapi.connectors.big_query.queries.artist.ArtistDeltaQuery.execute")
    def test_update_artists_batch_failure_triggers_retry(self, mock_artist_delta_query, mock_copy_file, caplog):
        artist1 = ArtistFactory(name="Old Name 1")
        artist2 = ArtistFactory(name="Old Name 2")

        delta1 = DeltaArtistModel(id=artist1.id, name="New Name 1", action=DeltaAction.UPDATE)
        delta2 = DeltaArtistModel(id=artist2.id, name="New Name 2", action=DeltaAction.UPDATE)

        mock_artist_delta_query.return_value = [delta1, delta2]
        mock_copy_file.side_effect = lambda file_id, **kwargs: file_id

        with patch("pcapi.models.db.session.commit") as mock_commit:
            # 1st call: batch update -> IntregrityError
            # 2nd call: individual update artist1 -> Success
            # 3rd call: individual update artist2 -> Success
            mock_commit.side_effect = [
                sa_exc.IntegrityError("Simulated Batch Integrity Error", params=None, orig=None),
                None,
                None,
            ]

            with caplog.at_level(logging.WARNING):
                ArtistImporter().run_delta_update(batch_size=2)

        assert "Batch update failed for Artist, retrying one by one" in caplog.text

        updated_artist1 = db.session.query(Artist).get(artist1.id)
        updated_artist2 = db.session.query(Artist).get(artist2.id)

        assert updated_artist1.name == "New Name 1"
        assert updated_artist2.name == "New Name 2"


class ComputeArtistsMostRelevantImageTest:
    @patch("pcapi.core.artist.commands.async_index_artist_ids")
    def test_compute_artists_most_relevant_image_if_no_image_set(self, mock_async_index_artist):
        artist = ArtistFactory(image=None, computed_image=None)
        product_mediation = offers_factories.ProductMediationFactory()
        ArtistProductLinkFactory(artist_id=artist.id, product_id=product_mediation.product.id)

        commands.compute_artists_most_relevant_image()

        assert artist.computed_image == product_mediation.url
        mock_async_index_artist.assert_called_once_with([artist.id], reason=IndexationReason.ARTIST_IMAGE_UPDATE)

    def test_process_artists_by_batch(self, app, clear_redis):
        artists = ArtistFactory.create_batch(5, image=None, computed_image=None)
        product_mediation = offers_factories.ProductMediationFactory()
        for artist in artists:
            ArtistProductLinkFactory(artist_id=artist.id, product_id=product_mediation.product.id)

        commands.compute_artists_most_relevant_image(batch_size=2)

        assert all(artist.computed_image == product_mediation.url for artist in artists)
        app.redis_client.smembers(redis_queues.REDIS_ARTIST_IDS_TO_INDEX) == {artist.id for artist in artists}

    @patch("pcapi.core.artist.commands.async_index_artist_ids")
    def test_update_artists_computed_image_only_if_changed(self, mock_async_index_artist):
        product_mediation = offers_factories.ProductMediationFactory()
        artist_with_update = ArtistFactory(image=None, computed_image="http://another.url.com")
        artist_without_update = ArtistFactory(image=None, computed_image=product_mediation.url)
        ArtistProductLinkFactory(artist_id=artist_with_update.id, product_id=product_mediation.product.id)
        ArtistProductLinkFactory(artist_id=artist_without_update.id, product_id=product_mediation.product.id)

        commands.compute_artists_most_relevant_image()

        assert artist_with_update.computed_image == product_mediation.url
        assert artist_without_update.computed_image == product_mediation.url
        mock_async_index_artist.assert_called_once_with(
            [artist_with_update.id], reason=IndexationReason.ARTIST_IMAGE_UPDATE
        )

    @patch("pcapi.core.artist.commands.async_index_artist_ids")
    def test_does_nothing_if_image_set(self, mock_async_index_artist):
        artist = ArtistFactory(image="http://example.com")
        product_mediation = offers_factories.ProductMediationFactory()
        ArtistProductLinkFactory(artist_id=artist.id, product_id=product_mediation.product.id)

        commands.compute_artists_most_relevant_image()

        assert artist.computed_image is None
        assert artist.image == "http://example.com"
        mock_async_index_artist.assert_not_called()


class UpdateArtistScoresTest:
    @patch("pcapi.connectors.big_query.queries.artist.ArtistScoresQuery.execute")
    def test_run_scores_update_updates_existing_and_ignores_missing(self, mock_query, caplog):
        artist = ArtistFactory(app_search_score=0.0, pro_search_score=0.0)
        fake_bq_data = [
            ArtistScoresModel(id=artist.id, app_search_score=8.5, pro_search_score=9.0),
            ArtistScoresModel(id="unknown-id-123", app_search_score=50.0, pro_search_score=50.0),
        ]
        mock_query.return_value = fake_bq_data

        with caplog.at_level(logging.INFO):
            importer = ArtistScoresImporter()
            importer.run_scores_update(batch_size=1)

        assert artist.app_search_score == 8.5
        assert artist.pro_search_score == 9.0
        assert db.session.query(Artist).count() == 1
        assert "Skipping scores update for missing artist" in caplog.text
        assert "Finished artist scores update" in caplog.text

    @patch("pcapi.connectors.big_query.queries.artist.ArtistScoresQuery.execute")
    def test_batch_transaction_failure_triggers_individual_retry_success(self, mock_bq_execute, caplog):
        artist_1 = ArtistFactory(app_search_score=0.0, pro_search_score=0.0)
        artist_2 = ArtistFactory(app_search_score=0.0, pro_search_score=0.0)
        bq_item1 = ArtistScoresModel(id=artist_1.id, app_search_score=10.0, pro_search_score=5.0)
        bq_item2 = ArtistScoresModel(id=artist_2.id, app_search_score=9.87, pro_search_score=8.0)
        mock_bq_execute.return_value = iter([bq_item1, bq_item2])

        with patch("pcapi.models.db.session.commit") as mock_commit:
            mock_commit.side_effect = [
                sa_exc.SQLAlchemyError("Simulated Batch Commit Failure"),
                None,
                None,
            ]
            importer = ArtistScoresImporter()
            importer.run_scores_update(batch_size=2)

            assert mock_commit.call_count == 3
            assert "Batch update failed" in caplog.text
            assert "Retrying one by one" in caplog.text
            assert artist_1.app_search_score == 10.0
            assert artist_1.pro_search_score == 5.0
            assert artist_2.app_search_score == 9.87
            assert artist_2.pro_search_score == 8.0
