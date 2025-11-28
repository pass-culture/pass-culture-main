import uuid
from unittest.mock import patch

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.connectors.big_query.queries.product import BigQueryTiteliveBookProductModel
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories
from pcapi.core.fraud.factories import ProductWhitelistFactory
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import constants as providers_constants
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers import models as providers_models
from pcapi.core.providers.titelive_bq_book_search import BigQueryTiteliveBookProductSync
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.offer_mixin import OfferValidationType

from tests.connectors.titelive.fixtures import build_titelive_one_book_response


@pytest.mark.usefixtures("db_session")
class BigQueryTiteliveBookProductSyncTest:
    EAN_TEST = "9782370730541"
    SCHOLAR_BOOK_GTL_ID = providers_constants.GTL_LEVEL_01_SCHOOL + "040300"
    EXTRACURRICULAR_GTL_ID = providers_constants.GTL_LEVEL_01_EXTRACURRICULAR + "080000"
    BATCH_SIZE = 100

    def _prepare_bq_product_from_fixture(self, fixture: dict) -> BigQueryTiteliveBookProductModel:
        work_data = fixture["result"][0]
        article_data = work_data["article"]["1"]
        merged_data = {
            **article_data,
            "ean": article_data.get("gencod"),
            "titre": work_data["titre"],
            "auteurs_multi": work_data["auteurs_multi"],
        }
        return BigQueryTiteliveBookProductModel.parse_obj(merged_data)

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    def test_synchronize_products_success_logs_events(self, mock_gcp_data, mock_gcp_backend, db_session):
        provider = providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        sync_manager = BigQueryTiteliveBookProductSync()

        with patch.object(sync_manager, "run_synchronization") as mock_run:
            sync_manager.synchronize_products(batch_size=self.BATCH_SIZE)
        mock_run.assert_called_once_with(self.BATCH_SIZE)

        events = (
            db_session.query(providers_models.LocalProviderEvent).order_by(providers_models.LocalProviderEvent.id).all()
        )
        assert len(events) == 2
        assert events[0].type == providers_models.LocalProviderEventType.SyncStart
        assert events[0].provider.id == provider.id
        assert events[1].type == providers_models.LocalProviderEventType.SyncEnd
        assert events[1].provider.id == provider.id

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    def test_synchronize_products_failure_logs_error_event(self, mock_gcp_data, mock_gcp_backend, db_session):
        provider = providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        sync_manager = BigQueryTiteliveBookProductSync()

        with patch.object(sync_manager, "run_synchronization") as mock_run:
            mock_run.side_effect = ValueError("Something went wrong")
            with pytest.raises(ValueError, match="Something went wrong"):
                sync_manager.synchronize_products(batch_size=self.BATCH_SIZE)
        mock_run.assert_called_once()

        events = (
            db_session.query(providers_models.LocalProviderEvent).order_by(providers_models.LocalProviderEvent.id).all()
        )
        assert len(events) == 2
        assert events[0].type == providers_models.LocalProviderEventType.SyncStart
        assert events[0].provider.id == provider.id
        assert events[1].type == providers_models.LocalProviderEventType.SyncError
        assert events[1].provider.id == provider.id
        assert events[1].payload == "paper : ValueError"

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    def test_create_1_product(self, mock_execute, mock_gcp_data, mock_gcp_backend, settings):
        providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        with patch.object(
            BigQueryTiteliveBookProductSync, "_copy_image_from_data_bucket_to_backend_bucket", lambda s, uuid: uuid
        ):
            BigQueryTiteliveBookProductSync().synchronize_products(batch_size=self.BATCH_SIZE)

        product = db.session.query(offers_models.Product).filter_by(ean=self.EAN_TEST).one()
        assert product is not None
        assert product.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert product.ean == self.EAN_TEST
        assert product.name == "The Book of All Things"
        assert product.description == "The book of all the good things"
        assert product.extraData.get("author") == "Eraticerrata"
        assert product.extraData.get("bookFormat") == providers_constants.BookFormat.BEAUX_LIVRES.name
        assert product.extraData.get("editeur") == "ALLARY"
        assert product.extraData.get("date_parution") == "2015-06-11"
        assert product.extraData.get("prix_livre") == "22.9"
        assert product.extraData.get("langueiso") == "fra"
        assert product.extraData.get("gtl_id") == "03020300"

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    def test_handle_bad_product_by_truncating_it(self, mock_execute, mock_gcp_data, mock_gcp_backend, settings):
        providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        long_title = "L'Arabe du futur Tome 2 : une jeunesse au Moyen-Orient (1984-1985) - Edition spéciale avec un titre très long pour tester la longueur de la description"
        fixture = build_titelive_one_book_response(title=long_title, ean=self.EAN_TEST)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        with patch.object(
            BigQueryTiteliveBookProductSync, "_copy_image_from_data_bucket_to_backend_bucket", lambda s, uuid: uuid
        ):
            BigQueryTiteliveBookProductSync().synchronize_products(batch_size=self.BATCH_SIZE)

        product = db.session.query(offers_models.Product).filter_by(ean=self.EAN_TEST).one()
        expected_truncated_title = "L'Arabe du futur Tome 2 : une jeunesse au Moyen-Orient (1984-1985) - Edition spéciale avec un titre très long pour tester la longueur de la…"
        assert product.name == expected_truncated_title
        assert len(product.name) == 140

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    def test_create_1_thing_when_gtl_not_has_lpad_zero(self, mock_execute, mock_gcp_data, mock_gcp_backend, settings):
        providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        unpadded_gtl = "3020300"
        expected_padded_gtl = "03020300"
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST, no_gtl=True)
        fixture["result"][0]["article"]["1"]["gtl"] = {"first": {"1": {"code": unpadded_gtl, "libelle": "Test GTL"}}}
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        with patch.object(
            BigQueryTiteliveBookProductSync, "_copy_image_from_data_bucket_to_backend_bucket", lambda s, uuid: uuid
        ):
            BigQueryTiteliveBookProductSync().synchronize_products(batch_size=self.BATCH_SIZE)

        product = db.session.query(offers_models.Product).filter_by(ean=self.EAN_TEST).one()
        assert product.extraData.get("gtl_id") == expected_padded_gtl

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    @pytest.mark.parametrize(
        "auteurs_multi_from_bq, expected_author_string",
        [
            (["John Mc Crae"], "John Mc Crae"),
            (["John Mc Crae", "John Doe"], "John Mc Crae, John Doe"),
            ("John Smith", "John Smith"),
            ({"auteur": "John Mc Crae", "auteur2": "Eraticerrata"}, "John Mc Crae, Eraticerrata"),
            (1234, None),
        ],
    )
    def test_handles_all_authors_formats(
        self, mock_execute, mock_gcp_data, mock_gcp_backend, settings, auteurs_multi_from_bq, expected_author_string
    ):
        providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST, auteurs_multi=auteurs_multi_from_bq)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        with patch.object(
            BigQueryTiteliveBookProductSync, "_copy_image_from_data_bucket_to_backend_bucket", lambda s, uuid: uuid
        ):
            BigQueryTiteliveBookProductSync().synchronize_products(batch_size=self.BATCH_SIZE)

        product = db.session.query(offers_models.Product).filter_by(ean=self.EAN_TEST).one()
        assert product.extraData.get("author") == expected_author_string

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    def test_does_not_create_product_when_product_is_gtl_school_book(
        self, mock_execute, mock_gcp_data, mock_gcp_backend, settings
    ):
        providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST, gtl_id=self.SCHOLAR_BOOK_GTL_ID, gtl_level=3)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        with patch.object(
            BigQueryTiteliveBookProductSync, "_copy_image_from_data_bucket_to_backend_bucket", lambda s, uuid: uuid
        ):
            BigQueryTiteliveBookProductSync().synchronize_products(batch_size=self.BATCH_SIZE)

        assert db.session.query(offers_models.Product).count() == 0

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    @pytest.mark.parametrize("taux_tva", ["20", "20.00"])
    def test_does_not_create_product_when_product_is_vat_20(
        self, mock_execute, mock_gcp_data, mock_gcp_backend, settings, taux_tva
    ):
        providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST, taux_tva=taux_tva)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        with patch.object(
            BigQueryTiteliveBookProductSync, "_copy_image_from_data_bucket_to_backend_bucket", lambda s, uuid: uuid
        ):
            BigQueryTiteliveBookProductSync().synchronize_products(batch_size=self.BATCH_SIZE)

        assert db.session.query(offers_models.Product).count() == 0

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    def test_does_not_create_product_when_product_is_extracurricular(
        self, mock_execute, mock_gcp_data, mock_gcp_backend, settings
    ):
        providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST, gtl_id=self.EXTRACURRICULAR_GTL_ID, gtl_level=2)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        with patch.object(
            BigQueryTiteliveBookProductSync, "_copy_image_from_data_bucket_to_backend_bucket", lambda s, uuid: uuid
        ):
            BigQueryTiteliveBookProductSync().synchronize_products(batch_size=self.BATCH_SIZE)

        assert db.session.query(offers_models.Product).count() == 0

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    @pytest.mark.parametrize(
        "support_code",
        [
            providers_constants.CALENDAR_SUPPORT_CODE,
            providers_constants.POSTER_SUPPORT_CODE,
            providers_constants.PAPER_CONSUMABLE_SUPPORT_CODE,
            providers_constants.BOX_SUPPORT_CODE,
            providers_constants.OBJECT_SUPPORT_CODE,
        ],
    )
    def test_does_not_create_product_when_product_is_non_eligible_support_code(
        self, mock_execute, mock_gcp_data, mock_gcp_backend, settings, support_code
    ):
        providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST, support_code=support_code)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        with patch.object(
            BigQueryTiteliveBookProductSync, "_copy_image_from_data_bucket_to_backend_bucket", lambda s, uuid: uuid
        ):
            BigQueryTiteliveBookProductSync().synchronize_products(batch_size=self.BATCH_SIZE)

        assert db.session.query(offers_models.Product).count() == 0

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    def test_does_not_create_product_when_product_is_lectorat_eighteen(
        self, mock_execute, mock_gcp_data, mock_gcp_backend, settings
    ):
        providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        fixture = build_titelive_one_book_response(
            ean=self.EAN_TEST, id_lectorat=providers_constants.LECTORAT_EIGHTEEN_ID
        )
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        with patch.object(
            BigQueryTiteliveBookProductSync, "_copy_image_from_data_bucket_to_backend_bucket", lambda s, uuid: uuid
        ):
            BigQueryTiteliveBookProductSync().synchronize_products(batch_size=self.BATCH_SIZE)

        assert db.session.query(offers_models.Product).count() == 0

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    @pytest.mark.parametrize(
        "level_02_code_gtl",
        [
            providers_constants.GTL_LEVEL_02_BEFORE_3,
            providers_constants.GTL_LEVEL_02_AFTER_3_AND_BEFORE_6,
        ],
    )
    def test_does_not_create_product_when_product_is_small_young(
        self, mock_execute, mock_gcp_data, mock_gcp_backend, settings, level_02_code_gtl
    ):
        providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        young_gtl_id = providers_constants.GTL_LEVEL_01_YOUNG + level_02_code_gtl + "0000"
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST, gtl_id=young_gtl_id, gtl_level=2)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        with patch.object(
            BigQueryTiteliveBookProductSync, "_copy_image_from_data_bucket_to_backend_bucket", lambda s, uuid: uuid
        ):
            BigQueryTiteliveBookProductSync().synchronize_products(batch_size=self.BATCH_SIZE)

        assert db.session.query(offers_models.Product).count() == 0

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    @pytest.mark.parametrize("title", ["Le guide officiel du test TOEIC", "Réussir le TOEFL"])
    def test_does_not_create_product_when_product_is_toeic_or_toefl(
        self, mock_execute, mock_gcp_data, mock_gcp_backend, settings, title
    ):
        providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST, title=title)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        with patch.object(
            BigQueryTiteliveBookProductSync, "_copy_image_from_data_bucket_to_backend_bucket", lambda s, uuid: uuid
        ):
            BigQueryTiteliveBookProductSync().synchronize_products(batch_size=self.BATCH_SIZE)

        assert db.session.query(offers_models.Product).count() == 0

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    def test_does_not_create_product_when_product_is_paper_press(
        self, mock_execute, mock_gcp_data, mock_gcp_backend, settings
    ):
        providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        fixture = build_titelive_one_book_response(
            ean=self.EAN_TEST, support_code=providers_constants.PAPER_PRESS_SUPPORT_CODE, taux_tva="2.10"
        )
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        with patch.object(
            BigQueryTiteliveBookProductSync, "_copy_image_from_data_bucket_to_backend_bucket", lambda s, uuid: uuid
        ):
            BigQueryTiteliveBookProductSync().synchronize_products(batch_size=self.BATCH_SIZE)

        assert db.session.query(offers_models.Product).count() == 0

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    def test_creates_product_when_ineligible_but_in_whitelist(
        self, mock_execute, mock_gcp_data, mock_gcp_backend, settings
    ):
        providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        ProductWhitelistFactory.create(ean=self.EAN_TEST)
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST, gtl_id=self.SCHOLAR_BOOK_GTL_ID, gtl_level=3)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        with patch.object(
            BigQueryTiteliveBookProductSync, "_copy_image_from_data_bucket_to_backend_bucket", lambda s, uuid: uuid
        ):
            BigQueryTiteliveBookProductSync().synchronize_products(batch_size=self.BATCH_SIZE)

        assert db.session.query(offers_models.Product).count() == 1
        product = db.session.query(offers_models.Product).filter_by(ean=self.EAN_TEST).one()
        assert product is not None

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    def test_update_offers_extra_data_from_thing(self, mock_execute, mock_gcp_data, mock_gcp_backend, settings):
        provider = providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        initial_extra_data = {
            "date_parution": "2000-01-01",
            "prix_livre": "99.99",
            "bookFormat": "POCHE",
            "editeur": "Ancien Éditeur",
        }
        offers_factories.ProductFactory.create(
            ean=self.EAN_TEST,
            extraData=initial_extra_data,
            lastProviderId=provider.id,
        )
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        with patch.object(
            BigQueryTiteliveBookProductSync, "_copy_image_from_data_bucket_to_backend_bucket", lambda s, uuid: uuid
        ):
            BigQueryTiteliveBookProductSync().synchronize_products(batch_size=self.BATCH_SIZE)

        product = db.session.query(offers_models.Product).filter_by(ean=self.EAN_TEST).one()
        assert product.extraData.get("date_parution") == "2015-06-11"
        assert product.extraData.get("prix_livre") == "22.9"
        assert product.extraData.get("bookFormat") == providers_constants.BookFormat.BEAUX_LIVRES.name
        assert product.extraData.get("editeur") == "ALLARY"

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    def test_update_should_not_override_fraud_incompatibility(
        self, mock_execute, mock_gcp_data, mock_gcp_backend, settings
    ):
        provider = providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        offers_factories.ProductFactory.create(
            ean=self.EAN_TEST,
            name="Ancien Titre",
            gcuCompatibilityType=offers_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE,
            lastProviderId=provider.id,
        )
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST, title="Titre Mis à Jour")
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        with patch.object(
            BigQueryTiteliveBookProductSync, "_copy_image_from_data_bucket_to_backend_bucket", lambda s, uuid: uuid
        ):
            BigQueryTiteliveBookProductSync().synchronize_products(batch_size=self.BATCH_SIZE)

        product = db.session.query(offers_models.Product).filter_by(ean=self.EAN_TEST).one()
        assert product.name == "Titre Mis à Jour"
        assert product.gcuCompatibilityType == offers_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    def test_should_reject_product_when_it_becomes_ineligible(
        self, mock_execute, mock_gcp_data, mock_gcp_backend, settings
    ):
        provider = providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        product = offers_factories.ProductFactory.create(ean=self.EAN_TEST, lastProviderId=provider.id)
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST, gtl_id=self.SCHOLAR_BOOK_GTL_ID, gtl_level=3)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        with patch.object(
            BigQueryTiteliveBookProductSync, "_copy_image_from_data_bucket_to_backend_bucket", lambda s, uuid: uuid
        ):
            BigQueryTiteliveBookProductSync().synchronize_products(batch_size=self.BATCH_SIZE)

        assert product.gcuCompatibilityType == offers_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    def test_should_reject_product_and_cancel_bookings(self, mock_execute, mock_gcp_data, mock_gcp_backend, settings):
        provider = providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        product = offers_factories.ProductFactory.create(ean=self.EAN_TEST, lastProviderId=provider.id)
        offer = offers_factories.OfferFactory.create(product=product)
        stock = offers_factories.StockFactory.create(offer=offer)
        booking = bookings_factories.BookingFactory.create(stock=stock)
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST, gtl_id=self.SCHOLAR_BOOK_GTL_ID, gtl_level=3)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        with patch.object(
            BigQueryTiteliveBookProductSync, "_copy_image_from_data_bucket_to_backend_bucket", lambda s, uuid: uuid
        ):
            BigQueryTiteliveBookProductSync().synchronize_products(batch_size=self.BATCH_SIZE)

        assert product.gcuCompatibilityType == offers_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE
        assert offer.validation == OfferValidationStatus.REJECTED
        assert booking.status == bookings_models.BookingStatus.CANCELLED

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    def test_should_approve_product_when_it_becomes_eligible(
        self, mock_execute, mock_gcp_data, mock_gcp_backend, settings
    ):
        provider = providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        product = offers_factories.ProductFactory.create(
            ean=self.EAN_TEST,
            lastProviderId=provider.id,
            gcuCompatibilityType=offers_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        )
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        with patch.object(
            BigQueryTiteliveBookProductSync, "_copy_image_from_data_bucket_to_backend_bucket", lambda s, uuid: uuid
        ):
            BigQueryTiteliveBookProductSync().synchronize_products(batch_size=self.BATCH_SIZE)

        assert product.isGcuCompatible == True

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    def test_should_approve_product_and_offers(self, mock_execute, mock_gcp_data, mock_gcp_backend, settings):
        provider = providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        product = offers_factories.ProductFactory.create(
            ean=self.EAN_TEST,
            lastProviderId=provider.id,
            gcuCompatibilityType=offers_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        )
        offer = offers_factories.OfferFactory.create(
            product=product,
            validation=OfferValidationStatus.REJECTED,
            lastValidationType=OfferValidationType.CGU_INCOMPATIBLE_PRODUCT,
        )
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        with patch.object(
            BigQueryTiteliveBookProductSync, "_copy_image_from_data_bucket_to_backend_bucket", lambda s, uuid: uuid
        ):
            BigQueryTiteliveBookProductSync().synchronize_products(batch_size=self.BATCH_SIZE)

        assert product.isGcuCompatible == True
        assert offer.validation == OfferValidationStatus.APPROVED

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    def test_approval_should_not_override_fraud_incompatibility(
        self, mock_execute, mock_gcp_data, mock_gcp_backend, settings
    ):
        provider = providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        product = offers_factories.ProductFactory.create(
            ean=self.EAN_TEST,
            lastProviderId=provider.id,
            gcuCompatibilityType=offers_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE,
        )
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        with patch.object(
            BigQueryTiteliveBookProductSync, "_copy_image_from_data_bucket_to_backend_bucket", lambda s, uuid: uuid
        ):
            BigQueryTiteliveBookProductSync().synchronize_products(batch_size=self.BATCH_SIZE)

        assert product.gcuCompatibilityType == offers_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch(
        "pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductSync._copy_image_from_data_bucket_to_backend_bucket"
    )
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    def test_creates_images_for_new_product(self, mock_execute, mock_copy_image, mock_gcp_data, mock_gcp_backend):
        mock_copy_image.side_effect = lambda uuid: uuid
        providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        recto_uuid = str(uuid.uuid4())
        verso_uuid = str(uuid.uuid4())
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        bq_product.recto_uuid = recto_uuid
        bq_product.verso_uuid = verso_uuid
        bq_product.has_image = True
        bq_product.has_verso_image = True
        mock_execute.return_value = iter([bq_product])

        BigQueryTiteliveBookProductSync().run_synchronization(batch_size=self.BATCH_SIZE)

        product = db.session.query(offers_models.Product).filter_by(ean=self.EAN_TEST).one()
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
        "pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductSync._copy_image_from_data_bucket_to_backend_bucket"
    )
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    def test_replaces_all_images_on_full_update(self, mock_execute, mock_copy_image, mock_gcp_data, mock_gcp_backend):
        mock_copy_image.side_effect = lambda uuid: uuid
        provider = providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        product = offers_factories.ProductFactory(ean=self.EAN_TEST, lastProviderId=provider.id)
        offers_factories.ProductMediationFactory(
            product=product, imageType=offers_models.ImageType.RECTO, uuid="old-recto-uuid"
        )
        offers_factories.ProductMediationFactory(
            product=product, imageType=offers_models.ImageType.VERSO, uuid="old-verso-uuid"
        )
        new_recto_uuid = str(uuid.uuid4())
        new_verso_uuid = str(uuid.uuid4())
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        bq_product.recto_uuid = new_recto_uuid
        bq_product.verso_uuid = new_verso_uuid
        bq_product.has_image = True
        bq_product.has_verso_image = True
        mock_execute.return_value = iter([bq_product])

        BigQueryTiteliveBookProductSync().run_synchronization(batch_size=self.BATCH_SIZE)

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
        "pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductSync._copy_image_from_data_bucket_to_backend_bucket"
    )
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    def test_replaces_only_provided_images_on_partial_update(
        self, mock_execute, mock_copy_image, mock_gcp_data, mock_gcp_backend
    ):
        mock_copy_image.side_effect = lambda uuid: uuid
        provider = providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        product = offers_factories.ProductFactory(ean=self.EAN_TEST, lastProviderId=provider.id)
        offers_factories.ProductMediationFactory(
            product=product, imageType=offers_models.ImageType.RECTO, uuid="old-recto-uuid"
        )
        offers_factories.ProductMediationFactory(
            product=product, imageType=offers_models.ImageType.VERSO, uuid="old-verso-uuid"
        )

        new_recto_uuid = str(uuid.uuid4())
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        bq_product.recto_uuid = new_recto_uuid
        bq_product.verso_uuid = None
        bq_product.has_image = True
        bq_product.has_verso_image = False
        mock_execute.return_value = iter([bq_product])

        BigQueryTiteliveBookProductSync().run_synchronization(batch_size=self.BATCH_SIZE)

        mediations = db.session.query(offers_models.ProductMediation).filter_by(productId=product.id).all()
        assert len(mediations) == 2
        mediation_map = {m.imageType: m.uuid for m in mediations}
        assert mediation_map[offers_models.ImageType.RECTO] == new_recto_uuid
        assert mediation_map[offers_models.ImageType.VERSO] == "old-verso-uuid"
        mock_copy_image.assert_called_once_with(new_recto_uuid)

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch(
        "pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductSync._copy_image_from_data_bucket_to_backend_bucket"
    )
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    def test_does_not_change_images_when_uuids_are_null(
        self, mock_execute, mock_copy_image, mock_gcp_data, mock_gcp_backend
    ):
        mock_copy_image.side_effect = lambda uuid: uuid
        provider = providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        product = offers_factories.ProductFactory(ean=self.EAN_TEST, lastProviderId=provider.id)
        offers_factories.ProductMediationFactory(
            product=product, imageType=offers_models.ImageType.RECTO, uuid="old-recto-uuid"
        )
        offers_factories.ProductMediationFactory(
            product=product, imageType=offers_models.ImageType.VERSO, uuid="old-verso-uuid"
        )
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        bq_product.recto_uuid = None
        bq_product.verso_uuid = None
        bq_product.has_image = True
        bq_product.has_verso_image = False
        mock_execute.return_value = iter([bq_product])

        BigQueryTiteliveBookProductSync().run_synchronization(batch_size=self.BATCH_SIZE)

        mediations = db.session.query(offers_models.ProductMediation).filter_by(productId=product.id).all()
        assert len(mediations) == 2
        mediation_map = {m.imageType: m.uuid for m in mediations}
        assert mediation_map[offers_models.ImageType.RECTO] == "old-recto-uuid"
        assert mediation_map[offers_models.ImageType.VERSO] == "old-verso-uuid"
        mock_copy_image.assert_not_called()

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
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
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        bq_product.recto_uuid = recto_uuid
        bq_product.has_image = True
        bq_product.has_verso_image = False
        mock_execute.return_value = iter([bq_product])

        sync_manager = BigQueryTiteliveBookProductSync()
        sync_manager.run_synchronization(batch_size=self.BATCH_SIZE)

        product = db.session.query(offers_models.Product).filter_by(ean=self.EAN_TEST).one_or_none()
        assert product is not None
        mediations_count = db.session.query(offers_models.ProductMediation).filter_by(productId=product.id).count()
        assert mediations_count == 0

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    def test_gcp_exception_during_image_update_does_not_delete_old_image(
        self, mock_execute, mock_gcp_data_class, mock_gcp_backend_class
    ):
        mock_gcp_data_instance = mock_gcp_data_class.return_value
        mock_gcp_backend_instance = mock_gcp_backend_class.return_value
        provider = providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        old_recto_uuid = "old-recto-uuid-12345"
        product = offers_factories.ProductFactory(ean=self.EAN_TEST, lastProviderId=provider.id, name="Old Name")
        offers_factories.ProductMediationFactory(
            product=product, imageType=offers_models.ImageType.RECTO, uuid=old_recto_uuid
        )
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST, title="New Updated Name")
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        bq_product.recto_uuid = str(uuid.uuid4())
        bq_product.has_image = True
        bq_product.has_verso_image = False
        mock_execute.return_value = iter([bq_product])
        mock_gcp_backend_instance.object_exists.return_value = False
        mock_gcp_data_instance.object_exists.return_value = True
        mock_gcp_data_instance.copy_object_to.side_effect = Exception("Simulated GCP BUCKET FAILURE")

        sync_manager = BigQueryTiteliveBookProductSync()
        sync_manager.run_synchronization(batch_size=self.BATCH_SIZE)

        assert product.name == "New Updated Name"
        mediations = db.session.query(offers_models.ProductMediation).filter_by(productId=product.id).all()
        assert len(mediations) == 1
        assert mediations[0].imageType == offers_models.ImageType.RECTO
        assert mediations[0].uuid == old_recto_uuid

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    def test_batch_transaction_failure_triggers_individual_retry_success(
        self, mock_execute, mock_gcp_data, mock_gcp_backend
    ):
        providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        EAN_1 = "9780000000001"
        EAN_2 = "9780000000002"
        fixture1 = build_titelive_one_book_response(ean=EAN_1, title="Product 1")
        bq_product1 = self._prepare_bq_product_from_fixture(fixture1)
        fixture2 = build_titelive_one_book_response(ean=EAN_2, title="Product 2")
        bq_product2 = self._prepare_bq_product_from_fixture(fixture2)
        mock_execute.return_value = iter([bq_product1, bq_product2])

        with patch("pcapi.models.db.session.commit") as mock_commit:
            mock_commit.side_effect = [
                Exception("Simulated Batch Commit Failure"),  # Batch commit fail
                None,  # individual commit for product 1
                None,  # individual commit for product 2
            ]
            with patch.object(
                BigQueryTiteliveBookProductSync, "_copy_image_from_data_bucket_to_backend_bucket", lambda s, uuid: uuid
            ):
                sync_manager = BigQueryTiteliveBookProductSync()
                sync_manager.run_synchronization(batch_size=self.BATCH_SIZE)

        product1 = db.session.query(offers_models.Product).filter_by(ean=EAN_1).one_or_none()
        assert product1 is not None
        assert product1.name == "Product 1"
        product2 = db.session.query(offers_models.Product).filter_by(ean=EAN_2).one_or_none()
        assert product2 is not None
        assert product2.name == "Product 2"
        assert mock_commit.call_count == 3

    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPBackend")
    @patch("pcapi.core.providers.titelive_bq_sync_base.GCPData")
    @patch("pcapi.core.providers.titelive_bq_book_search.BigQueryTiteliveBookProductDeltaQuery.execute")
    def test_sync_images_cleans_up_duplicates_when_correct_mediation_exists(
        self, mock_execute, mock_gcp_data, mock_gcp_backend
    ):
        provider = providers_factories.ProviderFactory.create(name=providers_constants.TITELIVE_ENRICHED_BY_DATA)
        product = offers_factories.ProductFactory(ean=self.EAN_TEST, lastProviderId=provider.id)
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
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        bq_product.recto_uuid = correct_recto_uuid
        bq_product.verso_uuid = untouched_verso_uuid
        bq_product.has_image = True
        bq_product.has_verso_image = True
        mock_execute.return_value = iter([bq_product])

        BigQueryTiteliveBookProductSync().run_synchronization(batch_size=self.BATCH_SIZE)

        assert len(product.productMediations) == 2
        assert correct_recto_uuid in product.images[offers_models.ImageType.RECTO.value]
        assert untouched_verso_uuid in product.images[offers_models.ImageType.VERSO.value]
