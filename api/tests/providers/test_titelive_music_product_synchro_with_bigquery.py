import copy
import uuid
from unittest.mock import patch

import pytest

import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.constants as providers_constants
import pcapi.core.providers.factories as providers_factories
import pcapi.core.providers.models as providers_models
from pcapi.connectors.big_query.queries.product import BigQueryTiteliveMusicProductModel
from pcapi.connectors.titelive import TiteliveBase
from pcapi.core.categories import subcategories
from pcapi.core.categories.genres import music
from pcapi.core.providers.titelive_bq_music_search import BigQueryTiteliveMusicProductSync
from pcapi.models import db

from tests.connectors.titelive import fixtures


@pytest.mark.usefixtures("db_session")
class BigQueryTiteliveMusicProductSyncTest:
    BATCH_SIZE = 100

    def _prepare_bq_music_from_fixture(self, fixture_result_item: dict) -> list[BigQueryTiteliveMusicProductModel]:
        models = []
        article_dict = fixture_result_item.get("article", {})

        for article_data in article_dict.values():
            model = BigQueryTiteliveMusicProductModel(
                **article_data,
                ean=article_data.get("gencod"),
                titre=fixture_result_item.get("titre"),
                recto_uuid=str(uuid.uuid4()) if article_data.get("image") else None,
                verso_uuid=str(uuid.uuid4()) if article_data.get("image_4") else None,
            )
            models.append(model)

        return models

    def _prepare_iterator_from_fixture(self, fixture: dict) -> list[BigQueryTiteliveMusicProductModel]:
        results = []
        if "result" in fixture:
            for item in fixture["result"]:
                results.extend(self._prepare_bq_music_from_fixture(item))
        return results

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_music_search.BigQueryTiteliveMusicProductDeltaQuery.execute")
    def test_titelive_music_sync(self, mock_execute, mock_gcp_data, mock_gcp_backend, settings):
        titelive_epagine_provider = providers_factories.ProviderFactory.create(
            name=providers_constants.TITELIVE_ENRICHED_BY_DATA
        )
        bq_products = self._prepare_iterator_from_fixture(fixtures.MUSIC_SEARCH_FIXTURE)
        mock_execute.return_value = iter(bq_products)
        offers_factories.ProductFactory(ean="3700187679323", lastProvider=titelive_epagine_provider)

        with patch.object(
            BigQueryTiteliveMusicProductSync, "_copy_image_from_data_bucket_to_backend_bucket", lambda s, uuid: uuid
        ):
            BigQueryTiteliveMusicProductSync().synchronize_products(batch_size=self.BATCH_SIZE)

        cd_product = (
            db.session.query(offers_models.Product)
            .filter(
                offers_models.Product.ean == "3700187679323",
                offers_models.Product.lastProvider == titelive_epagine_provider,
            )
            .one()
        )
        assert cd_product is not None
        assert cd_product.name == "Les dernières volontés de Mozart (symphony)"
        assert cd_product.description == 'GIMS revient avec " Les dernières volontés de Mozart ", un album de tubes.'
        assert cd_product.subcategoryId == subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id
        assert cd_product.ean == "3700187679323"
        assert cd_product.extraData["artist"] == "Gims"
        assert cd_product.extraData["author"] == "Gims"
        assert cd_product.extraData["contenu_explicite"] == "0"
        assert cd_product.extraData["date_parution"] == "2022-12-02"
        assert cd_product.extraData["dispo"] == 1
        assert cd_product.extraData["distributeur"] == "Believe"
        assert cd_product.extraData["editeur"] == "BELIEVE"
        assert cd_product.extraData["music_label"] == "PLAY TWO"
        assert cd_product.extraData["nb_galettes"] == "1"
        assert cd_product.extraData["performer"] == "Gims"
        assert cd_product.extraData["prix_musique"] == "14.99"
        assert cd_product.extraData["musicType"] == str(music.MUSIC_TYPES_BY_SLUG["HIP_HOP_RAP-RAP_FRANCAIS"].code)
        assert cd_product.extraData["musicSubType"] == str(
            music.MUSIC_SUB_TYPES_BY_SLUG["HIP_HOP_RAP-RAP_FRANCAIS"].code
        )

        vinyle_product = (
            db.session.query(offers_models.Product)
            .filter(
                offers_models.Product.ean == "5054197199738",
                offers_models.Product.lastProvider == titelive_epagine_provider,
            )
            .one()
        )
        assert vinyle_product.name is not None
        assert vinyle_product.name == "Cracker Island"
        assert (
            vinyle_product.description
            == "Ce huitième album studio de Gorillaz est une collection énergique, optimiste et riche en genres de 10 titres mettant en vedette un line-up stellaire de collaborateurs : Thundercat, Tame Impala, Bad Bunny, Stevie Nicks, Adeleye Omotayo, Bootie Brown et Beck."
        )
        assert vinyle_product.subcategoryId == subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id
        assert vinyle_product.ean == "5054197199738"
        assert vinyle_product.extraData["artist"] == "Gorillaz"
        assert vinyle_product.extraData["author"] == "Gorillaz"
        assert vinyle_product.extraData["contenu_explicite"] == "0"
        assert vinyle_product.extraData["date_parution"] == "2023-02-24"
        assert vinyle_product.extraData["dispo"] == 1
        assert vinyle_product.extraData["distributeur"] == "Warner Music France"
        assert vinyle_product.extraData["editeur"] == "WARNER MUSIC UK"
        assert vinyle_product.extraData["music_label"] == "WARNER MUSIC UK"
        assert vinyle_product.extraData["nb_galettes"] == "1"
        assert vinyle_product.extraData["performer"] == "Gorillaz"
        assert vinyle_product.extraData["musicType"] == str(music.MUSIC_TYPES_BY_SLUG["POP-BRITPOP"].code)
        assert vinyle_product.extraData["musicSubType"] == str(music.MUSIC_SUB_TYPES_BY_SLUG["POP-BRITPOP"].code)
        assert "prix_musique" not in vinyle_product.extraData

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_music_search.BigQueryTiteliveMusicProductDeltaQuery.execute")
    def test_titelive_sync_event(self, mock_execute, mock_gcp_data, mock_gcp_backend):
        titelive_epagine_provider = providers_factories.ProviderFactory.create(
            name=providers_constants.TITELIVE_ENRICHED_BY_DATA
        )
        mock_execute.return_value = iter([])

        BigQueryTiteliveMusicProductSync().synchronize_products(batch_size=self.BATCH_SIZE)

        stop_event, start_event = (
            db.session.query(providers_models.LocalProviderEvent)
            .order_by(providers_models.LocalProviderEvent.id.desc())
            .limit(2)
        )
        assert stop_event.provider == start_event.provider == titelive_epagine_provider
        assert stop_event.payload == start_event.payload == TiteliveBase.MUSIC.value
        assert stop_event.type == providers_models.LocalProviderEventType.SyncEnd
        assert start_event.type == providers_models.LocalProviderEventType.SyncStart

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    def test_titelive_sync_failure_event(self, mock_gcp_data, mock_gcp_backend):
        titelive_epagine_provider = providers_factories.ProviderFactory.create(
            name=providers_constants.TITELIVE_ENRICHED_BY_DATA
        )

        sync_manager = BigQueryTiteliveMusicProductSync()
        with patch.object(sync_manager, "run_synchronization") as mock_run:
            mock_run.side_effect = ValueError("BigQuery connection failed")
            with pytest.raises(ValueError):
                sync_manager.synchronize_products(batch_size=self.BATCH_SIZE)

        error_sync_events_query = db.session.query(providers_models.LocalProviderEvent).filter(
            providers_models.LocalProviderEvent.provider == titelive_epagine_provider,
            providers_models.LocalProviderEvent.type == providers_models.LocalProviderEventType.SyncError,
        )
        assert error_sync_events_query.count() == 1
        assert "ValueError" in error_sync_events_query.first().payload

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_music_search.BigQueryTiteliveMusicProductDeltaQuery.execute")
    def test_sync_skips_unallowed_format(self, mock_execute, mock_gcp_data, mock_gcp_backend):
        providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        fixture = copy.deepcopy(fixtures.MUSIC_SEARCH_FIXTURE)
        fixture["result"][1]["article"]["1"]["codesupport"] = "35"
        bq_products = self._prepare_iterator_from_fixture(fixture)
        mock_execute.return_value = iter(bq_products)

        with patch.object(
            BigQueryTiteliveMusicProductSync, "_copy_image_from_data_bucket_to_backend_bucket", lambda s, uuid: uuid
        ):
            BigQueryTiteliveMusicProductSync().synchronize_products(batch_size=self.BATCH_SIZE)

        synced_products = db.session.query(offers_models.Product).all()
        assert len(synced_products) == 2
        ean_valid = "3700187679323"
        assert db.session.query(offers_models.Product).filter_by(ean=ean_valid).count() == 1

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch(
        "pcapi.core.providers.titelive_bq_music_search.BigQueryTiteliveMusicProductSync._copy_image_from_data_bucket_to_backend_bucket"
    )
    @patch("pcapi.core.providers.titelive_bq_music_search.BigQueryTiteliveMusicProductDeltaQuery.execute")
    def test_creates_images_for_new_product(self, mock_execute, mock_copy_image, mock_gcp_data, mock_gcp_backend):
        mock_copy_image.side_effect = lambda uuid: uuid
        providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        recto_uuid = str(uuid.uuid4())
        verso_uuid = str(uuid.uuid4())
        fixture_item = fixtures.MUSIC_SEARCH_FIXTURE["result"][0]
        bq_product = self._prepare_bq_music_from_fixture(fixture_item)[0]
        bq_product.ean = "3700187679323"
        bq_product.recto_uuid = recto_uuid
        bq_product.verso_uuid = verso_uuid
        bq_product.has_image = True
        bq_product.has_verso_image = True
        mock_execute.return_value = iter([bq_product])

        BigQueryTiteliveMusicProductSync().run_synchronization(batch_size=self.BATCH_SIZE)

        product = db.session.query(offers_models.Product).filter_by(ean="3700187679323").one()
        mediations = db.session.query(offers_models.ProductMediation).filter_by(productId=product.id).all()
        assert len(mediations) == 2
        mediation_map = {m.imageType: m.uuid for m in mediations}
        assert mediation_map[offers_models.ImageType.RECTO] == recto_uuid
        assert mediation_map[offers_models.ImageType.VERSO] == verso_uuid
        mock_copy_image.assert_any_call(recto_uuid)
        mock_copy_image.assert_any_call(verso_uuid)

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch(
        "pcapi.core.providers.titelive_bq_music_search.BigQueryTiteliveMusicProductSync._copy_image_from_data_bucket_to_backend_bucket"
    )
    @patch("pcapi.core.providers.titelive_bq_music_search.BigQueryTiteliveMusicProductDeltaQuery.execute")
    def test_replaces_all_images_on_full_update(self, mock_execute, mock_copy_image, mock_gcp_data, mock_gcp_backend):
        mock_copy_image.side_effect = lambda uuid: uuid
        provider = providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        ean_test = "3700187679323"
        product = offers_factories.ProductFactory(ean=ean_test, lastProviderId=provider.id)
        offers_factories.ProductMediationFactory(
            product=product, imageType=offers_models.ImageType.RECTO, uuid="old-recto-uuid"
        )
        offers_factories.ProductMediationFactory(
            product=product, imageType=offers_models.ImageType.VERSO, uuid="old-verso-uuid"
        )
        new_recto_uuid = str(uuid.uuid4())
        new_verso_uuid = str(uuid.uuid4())
        fixture_item = fixtures.MUSIC_SEARCH_FIXTURE["result"][0]
        bq_product = self._prepare_bq_music_from_fixture(fixture_item)[0]
        bq_product.ean = ean_test
        bq_product.recto_uuid = new_recto_uuid
        bq_product.verso_uuid = new_verso_uuid
        bq_product.has_image = True
        bq_product.has_verso_image = True
        mock_execute.return_value = iter([bq_product])

        BigQueryTiteliveMusicProductSync().run_synchronization(batch_size=self.BATCH_SIZE)

        mediations = db.session.query(offers_models.ProductMediation).filter_by(productId=product.id).all()
        assert len(mediations) == 2
        mediation_map = {m.imageType: m.uuid for m in mediations}
        assert mediation_map[offers_models.ImageType.RECTO] == new_recto_uuid
        assert mediation_map[offers_models.ImageType.VERSO] == new_verso_uuid
        mock_copy_image.assert_any_call(new_recto_uuid)
        mock_copy_image.assert_any_call(new_verso_uuid)

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch(
        "pcapi.core.providers.titelive_bq_music_search.BigQueryTiteliveMusicProductSync._copy_image_from_data_bucket_to_backend_bucket"
    )
    @patch("pcapi.core.providers.titelive_bq_music_search.BigQueryTiteliveMusicProductDeltaQuery.execute")
    def test_replaces_only_provided_images_on_partial_update(
        self, mock_execute, mock_copy_image, mock_gcp_data, mock_gcp_backend
    ):
        mock_copy_image.side_effect = lambda uuid: uuid
        provider = providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        ean_test = "3700187679323"
        product = offers_factories.ProductFactory(ean=ean_test, lastProviderId=provider.id)
        offers_factories.ProductMediationFactory(
            product=product, imageType=offers_models.ImageType.RECTO, uuid="old-recto-uuid"
        )
        offers_factories.ProductMediationFactory(
            product=product, imageType=offers_models.ImageType.VERSO, uuid="old-verso-uuid"
        )
        new_recto_uuid = str(uuid.uuid4())
        fixture_item = fixtures.MUSIC_SEARCH_FIXTURE["result"][0]
        bq_product = self._prepare_bq_music_from_fixture(fixture_item)[0]
        bq_product.ean = ean_test
        bq_product.recto_uuid = new_recto_uuid
        bq_product.verso_uuid = None
        bq_product.has_image = True
        bq_product.has_verso_image = False
        mock_execute.return_value = iter([bq_product])

        BigQueryTiteliveMusicProductSync().run_synchronization(batch_size=self.BATCH_SIZE)

        mediations = db.session.query(offers_models.ProductMediation).filter_by(productId=product.id).all()
        assert len(mediations) == 2
        mediation_map = {m.imageType: m.uuid for m in mediations}
        assert mediation_map[offers_models.ImageType.RECTO] == new_recto_uuid
        assert mediation_map[offers_models.ImageType.VERSO] == "old-verso-uuid"
        mock_copy_image.assert_called_once_with(new_recto_uuid)

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch(
        "pcapi.core.providers.titelive_bq_music_search.BigQueryTiteliveMusicProductSync._copy_image_from_data_bucket_to_backend_bucket"
    )
    @patch("pcapi.core.providers.titelive_bq_music_search.BigQueryTiteliveMusicProductDeltaQuery.execute")
    def test_does_not_change_images_when_uuids_are_null(
        self, mock_execute, mock_copy_image, mock_gcp_data, mock_gcp_backend
    ):
        mock_copy_image.side_effect = lambda uuid: uuid
        provider = providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        ean_test = "3700187679323"
        product = offers_factories.ProductFactory(ean=ean_test, lastProviderId=provider.id)
        offers_factories.ProductMediationFactory(
            product=product, imageType=offers_models.ImageType.RECTO, uuid="old-recto-uuid"
        )
        offers_factories.ProductMediationFactory(
            product=product, imageType=offers_models.ImageType.VERSO, uuid="old-verso-uuid"
        )
        fixture_item = fixtures.MUSIC_SEARCH_FIXTURE["result"][0]
        bq_product = self._prepare_bq_music_from_fixture(fixture_item)[0]
        bq_product.ean = ean_test
        bq_product.recto_uuid = None
        bq_product.verso_uuid = None
        bq_product.has_image = True
        bq_product.has_verso_image = False
        mock_execute.return_value = iter([bq_product])

        BigQueryTiteliveMusicProductSync().run_synchronization(batch_size=self.BATCH_SIZE)

        mediations = db.session.query(offers_models.ProductMediation).filter_by(productId=product.id).all()
        assert len(mediations) == 2
        mediation_map = {m.imageType: m.uuid for m in mediations}
        assert mediation_map[offers_models.ImageType.RECTO] == "old-recto-uuid"
        assert mediation_map[offers_models.ImageType.VERSO] == "old-verso-uuid"
        mock_copy_image.assert_not_called()

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_music_search.BigQueryTiteliveMusicProductDeltaQuery.execute")
    def test_gcp_exception_during_image_copy_is_caught_and_does_not_crash_sync(
        self, mock_execute, mock_gcp_data_class, mock_gcp_backend_class
    ):
        mock_gcp_data_instance = mock_gcp_data_class.return_value
        mock_gcp_backend_instance = mock_gcp_backend_class.return_value
        mock_gcp_backend_instance.object_exists.return_value = False
        mock_gcp_data_instance.object_exists.return_value = True
        mock_gcp_data_instance.copy_object_to.side_effect = Exception("Simulated GCP BUCKET FAILURE")
        providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        recto_uuid = str(uuid.uuid4())
        ean_test = "3700187679323"
        fixture_item = fixtures.MUSIC_SEARCH_FIXTURE["result"][0]
        bq_product = self._prepare_bq_music_from_fixture(fixture_item)[0]
        bq_product.ean = ean_test
        bq_product.recto_uuid = recto_uuid
        bq_product.has_image = True
        bq_product.has_verso_image = False
        mock_execute.return_value = iter([bq_product])

        BigQueryTiteliveMusicProductSync().run_synchronization(batch_size=self.BATCH_SIZE)

        product = db.session.query(offers_models.Product).filter_by(ean=ean_test).one_or_none()
        assert product is not None
        mediations_count = db.session.query(offers_models.ProductMediation).filter_by(productId=product.id).count()
        assert mediations_count == 0

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_music_search.BigQueryTiteliveMusicProductDeltaQuery.execute")
    def test_gcp_exception_during_image_update_does_not_delete_old_image(
        self, mock_execute, mock_gcp_data_class, mock_gcp_backend_class
    ):
        mock_gcp_data_instance = mock_gcp_data_class.return_value
        mock_gcp_backend_instance = mock_gcp_backend_class.return_value
        provider = providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        ean_test = "3700187679323"
        old_recto_uuid = "old-recto-uuid-12345"
        product = offers_factories.ProductFactory(ean=ean_test, lastProviderId=provider.id, name="Old Name")
        offers_factories.ProductMediationFactory(
            product=product, imageType=offers_models.ImageType.RECTO, uuid=old_recto_uuid
        )
        fixture_item = fixtures.MUSIC_SEARCH_FIXTURE["result"][0]
        bq_product = self._prepare_bq_music_from_fixture(fixture_item)[0]
        bq_product.ean = ean_test
        bq_product.titre = "New Updated Name"
        bq_product.recto_uuid = str(uuid.uuid4())
        bq_product.has_image = True
        bq_product.has_verso_image = False
        mock_execute.return_value = iter([bq_product])
        mock_gcp_backend_instance.object_exists.return_value = False
        mock_gcp_data_instance.object_exists.return_value = True
        mock_gcp_data_instance.copy_object_to.side_effect = Exception("Simulated GCP BUCKET FAILURE")

        BigQueryTiteliveMusicProductSync().run_synchronization(batch_size=self.BATCH_SIZE)

        assert product.name == "New Updated Name"
        mediations = db.session.query(offers_models.ProductMediation).filter_by(productId=product.id).all()
        assert len(mediations) == 1
        assert mediations[0].imageType == offers_models.ImageType.RECTO
        assert mediations[0].uuid == old_recto_uuid

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_music_search.BigQueryTiteliveMusicProductDeltaQuery.execute")
    def test_batch_transaction_failure_triggers_individual_retry_success(
        self, mock_execute, mock_gcp_data, mock_gcp_backend
    ):
        providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        EAN_1 = "3700000000001"
        EAN_2 = "3700000000002"
        fixture_item = fixtures.MUSIC_SEARCH_FIXTURE["result"][0]
        bq_product1 = self._prepare_bq_music_from_fixture(fixture_item)[0]
        bq_product1.ean = EAN_1
        bq_product1.titre = "Music Product 1"
        bq_product2 = self._prepare_bq_music_from_fixture(fixture_item)[0]
        bq_product2.ean = EAN_2
        bq_product2.titre = "Music Product 2"
        mock_execute.return_value = iter([bq_product1, bq_product2])

        with patch("pcapi.models.db.session.commit") as mock_commit:
            mock_commit.side_effect = [
                Exception("Simulated Batch Commit Failure"),  # Batch commit fail
                None,  # individual commit for product 1
                None,  # individual commit for product 2
            ]
            with patch.object(
                BigQueryTiteliveMusicProductSync, "_copy_image_from_data_bucket_to_backend_bucket", lambda s, uuid: uuid
            ):
                sync_manager = BigQueryTiteliveMusicProductSync()
                sync_manager.run_synchronization(batch_size=self.BATCH_SIZE)

        product1 = db.session.query(offers_models.Product).filter_by(ean=EAN_1).one_or_none()
        assert product1 is not None
        assert product1.name == "Music Product 1"
        product2 = db.session.query(offers_models.Product).filter_by(ean=EAN_2).one_or_none()
        assert product2 is not None
        assert product2.name == "Music Product 2"
        assert mock_commit.call_count == 3

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_music_search.BigQueryTiteliveMusicProductDeltaQuery.execute")
    def test_sync_images_cleans_up_duplicates_when_correct_mediation_exists(
        self, mock_execute, mock_gcp_data, mock_gcp_backend
    ):
        provider = providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        ean_test = "3700187679323"
        product = offers_factories.ProductFactory(ean=ean_test, lastProviderId=provider.id)
        correct_recto_uuid = str(uuid.uuid4())
        old_recto_uuid = str(uuid.uuid4())
        untouched_verso_uuid = str(uuid.uuid4())
        offers_factories.ProductMediationFactory(
            product=product, imageType=offers_models.ImageType.RECTO, uuid=correct_recto_uuid
        )
        offers_factories.ProductMediationFactory(
            product=product, imageType=offers_models.ImageType.RECTO, uuid=old_recto_uuid
        )
        offers_factories.ProductMediationFactory(
            product=product, imageType=offers_models.ImageType.VERSO, uuid=untouched_verso_uuid
        )
        fixture_item = fixtures.MUSIC_SEARCH_FIXTURE["result"][0]
        bq_product = self._prepare_bq_music_from_fixture(fixture_item)[0]
        bq_product.ean = ean_test
        bq_product.recto_uuid = correct_recto_uuid
        bq_product.verso_uuid = untouched_verso_uuid
        bq_product.has_image = True
        bq_product.has_verso_image = True
        mock_execute.return_value = iter([bq_product])

        BigQueryTiteliveMusicProductSync().run_synchronization(batch_size=self.BATCH_SIZE)

        assert len(product.productMediations) == 2
        assert correct_recto_uuid in product.images[offers_models.ImageType.RECTO.value]
        assert untouched_verso_uuid in product.images[offers_models.ImageType.VERSO.value]
