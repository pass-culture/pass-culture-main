import datetime
import uuid
from unittest.mock import patch

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.connectors.big_query.queries.product import BigQueryProductModel
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories
from pcapi.core.fraud.factories import ProductWhitelistFactory
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.products import factories as products_factories
from pcapi.core.products import models as products_models
from pcapi.core.providers import constants as providers_constants
from pcapi.core.providers import models as providers_models
from pcapi.core.providers.repository import get_provider_by_name
from pcapi.core.providers.titelive_bq_book_search import BigQueryProductSync
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.offer_mixin import OfferValidationType

from tests.connectors.titelive.fixtures import build_titelive_one_book_response


@pytest.mark.usefixtures("db_session")
class BigQueryProductSyncTest:
    EAN_TEST = "9782370730541"
    SCHOLAR_BOOK_GTL_ID = providers_constants.GTL_LEVEL_01_SCHOOL + "040300"
    EXTRACURRICULAR_GTL_ID = providers_constants.GTL_LEVEL_01_EXTRACURRICULAR + "080000"

    def _prepare_bq_product_from_fixture(self, fixture: dict) -> BigQueryProductModel:
        work_data = fixture["result"][0]
        article_data = work_data["article"]["1"]
        merged_data = {
            **article_data,
            "titre": work_data["titre"],
            "auteurs_multi": work_data["auteurs_multi"],
        }
        return BigQueryProductModel.parse_obj(merged_data)

    def test_synchronize_products_success_logs_events(self, db_session):
        from_date = datetime.datetime(2025, 9, 1)
        to_date = datetime.datetime(2025, 9, 2)
        provider = (
            db.session.query(providers_models.Provider)
            .filter_by(name=providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME)
            .one()
        )
        sync_manager = BigQueryProductSync()

        with patch.object(sync_manager, "run_synchronization") as mock_run:
            sync_manager.synchronize_products(from_date=from_date, to_date=to_date)
        mock_run.assert_called_once_with(from_date, to_date)

        events = (
            db_session.query(providers_models.LocalProviderEvent).order_by(providers_models.LocalProviderEvent.id).all()
        )
        assert len(events) == 2
        assert events[0].type == providers_models.LocalProviderEventType.SyncStart
        assert events[0].provider.id == provider.id
        assert events[1].type == providers_models.LocalProviderEventType.SyncEnd
        assert events[1].provider.id == provider.id

    def test_synchronize_products_failure_logs_error_event(self, db_session):
        from_date = datetime.datetime(2025, 9, 1)
        to_date = datetime.datetime(2025, 9, 2)
        provider = (
            db_session.query(providers_models.Provider)
            .filter_by(name=providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME)
            .one()
        )
        sync_manager = BigQueryProductSync()

        with patch.object(sync_manager, "run_synchronization") as mock_run:
            mock_run.side_effect = ValueError("Something went wrong")
            with pytest.raises(ValueError, match="Something went wrong"):
                sync_manager.synchronize_products(from_date=from_date, to_date=to_date)
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

    def test_synchronize_products_aborts_if_dates_invalid(self, db_session, caplog):
        from_date = datetime.datetime(2025, 9, 2)
        to_date = datetime.datetime(2025, 9, 1)
        sync_manager = BigQueryProductSync()

        with patch.object(sync_manager, "run_synchronization") as mock_run:
            sync_manager.synchronize_products(from_date=from_date, to_date=to_date)
        mock_run.assert_not_called()

        events_count = db_session.query(providers_models.LocalProviderEvent).count()
        assert events_count == 0
        assert "Start date" in caplog.text
        assert "is after end date" in caplog.text
        assert "Aborting synchronization" in caplog.text

    @patch("pcapi.core.providers.titelive_bq_book_search.ProductsToSyncQuery.execute")
    def test_create_1_product(self, mock_execute, settings):
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        BigQueryProductSync().synchronize_products(
            from_date=datetime.datetime(2024, 1, 1), to_date=datetime.datetime(2024, 1, 2)
        )

        product = db.session.query(products_models.Product).filter_by(ean=self.EAN_TEST).one()
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

    @patch("pcapi.core.providers.titelive_bq_book_search.ProductsToSyncQuery.execute")
    def test_handle_bad_product_by_truncating_it(self, mock_execute, settings):
        long_title = "L'Arabe du futur Tome 2 : une jeunesse au Moyen-Orient (1984-1985) - Edition spéciale avec un titre très long pour tester la longueur de la description"
        fixture = build_titelive_one_book_response(title=long_title, ean=self.EAN_TEST)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        BigQueryProductSync().synchronize_products(
            from_date=datetime.datetime(2024, 1, 1), to_date=datetime.datetime(2024, 1, 2)
        )

        product = db.session.query(products_models.Product).filter_by(ean=self.EAN_TEST).one()
        expected_truncated_title = "L'Arabe du futur Tome 2 : une jeunesse au Moyen-Orient (1984-1985) - Edition spéciale avec un titre très long pour tester la longueur de la…"
        assert product.name == expected_truncated_title
        assert len(product.name) == 140

    @patch("pcapi.core.providers.titelive_bq_book_search.ProductsToSyncQuery.execute")
    def test_create_1_thing_when_gtl_not_has_lpad_zero(self, mock_execute, settings):
        unpadded_gtl = "3020300"
        expected_padded_gtl = "03020300"
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST, no_gtl=True)
        fixture["result"][0]["article"]["1"]["gtl"] = {"first": {"1": {"code": unpadded_gtl, "libelle": "Test GTL"}}}
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        BigQueryProductSync().synchronize_products(
            from_date=datetime.datetime(2024, 1, 1), to_date=datetime.datetime(2024, 1, 2)
        )

        product = db.session.query(products_models.Product).filter_by(ean=self.EAN_TEST).one()
        assert product.extraData.get("gtl_id") == expected_padded_gtl

    @patch("pcapi.core.providers.titelive_bq_book_search.ProductsToSyncQuery.execute")
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
    def test_handles_all_authors_formats(self, mock_execute, settings, auteurs_multi_from_bq, expected_author_string):
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST, auteurs_multi=auteurs_multi_from_bq)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        BigQueryProductSync().synchronize_products(
            from_date=datetime.datetime(2024, 1, 1), to_date=datetime.datetime(2024, 1, 2)
        )

        product = db.session.query(products_models.Product).filter_by(ean=self.EAN_TEST).one()
        assert product.extraData.get("author") == expected_author_string

    @patch("pcapi.core.providers.titelive_bq_book_search.ProductsToSyncQuery.execute")
    def test_does_not_create_product_when_product_is_gtl_school_book(self, mock_execute, settings):
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST, gtl_id=self.SCHOLAR_BOOK_GTL_ID, gtl_level=3)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        BigQueryProductSync().synchronize_products(
            from_date=datetime.datetime(2024, 1, 1), to_date=datetime.datetime(2024, 1, 2)
        )

        assert db.session.query(products_models.Product).count() == 0

    @patch("pcapi.core.providers.titelive_bq_book_search.ProductsToSyncQuery.execute")
    @pytest.mark.parametrize("taux_tva", ["20", "20.00"])
    def test_does_not_create_product_when_product_is_vat_20(self, mock_execute, settings, taux_tva):
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST, taux_tva=taux_tva)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        BigQueryProductSync().synchronize_products(
            from_date=datetime.datetime(2024, 1, 1), to_date=datetime.datetime(2024, 1, 2)
        )

        assert db.session.query(products_models.Product).count() == 0

    @patch("pcapi.core.providers.titelive_bq_book_search.ProductsToSyncQuery.execute")
    def test_does_not_create_product_when_product_is_extracurricular(self, mock_execute, settings):
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST, gtl_id=self.EXTRACURRICULAR_GTL_ID, gtl_level=2)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        BigQueryProductSync().synchronize_products(
            from_date=datetime.datetime(2024, 1, 1), to_date=datetime.datetime(2024, 1, 2)
        )

        assert db.session.query(products_models.Product).count() == 0

    @patch("pcapi.core.providers.titelive_bq_book_search.ProductsToSyncQuery.execute")
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
        self, mock_execute, settings, support_code
    ):
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST, support_code=support_code)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        BigQueryProductSync().synchronize_products(
            from_date=datetime.datetime(2024, 1, 1), to_date=datetime.datetime(2024, 1, 2)
        )

        assert db.session.query(products_models.Product).count() == 0

    @patch("pcapi.core.providers.titelive_bq_book_search.ProductsToSyncQuery.execute")
    def test_does_not_create_product_when_product_is_lectorat_eighteen(self, mock_execute, settings):
        fixture = build_titelive_one_book_response(
            ean=self.EAN_TEST, id_lectorat=providers_constants.LECTORAT_EIGHTEEN_ID
        )
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        BigQueryProductSync().synchronize_products(
            from_date=datetime.datetime(2024, 1, 1), to_date=datetime.datetime(2024, 1, 2)
        )

        assert db.session.query(products_models.Product).count() == 0

    @patch("pcapi.core.providers.titelive_bq_book_search.ProductsToSyncQuery.execute")
    @pytest.mark.parametrize(
        "level_02_code_gtl",
        [
            providers_constants.GTL_LEVEL_02_BEFORE_3,
            providers_constants.GTL_LEVEL_02_AFTER_3_AND_BEFORE_6,
        ],
    )
    def test_does_not_create_product_when_product_is_small_young(self, mock_execute, settings, level_02_code_gtl):
        young_gtl_id = providers_constants.GTL_LEVEL_01_YOUNG + level_02_code_gtl + "0000"
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST, gtl_id=young_gtl_id, gtl_level=2)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        BigQueryProductSync().synchronize_products(
            from_date=datetime.datetime(2024, 1, 1), to_date=datetime.datetime(2024, 1, 2)
        )

        assert db.session.query(products_models.Product).count() == 0

    @patch("pcapi.core.providers.titelive_bq_book_search.ProductsToSyncQuery.execute")
    @pytest.mark.parametrize("title", ["Le guide officiel du test TOEIC", "Réussir le TOEFL"])
    def test_does_not_create_product_when_product_is_toeic_or_toefl(self, mock_execute, settings, title):
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST, title=title)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        BigQueryProductSync().synchronize_products(
            from_date=datetime.datetime(2024, 1, 1), to_date=datetime.datetime(2024, 1, 2)
        )

        assert db.session.query(products_models.Product).count() == 0

    @patch("pcapi.core.providers.titelive_bq_book_search.ProductsToSyncQuery.execute")
    def test_does_not_create_product_when_product_is_paper_press(self, mock_execute, settings):
        fixture = build_titelive_one_book_response(
            ean=self.EAN_TEST, support_code=providers_constants.PAPER_PRESS_SUPPORT_CODE, taux_tva="2.10"
        )
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        BigQueryProductSync().synchronize_products(
            from_date=datetime.datetime(2024, 1, 1), to_date=datetime.datetime(2024, 1, 2)
        )

        assert db.session.query(products_models.Product).count() == 0

    @patch("pcapi.core.providers.titelive_bq_book_search.ProductsToSyncQuery.execute")
    def test_creates_product_when_ineligible_but_in_whitelist(self, mock_execute, settings):
        ProductWhitelistFactory.create(ean=self.EAN_TEST)
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST, gtl_id=self.SCHOLAR_BOOK_GTL_ID, gtl_level=3)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        BigQueryProductSync().synchronize_products(
            from_date=datetime.datetime(2024, 1, 1), to_date=datetime.datetime(2024, 1, 2)
        )

        assert db.session.query(products_models.Product).count() == 1
        product = db.session.query(products_models.Product).filter_by(ean=self.EAN_TEST).one()
        assert product is not None

    @patch("pcapi.core.providers.titelive_bq_book_search.ProductsToSyncQuery.execute")
    def test_update_offers_extra_data_from_thing(self, mock_execute, settings):
        provider = get_provider_by_name(providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME)
        initial_extra_data = {
            "date_parution": "2000-01-01",
            "prix_livre": "99.99",
            "bookFormat": "POCHE",
            "editeur": "Ancien Éditeur",
        }
        products_factories.ProductFactory.create(
            ean=self.EAN_TEST,
            extraData=initial_extra_data,
            lastProviderId=provider.id,
        )
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        BigQueryProductSync().synchronize_products(
            from_date=datetime.datetime(2024, 1, 1), to_date=datetime.datetime(2024, 1, 2)
        )

        product = db.session.query(products_models.Product).filter_by(ean=self.EAN_TEST).one()
        assert product.extraData.get("date_parution") == "2015-06-11"
        assert product.extraData.get("prix_livre") == "22.9"
        assert product.extraData.get("bookFormat") == providers_constants.BookFormat.BEAUX_LIVRES.name
        assert product.extraData.get("editeur") == "ALLARY"

    @patch("pcapi.core.providers.titelive_bq_book_search.ProductsToSyncQuery.execute")
    def test_update_should_not_override_fraud_incompatibility(self, mock_execute, settings):
        provider = get_provider_by_name(providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME)
        products_factories.ProductFactory.create(
            ean=self.EAN_TEST,
            name="Ancien Titre",
            gcuCompatibilityType=products_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE,
            lastProviderId=provider.id,
        )
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST, title="Titre Mis à Jour")
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        BigQueryProductSync().synchronize_products(
            from_date=datetime.datetime(2024, 1, 1), to_date=datetime.datetime(2024, 1, 2)
        )

        product = db.session.query(products_models.Product).filter_by(ean=self.EAN_TEST).one()
        assert product.name == "Titre Mis à Jour"
        assert product.gcuCompatibilityType == products_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE

    @patch("pcapi.core.providers.titelive_bq_book_search.ProductsToSyncQuery.execute")
    def test_should_reject_product_when_it_becomes_ineligible(self, mock_execute, settings):
        provider = get_provider_by_name(providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME)
        product = products_factories.ProductFactory.create(ean=self.EAN_TEST, lastProviderId=provider.id)
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST, gtl_id=self.SCHOLAR_BOOK_GTL_ID, gtl_level=3)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        BigQueryProductSync().synchronize_products(
            from_date=datetime.datetime(2024, 1, 1), to_date=datetime.datetime(2024, 1, 2)
        )

        assert product.gcuCompatibilityType == products_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE

    @patch("pcapi.core.providers.titelive_bq_book_search.ProductsToSyncQuery.execute")
    def test_should_reject_product_and_cancel_bookings(self, mock_execute, settings):
        provider = get_provider_by_name(providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME)
        product = products_factories.ProductFactory.create(ean=self.EAN_TEST, lastProviderId=provider.id)
        offer = offers_factories.OfferFactory.create(product=product)
        stock = offers_factories.StockFactory.create(offer=offer)
        booking = bookings_factories.BookingFactory.create(stock=stock)
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST, gtl_id=self.SCHOLAR_BOOK_GTL_ID, gtl_level=3)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        BigQueryProductSync().synchronize_products(
            from_date=datetime.datetime(2024, 1, 1), to_date=datetime.datetime(2024, 1, 2)
        )

        assert product.gcuCompatibilityType == products_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE
        assert offer.validation == OfferValidationStatus.REJECTED
        assert booking.status == bookings_models.BookingStatus.CANCELLED

    @patch("pcapi.core.providers.titelive_bq_book_search.ProductsToSyncQuery.execute")
    def test_should_approve_product_when_it_becomes_eligible(self, mock_execute, settings):
        provider = get_provider_by_name(providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME)
        product = products_factories.ProductFactory.create(
            ean=self.EAN_TEST,
            lastProviderId=provider.id,
            gcuCompatibilityType=products_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        )
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        BigQueryProductSync().synchronize_products(
            from_date=datetime.datetime(2024, 1, 1), to_date=datetime.datetime(2024, 1, 2)
        )

        assert product.isGcuCompatible == True

    @patch("pcapi.core.providers.titelive_bq_book_search.ProductsToSyncQuery.execute")
    def test_should_approve_product_and_offers(self, mock_execute, settings):
        provider = get_provider_by_name(providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME)
        product = products_factories.ProductFactory.create(
            ean=self.EAN_TEST,
            lastProviderId=provider.id,
            gcuCompatibilityType=products_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        )
        offer = offers_factories.OfferFactory.create(
            product=product,
            validation=OfferValidationStatus.REJECTED,
            lastValidationType=OfferValidationType.CGU_INCOMPATIBLE_PRODUCT,
        )
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        BigQueryProductSync().synchronize_products(
            from_date=datetime.datetime(2024, 1, 1), to_date=datetime.datetime(2024, 1, 2)
        )

        assert product.isGcuCompatible == True
        assert offer.validation == OfferValidationStatus.APPROVED

    @patch("pcapi.core.providers.titelive_bq_book_search.ProductsToSyncQuery.execute")
    def test_approval_should_not_override_fraud_incompatibility(self, mock_execute, settings):
        provider = get_provider_by_name(providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME)
        product = products_factories.ProductFactory.create(
            ean=self.EAN_TEST,
            lastProviderId=provider.id,
            gcuCompatibilityType=products_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE,
        )
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        mock_execute.return_value = iter([bq_product])

        BigQueryProductSync().synchronize_products(
            from_date=datetime.datetime(2024, 1, 1), to_date=datetime.datetime(2024, 1, 2)
        )

        assert product.gcuCompatibilityType == products_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE

    @patch("pcapi.core.providers.titelive_bq_book_search.ProductsToSyncQuery.execute")
    def test_creates_images_for_new_product(self, mock_execute):
        recto_uuid = str(uuid.uuid4())
        verso_uuid = str(uuid.uuid4())
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        bq_product.recto_uuid = recto_uuid
        bq_product.verso_uuid = verso_uuid
        mock_execute.return_value = iter([bq_product])

        BigQueryProductSync().run_synchronization(
            from_date=datetime.date(2025, 1, 1), to_date=datetime.date(2025, 1, 2)
        )

        product = db.session.query(products_models.Product).filter_by(ean=self.EAN_TEST).one()
        mediations = db.session.query(products_models.ProductMediation).filter_by(productId=product.id).all()
        assert len(mediations) == 2
        mediation_map = {m.imageType: m.uuid for m in mediations}
        assert mediation_map[offers_models.ImageType.RECTO] == recto_uuid
        assert mediation_map[offers_models.ImageType.VERSO] == verso_uuid

    @patch("pcapi.core.providers.titelive_bq_book_search.ProductsToSyncQuery.execute")
    def test_replaces_all_images_on_full_update(self, mock_execute):
        provider = get_provider_by_name(providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME)
        product = products_factories.ProductFactory(ean=self.EAN_TEST, lastProviderId=provider.id)
        products_factories.ProductMediationFactory(
            product=product, imageType=offers_models.ImageType.RECTO, uuid="old-recto-uuid"
        )
        products_factories.ProductMediationFactory(
            product=product, imageType=offers_models.ImageType.VERSO, uuid="old-verso-uuid"
        )
        new_recto_uuid = str(uuid.uuid4())
        new_verso_uuid = str(uuid.uuid4())
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        bq_product.recto_uuid = new_recto_uuid
        bq_product.verso_uuid = new_verso_uuid
        mock_execute.return_value = iter([bq_product])

        BigQueryProductSync().run_synchronization(
            from_date=datetime.date(2025, 1, 1), to_date=datetime.date(2025, 1, 2)
        )

        mediations = db.session.query(products_models.ProductMediation).filter_by(productId=product.id).all()
        assert len(mediations) == 2
        mediation_map = {m.imageType: m.uuid for m in mediations}
        assert mediation_map[offers_models.ImageType.RECTO] == new_recto_uuid
        assert mediation_map[offers_models.ImageType.VERSO] == new_verso_uuid

    @patch("pcapi.core.providers.titelive_bq_book_search.ProductsToSyncQuery.execute")
    def test_replaces_all_images_even_on_partial_update(self, mock_execute):
        provider = get_provider_by_name(providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME)
        product = products_factories.ProductFactory(ean=self.EAN_TEST, lastProviderId=provider.id)
        products_factories.ProductMediationFactory(
            product=product, imageType=offers_models.ImageType.RECTO, uuid="old-recto-uuid"
        )
        products_factories.ProductMediationFactory(
            product=product, imageType=offers_models.ImageType.VERSO, uuid="old-verso-uuid"
        )
        new_recto_uuid = str(uuid.uuid4())
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        bq_product.recto_uuid = new_recto_uuid
        bq_product.verso_uuid = None
        mock_execute.return_value = iter([bq_product])

        BigQueryProductSync().run_synchronization(
            from_date=datetime.date(2025, 1, 1), to_date=datetime.date(2025, 1, 2)
        )

        mediations = db.session.query(products_models.ProductMediation).filter_by(productId=product.id).all()
        assert len(mediations) == 1
        assert mediations[0].imageType == offers_models.ImageType.RECTO
        assert mediations[0].uuid == new_recto_uuid

    @patch("pcapi.core.providers.titelive_bq_book_search.ProductsToSyncQuery.execute")
    def test_does_not_change_images_when_uuids_are_null(self, mock_execute):
        provider = get_provider_by_name(providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME)
        product = products_factories.ProductFactory(ean=self.EAN_TEST, lastProviderId=provider.id)
        products_factories.ProductMediationFactory(
            product=product, imageType=offers_models.ImageType.RECTO, uuid="old-recto-uuid"
        )
        products_factories.ProductMediationFactory(
            product=product, imageType=offers_models.ImageType.VERSO, uuid="old-verso-uuid"
        )
        fixture = build_titelive_one_book_response(ean=self.EAN_TEST)
        bq_product = self._prepare_bq_product_from_fixture(fixture)
        bq_product.recto_uuid = None
        bq_product.verso_uuid = None
        mock_execute.return_value = iter([bq_product])

        BigQueryProductSync().run_synchronization(
            from_date=datetime.date(2025, 1, 1), to_date=datetime.date(2025, 1, 2)
        )

        mediations = db.session.query(products_models.ProductMediation).filter_by(productId=product.id).all()
        assert len(mediations) == 2
        assert mediations[0].uuid == "old-recto-uuid"
        assert mediations[1].uuid == "old-verso-uuid"
