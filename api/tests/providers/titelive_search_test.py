import copy
import datetime
import pathlib
import re

import pytest
import time_machine

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.constants as providers_constants
import pcapi.core.providers.factories as providers_factories
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
from pcapi.connectors import titelive
from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories
from pcapi.core.categories.genres import music
from pcapi.core.fraud.factories import ProductWhitelistFactory
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers.titelive_book_search import TiteliveBookSearch
from pcapi.core.providers.titelive_book_search import extract_eans_from_titelive_response
from pcapi.core.providers.titelive_music_search import TiteliveMusicSearch
from pcapi.core.users.factories import FavoriteFactory
from pcapi.core.users.models import Favorite
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.utils import requests

import tests
from tests.connectors.titelive import fixtures


def _configure_login_and_images(requests_mock, settings):
    requests_mock.post(
        f"{settings.TITELIVE_EPAGINE_API_AUTH_URL}/login/test@example.com/token",
        json={"token": "XYZ"},
    )
    image_path = pathlib.Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
    with open(image_path, "rb") as thumb_file:
        requests_mock.get(re.compile("image"), content=thumb_file.read())


@pytest.mark.settings(TITELIVE_EPAGINE_API_USERNAME="test@example.com", TITELIVE_EPAGINE_API_PASSWORD="qwerty123")
@pytest.mark.usefixtures("db_session")
class TiteliveSearchTest:
    def test_titelive_music_sync(self, requests_mock, settings):
        _configure_login_and_images(requests_mock, settings)
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=1", json=fixtures.MUSIC_SEARCH_FIXTURE)
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=2", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE
        )
        titelive_epagine_provider = providers_repository.get_provider_by_name(
            providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME
        )
        offers_factories.ProductFactory(
            ean="3700187679323", idAtProviders="3700187679323", lastProvider=titelive_epagine_provider
        )

        sync_date = datetime.date(2022, 12, 1)
        TiteliveMusicSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        cd_product = offers_models.Product.query.filter(
            offers_models.Product.idAtProviders == "3700187679323",
            offers_models.Product.lastProvider == titelive_epagine_provider,
        ).one()
        assert cd_product is not None
        assert cd_product.name == "Les dernières volontés de Mozart (symphony)"
        assert cd_product.description == 'GIMS revient avec " Les dernières volontés de Mozart ", un album de tubes.'
        assert cd_product.subcategoryId == subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id
        assert cd_product.ean == "3700187679323"
        assert cd_product.extraData["artist"] == "Gims"
        assert cd_product.extraData["author"] == "Gims"
        assert cd_product.extraData["contenu_explicite"] == "0"
        assert cd_product.extraData["date_parution"] == "2022-12-02"
        assert cd_product.extraData["dispo"] == "1"
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

        shared_gtl_product = (
            db.session.query(offers_models.Product)
            .filter(
                offers_models.Product.idAtProviders == "3700187679324",
                offers_models.Product.lastProvider == titelive_epagine_provider,
            )
            .one()
        )
        assert shared_gtl_product is not None
        assert shared_gtl_product.name == "Les dernières volontés de Mozart (symphony)"
        assert (
            shared_gtl_product.description
            == 'GIMS revient avec " Les dernières volontés de Mozart ", un album de tubes.'
        )
        assert shared_gtl_product.subcategoryId == subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id
        assert shared_gtl_product.ean == "3700187679324"
        assert shared_gtl_product.extraData["artist"] == "Gims"
        assert shared_gtl_product.extraData["author"] == "Gims"
        assert shared_gtl_product.extraData["contenu_explicite"] == "0"
        assert shared_gtl_product.extraData["date_parution"] == "2022-12-02"
        assert shared_gtl_product.extraData["dispo"] == "1"
        assert shared_gtl_product.extraData["distributeur"] == "Believe"
        assert shared_gtl_product.extraData["editeur"] == "BELIEVE"
        assert shared_gtl_product.extraData["music_label"] == "PLAY TWO"
        assert shared_gtl_product.extraData["nb_galettes"] == "1"
        assert shared_gtl_product.extraData["performer"] == "Gims"
        assert shared_gtl_product.extraData["prix_musique"] == "14.99"
        assert shared_gtl_product.extraData["musicType"] == str(
            music.MUSIC_TYPES_BY_SLUG["HIP_HOP_RAP-RAP_FRANCAIS"].code
        )
        assert shared_gtl_product.extraData["musicSubType"] == str(
            music.MUSIC_SUB_TYPES_BY_SLUG["HIP_HOP_RAP-RAP_FRANCAIS"].code
        )

        vinyle_product = (
            db.session.query(offers_models.Product)
            .filter(
                offers_models.Product.idAtProviders == "5054197199738",
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
        assert vinyle_product.extraData["dispo"] == "1"
        assert vinyle_product.extraData["distributeur"] == "Warner Music France"
        assert vinyle_product.extraData["editeur"] == "WARNER MUSIC UK"
        assert vinyle_product.extraData["music_label"] == "WARNER MUSIC UK"
        assert vinyle_product.extraData["nb_galettes"] == "1"
        assert vinyle_product.extraData["performer"] == "Gorillaz"
        assert vinyle_product.extraData["musicType"] == str(music.MUSIC_TYPES_BY_SLUG["POP-BRITPOP"].code)
        assert vinyle_product.extraData["musicSubType"] == str(music.MUSIC_SUB_TYPES_BY_SLUG["POP-BRITPOP"].code)
        assert "prix_musique" not in vinyle_product.extraData

    @time_machine.travel("2023-01-01", tick=False)
    def test_titelive_sync_event(self, requests_mock, settings):
        _configure_login_and_images(requests_mock, settings)
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/search", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE)
        titelive_epagine_provider = providers_repository.get_provider_by_name(
            providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME
        )
        sync_datetime = datetime.datetime(2022, 5, 5)
        providers_factories.LocalProviderEventFactory(
            provider=titelive_epagine_provider,
            type=providers_models.LocalProviderEventType.SyncEnd,
            date=sync_datetime,
            payload=titelive.TiteliveBase.MUSIC.value,
        )

        TiteliveMusicSearch().synchronize_products(to_date=sync_datetime.date())

        assert requests_mock.request_history[-2].qs["dateminm"] == ["04/05/2022"]
        assert requests_mock.request_history[-1].qs["dateminm"] == ["05/05/2022"]

        stop_event, start_event = (
            db.session.query(providers_models.LocalProviderEvent)
            .order_by(providers_models.LocalProviderEvent.id.desc())
            .limit(2)
        )
        assert stop_event.provider == start_event.provider == titelive_epagine_provider
        assert stop_event.date == start_event.date == datetime.datetime(2023, 1, 1)
        assert stop_event.payload == start_event.payload == titelive.TiteliveBase.MUSIC.value
        assert stop_event.type == providers_models.LocalProviderEventType.SyncEnd
        assert start_event.type == providers_models.LocalProviderEventType.SyncStart

    def test_titelive_sync_failure_event(self, requests_mock, settings):
        _configure_login_and_images(requests_mock, settings)
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/search", exc=requests.exceptions.RequestException)
        titelive_epagine_provider = providers_repository.get_provider_by_name(
            providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME
        )
        providers_factories.LocalProviderEventFactory(
            provider=titelive_epagine_provider,
            type=providers_models.LocalProviderEventType.SyncEnd,
            payload=titelive.TiteliveBase.MUSIC.value,
        )

        with pytest.raises(requests.ExternalAPIException):
            TiteliveMusicSearch().synchronize_products()

        start_sync_events_query = db.session.query(providers_models.LocalProviderEvent).filter(
            providers_models.LocalProviderEvent.provider == titelive_epagine_provider,
            providers_models.LocalProviderEvent.type == providers_models.LocalProviderEventType.SyncStart,
            providers_models.LocalProviderEvent.payload == titelive.TiteliveBase.MUSIC.value,
        )
        assert start_sync_events_query.count() == 1

        end_sync_events_query = db.session.query(providers_models.LocalProviderEvent).filter(
            providers_models.LocalProviderEvent.provider == titelive_epagine_provider,
            providers_models.LocalProviderEvent.type == providers_models.LocalProviderEventType.SyncEnd,
            providers_models.LocalProviderEvent.payload == titelive.TiteliveBase.MUSIC.value,
        )
        assert end_sync_events_query.count() == 1  # no new end sync event

        error_sync_events_query = db.session.query(providers_models.LocalProviderEvent).filter(
            providers_models.LocalProviderEvent.provider == titelive_epagine_provider,
            providers_models.LocalProviderEvent.type == providers_models.LocalProviderEventType.SyncError,
        )
        assert error_sync_events_query.count() == 1

    def test_sync_skips_products_already_synced_by_other_provider(self, requests_mock, settings):
        _configure_login_and_images(requests_mock, settings)
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=1", json=fixtures.MUSIC_SEARCH_FIXTURE)
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=2", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE
        )
        other_provider = providers_factories.ProviderFactory()
        offers_factories.ProductFactory(ean="3700187679323", lastProvider=other_provider)

        sync_date = datetime.date(2022, 12, 1)
        TiteliveMusicSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        products_with_same_ean_query = db.session.query(offers_models.Product).filter(
            offers_models.Product.ean == "3700187679323"
        )
        assert products_with_same_ean_query.count() == 1

        titelive_epagine_provider = providers_repository.get_provider_by_name(
            providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME
        )
        titelive_synced_products_query = db.session.query(offers_models.Product).filter(
            offers_models.Product.lastProvider == titelive_epagine_provider
        )
        assert titelive_synced_products_query.count() == 2

    def test_sync_thumbnails(self, requests_mock, settings):
        _configure_login_and_images(requests_mock, settings)
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=1", json=fixtures.MUSIC_SEARCH_FIXTURE)
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=2", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE
        )

        sync_date = datetime.date(2022, 12, 1)
        TiteliveMusicSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        synced_products = db.session.query(offers_models.Product).all()
        assert len(synced_products) == 3
        assert all(
            db.session.query(offers_models.ProductMediation)
            .filter(offers_models.ProductMediation.productId == synced_product.id)
            .count()
            > 0
            for synced_product in synced_products
        )

    def test_sync_thumbnails_deletes_old_mediations(self, requests_mock, settings):
        _configure_login_and_images(requests_mock, settings)
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=1", json=fixtures.MUSIC_SEARCH_FIXTURE)
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=2", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE
        )

        sync_date = datetime.date(2022, 12, 1)
        TiteliveMusicSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        synced_products = db.session.query(offers_models.Product).all()
        assert len(synced_products) == 3
        old_mediations = db.session.query(offers_models.ProductMediation).all()
        assert len(old_mediations) == 6

        TiteliveMusicSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        new_mediations = db.session.query(offers_models.ProductMediation).all()
        assert len(new_mediations) == 6
        assert all(old_mediation not in new_mediations for old_mediation in old_mediations)
        assert all(mediation.uuid is not None for mediation in new_mediations)

    def test_sync_thumbnails_network_failure_is_silent(self, requests_mock, settings):
        _configure_login_and_images(requests_mock, settings)
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=1", json=fixtures.MUSIC_SEARCH_FIXTURE)
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=2", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE
        )
        requests_mock.get("https://images.epagine.fr/323/3700187679324.jpg", exc=requests.exceptions.RequestException)
        requests_mock.get("https://images.epagine.fr/738/5054197199738_2.jpg", exc=requests.exceptions.RequestException)

        sync_date = datetime.date(2022, 12, 1)
        TiteliveMusicSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        synced_products = db.session.query(offers_models.Product).all()
        assert len(synced_products) == 3
        assert db.session.query(offers_models.ProductMediation).count() == 2

        no_thumbnail_product_1 = next(
            (product for product in synced_products if product.idAtProviders == "3700187679324"), None
        )

        assert no_thumbnail_product_1 is not None
        assert (
            db.session.query(offers_models.ProductMediation)
            .filter(offers_models.ProductMediation.productId == no_thumbnail_product_1.id)
            .count()
            == 0
        )
        no_thumbnail_product_2 = next(
            (product for product in synced_products if product.idAtProviders == "5054197199738"), None
        )
        assert no_thumbnail_product_2 is not None
        assert (
            db.session.query(offers_models.ProductMediation)
            .filter(offers_models.ProductMediation.productId == no_thumbnail_product_2.id)
            .count()
            == 0
        )

    def test_sync_thumbnails_open_failure_is_silent(self, requests_mock, settings):
        _configure_login_and_images(requests_mock, settings)
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=1", json=fixtures.MUSIC_SEARCH_FIXTURE)
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=2", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE
        )
        requests_mock.get("https://images.epagine.fr/323/3700187679324.jpg", body=b"")

        sync_date = datetime.date(2022, 12, 1)
        TiteliveMusicSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        synced_products = db.session.query(offers_models.Product).all()
        assert len(synced_products) == 3
        assert db.session.query(offers_models.ProductMediation).count() == 4
        no_thumbnail_product = next(
            (product for product in synced_products if product.idAtProviders == "3700187679324"), None
        )
        assert no_thumbnail_product is not None
        assert (
            db.session.query(offers_models.ProductMediation)
            .filter(offers_models.ProductMediation.productId == no_thumbnail_product.id)
            .count()
            == 0
        )

    def test_sync_thumbnails_truncated_failure_is_silent(self, requests_mock, settings):
        _configure_login_and_images(requests_mock, settings)
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=1", json=fixtures.MUSIC_SEARCH_FIXTURE)
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=2", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE
        )
        requests_mock.get("https://images.epagine.fr/323/3700187679324.jpg", exc=OSError)

        sync_date = datetime.date(2022, 12, 1)
        TiteliveMusicSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        synced_products = db.session.query(offers_models.Product).all()
        assert len(synced_products) == 3
        assert db.session.query(offers_models.ProductMediation).count() == 4
        no_thumbnail_product = next(
            (product for product in synced_products if product.idAtProviders == "3700187679324"), None
        )
        assert no_thumbnail_product is not None
        assert (
            db.session.query(offers_models.ProductMediation)
            .filter(offers_models.ProductMediation.productId == no_thumbnail_product.id)
            .count()
            == 0
        )

    def test_sync_skips_unallowed_format(self, requests_mock, settings):
        _configure_login_and_images(requests_mock, settings)
        not_fully_allowed_response = copy.deepcopy(fixtures.MUSIC_SEARCH_FIXTURE)
        not_fully_allowed_response["result"][-1]["article"]["1"]["codesupport"] = 35
        del not_fully_allowed_response["result"][0]["article"]["2"]["codesupport"]
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=1", json=not_fully_allowed_response)
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=2",
            json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE,
        )

        sync_date = datetime.date(2022, 12, 1)
        TiteliveMusicSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        synced_product = db.session.query(offers_models.Product).one()
        assert synced_product.idAtProviders == "3700187679323"

    def test_titelive_music_sync_from_page(self, requests_mock, settings):
        _configure_login_and_images(requests_mock, settings)
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=1", json=fixtures.MUSIC_SEARCH_FIXTURE)
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=2", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE
        )

        sync_date = datetime.date(2022, 12, 1)
        TiteliveMusicSearch().synchronize_products(from_date=sync_date, to_date=sync_date, from_page=2)

        assert db.session.query(offers_models.Product).count() == 0

    def test_titelive_music_sync_on_multiple_days(self, requests_mock, settings):
        _configure_login_and_images(requests_mock, settings)
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/search?datemaxm=01/12/2022", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE
        )
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=1&datemaxm=02/12/2022",
            json=fixtures.MUSIC_SEARCH_FIXTURE,
        )
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=2&datemaxm=02/12/2022",
            json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE,
        )

        TiteliveMusicSearch().synchronize_products(
            from_date=datetime.date(2022, 11, 30), to_date=datetime.date(2022, 12, 1)
        )

        assert db.session.query(offers_models.Product).count() == 3


@pytest.mark.settings(TITELIVE_EPAGINE_API_USERNAME="test@example.com", TITELIVE_EPAGINE_API_PASSWORD="qwerty123")
@pytest.mark.usefixtures("db_session")
class TiteliveBookSearchTest:
    EAN_TEST = "9782370730541"
    SCHOLAR_BOOK_GTL_ID = providers_constants.GTL_LEVEL_01_SCHOOL + "040300"
    EXTRACURRICULAR_GTL_ID = providers_constants.GTL_LEVEL_01_EXTRACURRICULAR + "080000"

    def setup_api_response_fixture(self, requests_mock, settings, fixture, eans=None):
        _configure_login_and_images(requests_mock, settings)
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=1", json=fixture)
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=2", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE
        )
        if eans is None:
            eans = []
            if "result" in fixture:
                eans = extract_eans_from_titelive_response(fixture["result"])
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/ean?in=ean={'|'.join(eans)}", json=fixture)

    def build_previously_synced_book_product(
        self, ean=None, name=None, extra_data=None, gcuCompatibilityType=offers_models.GcuCompatibilityType.COMPATIBLE
    ) -> offers_models.Product:
        titelive_provider = providers_repository.get_provider_by_name(
            providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME
        )
        if extra_data is None:
            extra_data = {}
        if ean is None:
            ean = self.EAN_TEST
            extra_data["ean"] = ean

        product = offers_factories.ProductFactory(
            ean=ean,
            idAtProviders=ean,
            gcuCompatibilityType=gcuCompatibilityType,
            lastProviderId=titelive_provider.id,
            name=name if name else "The Book",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )
        return product

    def test_create_1_thing(self, requests_mock, settings):
        self.setup_api_response_fixture(requests_mock, settings, fixtures.build_titelive_one_book_response())

        # When
        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        # Then
        product = db.session.query(offers_models.Product).one()

        assert product.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert product.ean == self.EAN_TEST
        assert product.extraData.get("bookFormat") == providers_constants.BookFormat.BEAUX_LIVRES.value
        assert product.ean == self.EAN_TEST

        assert product.extraData.get("gtl_id") == "03020300"
        closest_csr = {"label": "Bandes dessinées adultes / Comics", "csr_id": "1901"}
        assert product.extraData.get("csr_id") == closest_csr.get("csr_id")
        assert product.extraData.get("rayon") == closest_csr.get("label")
        assert product.extraData.get("code_clil") == "3774"

    def test_handle_bad_product_by_truncating_it(self, requests_mock, settings):
        TWO_BOOKS_RESPONSE_FIXTURE_WITH_LONG_TITLE = copy.deepcopy(fixtures.TWO_BOOKS_RESPONSE_FIXTURE)
        TWO_BOOKS_RESPONSE_FIXTURE_WITH_LONG_TITLE["result"][0]["titre"] = (
            "L'Arabe du futur Tome 2 : une jeunesse au Moyen-Orient (1984-1985) - Edition spéciale avec un titre très long pour tester la longueur de la description"
        )

        self.setup_api_response_fixture(requests_mock, settings, TWO_BOOKS_RESPONSE_FIXTURE_WITH_LONG_TITLE)

        # When
        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        # Then
        product = db.session.query(offers_models.Product).order_by(offers_models.Product.name).all()
        assert len(product) == 2
        assert (
            product[0].name
            == "L'Arabe du futur Tome 2 : une jeunesse au Moyen-Orient (1984-1985) - Edition spéciale avec un titre très long pour tester la longueur de la…"
        )
        assert product[1].name == "Mortelle Adèle Tome 1 : tout ça finira mal"

    def test_create_1_thing_when_gtl_not_has_lpad_zero(self, requests_mock, settings):
        self.setup_api_response_fixture(
            requests_mock, settings, fixtures.build_titelive_one_book_response(gtl_id="03020300", gtl_level=3)
        )

        # When
        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        # Then
        product = db.session.query(offers_models.Product).one()

        assert product.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert product.ean == self.EAN_TEST
        assert product.extraData.get("bookFormat") == providers_constants.BookFormat.BEAUX_LIVRES.value
        assert product.ean == self.EAN_TEST

        assert product.extraData.get("gtl_id") == "03020300"
        closest_csr = {"label": "Bandes dessinées adultes / Comics", "csr_id": "1901"}
        assert product.extraData.get("csr_id") == closest_csr.get("csr_id")
        assert product.extraData.get("rayon") == closest_csr.get("label")
        assert product.extraData.get("code_clil") == "3774"

    def test_create_1_thing_when_syncing_on_multiple_days(self, requests_mock, settings):
        _configure_login_and_images(requests_mock, settings)
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/search?datemaxm=01/12/2022", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE
        )
        fixture = fixtures.build_titelive_one_book_response()
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=1&datemaxm=02/12/2022", json=fixture)
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=2&datemaxm=02/12/2022",
            json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE,
        )
        eans = extract_eans_from_titelive_response(fixture["result"])
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/ean?in=ean={'|'.join(eans)}", json=fixture)

        TiteliveBookSearch().synchronize_products(
            from_date=datetime.date(2022, 11, 30), to_date=datetime.date(2022, 12, 1)
        )

        assert db.session.query(offers_models.Product).one()

    def test_does_not_create_product_when_product_is_gtl_school_book(self, requests_mock, settings):
        # Given
        self.setup_api_response_fixture(
            requests_mock,
            settings,
            fixtures.build_titelive_one_book_response(gtl_id=self.SCHOLAR_BOOK_GTL_ID, gtl_level=3),
        )

        # When
        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        # Then
        assert db.session.query(offers_models.Product).count() == 0

    @pytest.mark.parametrize("taux_tva", ["20", "20.00"])
    def test_does_not_create_product_when_product_is_vat_20(self, requests_mock, settings, taux_tva):
        # Given
        self.setup_api_response_fixture(
            requests_mock,
            settings,
            fixtures.build_titelive_one_book_response(taux_tva=taux_tva, code_tva="4"),  # TODO: find real values
        )

        # When
        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        # Then
        assert db.session.query(offers_models.Product).count() == 0

    def test_does_not_create_product_when_product_is_extracurricular(self, requests_mock, settings):
        self.setup_api_response_fixture(
            requests_mock,
            settings,
            fixtures.build_titelive_one_book_response(gtl_id=self.EXTRACURRICULAR_GTL_ID, gtl_level=2),
        )

        # When
        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        # Then
        assert db.session.query(offers_models.Product).count() == 0

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
        self, requests_mock, settings, support_code
    ):
        # Given
        self.setup_api_response_fixture(
            requests_mock, settings, fixtures.build_titelive_one_book_response(support_code=support_code)
        )

        # When
        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        # Then
        assert db.session.query(offers_models.Product).count() == 0

    def test_create_product_when_product_is_gtl_school_book_but_in_product_whitelist(self, requests_mock, settings):
        # Given
        whitelisted_ean = self.EAN_TEST
        self.setup_api_response_fixture(
            requests_mock,
            settings,
            fixtures.build_titelive_one_book_response(
                ean=whitelisted_ean, gtl_id=self.SCHOLAR_BOOK_GTL_ID, gtl_level=3
            ),
        )

        ProductWhitelistFactory(ean=whitelisted_ean)

        # When
        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        # Then
        # the assertion on the content is made in the previous tests
        assert db.session.query(offers_models.Product).count() == 1

    def test_does_not_create_product_when_product_is_lectorat_eighteen(self, requests_mock, settings):
        # Given
        self.setup_api_response_fixture(
            requests_mock,
            settings,
            fixtures.build_titelive_one_book_response(id_lectorat=providers_constants.LECTORAT_EIGHTEEN_ID),
        )

        # When
        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        # Then
        assert db.session.query(offers_models.Product).count() == 0

    @pytest.mark.parametrize(
        "level_02_code_gtl",
        [
            providers_constants.GTL_LEVEL_02_BEFORE_3,
            providers_constants.GTL_LEVEL_02_AFTER_3_AND_BEFORE_6,
        ],
    )
    def test_does_not_create_product_when_product_is_small_young(self, requests_mock, settings, level_02_code_gtl):
        # Given
        young_gtl_id = providers_constants.GTL_LEVEL_01_YOUNG + level_02_code_gtl + "0000"
        self.setup_api_response_fixture(
            requests_mock, settings, fixtures.build_titelive_one_book_response(gtl_id=young_gtl_id, gtl_level=2)
        )

        # When
        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        # Then
        assert db.session.query(offers_models.Product).count() == 0

    @pytest.mark.parametrize(
        "title",
        [
            "bryan pass toeic",
            "toefl yes we can",
        ],
    )
    def test_does_not_create_product_when_product_is_toeic_or_toefl(self, requests_mock, settings, title):
        # Given
        self.setup_api_response_fixture(requests_mock, settings, fixtures.build_titelive_one_book_response(title=title))

        # When
        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        # Then
        assert db.session.query(offers_models.Product).count() == 0

    def test_should_not_create_product_when_product_is_paper_press(self, requests_mock, settings):
        # When
        # One book press with tva
        edited_fixture = copy.deepcopy(fixtures.TWO_BOOKS_RESPONSE_FIXTURE)

        non_synced_ean = "9999999999999"
        edited_fixture["result"][0]["article"]["1"]["codesupport"] = "R"
        edited_fixture["result"][0]["article"]["1"]["taux_tva"] = "2.10"
        edited_fixture["result"][0]["article"]["1"]["code_tva"] = "1"
        edited_fixture["result"][1]["article"]["1"]["gencod"] = non_synced_ean

        # One book not press with tva
        edited_fixture["result"][1]["article"]["1"]["taux_tva"] = "2.10"
        edited_fixture["result"][1]["article"]["1"]["code_tva"] = "1"
        edited_fixture["result"][1]["article"]["1"]["gencod"] = self.EAN_TEST
        self.setup_api_response_fixture(requests_mock, settings, edited_fixture)

        # When
        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        # Then
        product = db.session.query(offers_models.Product).one()
        assert product.ean == self.EAN_TEST
        assert product.ean == self.EAN_TEST

    # UPDATE
    def test_update_1_thing(self, requests_mock, settings):
        # Given
        self.build_previously_synced_book_product()
        fixture_data = fixtures.build_titelive_one_book_response(ean=self.EAN_TEST)
        self.setup_api_response_fixture(requests_mock, settings, fixture_data)

        # When
        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        # Then
        product = db.session.query(offers_models.Product).one()
        assert product.ean == self.EAN_TEST
        assert product.ean == self.EAN_TEST
        assert product.name == fixture_data["result"][0]["titre"]

    def test_should_reject_product_when_gtl_changes_to_school_related_product(self, requests_mock, settings):
        # Given
        product = self.build_previously_synced_book_product()
        self.setup_api_response_fixture(
            requests_mock,
            settings,
            fixtures.build_titelive_one_book_response(ean=self.EAN_TEST, gtl_id=self.SCHOLAR_BOOK_GTL_ID, gtl_level=3),
        )

        offer = offers_factories.OfferFactory(product=product)
        FavoriteFactory(offer=offer)
        assert offer.validation != offers_models.OfferValidationStatus.REJECTED

        # When
        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        # Then
        product = db.session.query(offers_models.Product).one()
        offer = db.session.query(offers_models.Offer).one()
        assert product.gcuCompatibilityType == offers_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE
        assert db.session.query(Favorite).count() == 0
        assert offer.validation == offers_models.OfferValidationStatus.REJECTED
        assert offer.lastValidationType == OfferValidationType.CGU_INCOMPATIBLE_PRODUCT

    def test_should_reject_product_when_gtl_changes_to_extracurricular_related_product(self, requests_mock, settings):
        # Given
        self.setup_api_response_fixture(
            requests_mock,
            settings,
            fixtures.build_titelive_one_book_response(
                ean=self.EAN_TEST, gtl_id=self.EXTRACURRICULAR_GTL_ID, gtl_level=2
            ),
        )

        product = self.build_previously_synced_book_product()
        offer = offers_factories.OfferFactory(product=product)
        FavoriteFactory(offer=offer)
        assert offer.validation != offers_models.OfferValidationStatus.REJECTED

        # When
        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        # Then
        product = db.session.query(offers_models.Product).one()
        offer = db.session.query(offers_models.Offer).one()
        assert product.gcuCompatibilityType == offers_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE
        assert db.session.query(Favorite).count() == 0
        assert offer.validation == offers_models.OfferValidationStatus.REJECTED
        assert offer.lastValidationType == OfferValidationType.CGU_INCOMPATIBLE_PRODUCT

    def test_should_reject_product_when_non_valid_product_type(self, requests_mock, settings):
        product = self.build_previously_synced_book_product()
        self.setup_api_response_fixture(
            requests_mock,
            settings,
            fixtures.build_titelive_one_book_response(
                ean=self.EAN_TEST, gtl_id="04050505", gtl_level=4, title="jeux de société", support_code="O"
            ),
        )

        # When
        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        # Then
        product = db.session.query(offers_models.Product).one()
        assert product.gcuCompatibilityType == offers_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE

    def test_should_reject_product_when_it_changes_to_paper_press_product(self, requests_mock, settings):
        product = self.build_previously_synced_book_product()
        self.setup_api_response_fixture(
            requests_mock,
            settings,
            fixtures.build_titelive_one_book_response(
                ean=self.EAN_TEST, support_code="R", taux_tva="2.10", code_tva="1"
            ),
        )

        # When
        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        # Then
        product = db.session.query(offers_models.Product).one()
        assert product.gcuCompatibilityType == offers_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE

    def test_should_not_reject_product_and_deactivate_associated_offer_when_it_changes_to_paper_press_product(
        self, requests_mock, settings
    ):
        product = self.build_previously_synced_book_product()
        offerer = offerers_factories.OffererFactory(siren="123456789")
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = offers_factories.ThingOfferFactory(product=product, venue=venue)
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        BookingFactory(stock=stock)

        self.setup_api_response_fixture(
            requests_mock,
            settings,
            fixtures.build_titelive_one_book_response(ean=self.EAN_TEST, support_code="R", taux_tva="2.10"),
        )

        # When
        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        # Then
        offer = db.session.query(offers_models.Offer).one()
        assert offer.validation == offers_models.OfferValidationStatus.REJECTED
        assert stock.bookings[0].status == BookingStatus.CANCELLED

        product = db.session.query(offers_models.Product).one()
        assert product.gcuCompatibilityType == offers_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE

    def test_update_should_not_override_fraud_incompatibility(self, requests_mock, settings):
        product = self.build_previously_synced_book_product(
            gcuCompatibilityType=offers_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE
        )
        self.setup_api_response_fixture(
            requests_mock,
            settings,
            fixtures.build_titelive_one_book_response(id_lectorat=providers_constants.LECTORAT_EIGHTEEN_ID),
        )

        # When
        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        # Then
        product = db.session.query(offers_models.Product).one()
        assert product.gcuCompatibilityType == offers_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE

    def test_update_offers_extra_data_from_thing(self, requests_mock, settings):
        product = self.build_previously_synced_book_product()
        self.setup_api_response_fixture(requests_mock, settings, fixtures.build_titelive_one_book_response())

        # When
        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        # Then
        product = db.session.query(offers_models.Product).one()

        assert product.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert product.extraData.get("bookFormat") == providers_constants.BookFormat.BEAUX_LIVRES.value
        assert product.ean == self.EAN_TEST
        assert product.ean == self.EAN_TEST

        assert product.extraData.get("gtl_id") == "03020300"
        closest_csr = {"label": "Bandes dessinées adultes / Comics", "csr_id": "1901"}
        assert product.extraData.get("csr_id") == closest_csr.get("csr_id")
        assert product.extraData.get("rayon") == closest_csr.get("label")
        assert product.extraData.get("code_clil") == "3774"

    # APPROVAL
    def test_approve_product_from_inappropriate_thing(self, requests_mock, settings):
        product = self.build_previously_synced_book_product(
            gcuCompatibilityType=offers_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE
        )
        self.setup_api_response_fixture(
            requests_mock,
            settings,
            fixtures.build_titelive_one_book_response(ean=self.EAN_TEST),
        )

        # When
        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        # Then
        product = db.session.query(offers_models.Product).one()
        assert product.isGcuCompatible

    def test_approve_product_and_offers_from_inappropriate_thing(self, requests_mock, settings):
        product = self.build_previously_synced_book_product(
            gcuCompatibilityType=offers_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE
        )
        offers_factories.ThingOfferFactory(
            product=product,
            validation=OfferValidationStatus.REJECTED,
            lastValidationType=OfferValidationType.CGU_INCOMPATIBLE_PRODUCT,
        )

        self.setup_api_response_fixture(
            requests_mock,
            settings,
            fixtures.build_titelive_one_book_response(ean=self.EAN_TEST),
        )

        # When
        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        # Then
        product = db.session.query(offers_models.Product).one()
        assert product.isGcuCompatible

        offers = db.session.query(offers_models.Offer).all()
        assert all(offer.validation == OfferValidationStatus.APPROVED for offer in offers)

    @pytest.mark.parametrize(
        "auteurs_multi,expected_author",
        [
            (["John Mc Crae"], "John Mc Crae"),
            (["John Mc Crae", "John Doe"], "John Mc Crae, John Doe"),
            ("John Smith", "John Smith"),
            ("John Mc Crae, John Doe", "John Mc Crae, John Doe"),
            ({"auteur": "John Mc Crae"}, "John Mc Crae"),
            ({"auteur": "John Mc Crae", "auteur2": "Eraticerrata"}, "John Mc Crae, Eraticerrata"),
            (1234, None),  # invalid type
        ],
    )
    def test_handles_all_authors_formats(self, requests_mock, settings, auteurs_multi, expected_author):
        # Given
        self.setup_api_response_fixture(
            requests_mock, settings, fixtures.build_titelive_one_book_response(auteurs_multi=auteurs_multi)
        )

        # When
        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        # Then
        product = db.session.query(offers_models.Product).one()
        assert product.extraData.get("author") == expected_author

    def test_approval_should_not_override_fraud_incompatibility(self, requests_mock, settings):
        product = self.build_previously_synced_book_product(
            gcuCompatibilityType=offers_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE
        )
        self.setup_api_response_fixture(
            requests_mock,
            settings,
            fixtures.build_titelive_one_book_response(ean=self.EAN_TEST),
        )

        # When
        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        # Then
        product = db.session.query(offers_models.Product).one()
        assert product.gcuCompatibilityType == offers_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE

    def test_get_information_from_titelive_multiple_ean_route(self, requests_mock, settings):
        self.setup_api_response_fixture(
            requests_mock, settings, fixtures.BOOKS_BY_MULTIPLE_EANS_FIXTURE, eans=["1", "2"]
        )

        products = TiteliveBookSearch().get_product_info_from_eans(eans=["1", "2"])

        assert products[0].article[0].gencod == "9782070726370"
        assert products[1].article[0].gencod == "9782335010046"
        assert len(products) == 2

    def test_get_information_from_titelive_multiple_ean_route_with_dict_response(self, requests_mock, settings):
        dict_result_response = copy.deepcopy(fixtures.BOOKS_BY_MULTIPLE_EANS_FIXTURE)
        dict_result_response["result"] = {str(i): result for i, result in enumerate(dict_result_response["result"])}
        self.setup_api_response_fixture(requests_mock, settings, dict_result_response, eans=["1", "2"])

        products = TiteliveBookSearch().get_product_info_from_eans(eans=["1", "2"])

        assert products[0].article[0].gencod == "9782070726370"
        assert products[1].article[0].gencod == "9782335010046"
        assert len(products) == 2

    def test_get_information_from_titelive_single_ean_route(self, requests_mock, settings):
        self.setup_api_response_fixture(requests_mock, settings, fixtures.BOOK_BY_SINGLE_EAN_FIXTURE, eans=["1"])

        products = TiteliveBookSearch().get_product_info_from_eans(eans=["1"])
        assert products[0].article[0].gencod == "9782070455379"
        assert len(products) == 1

    def test_sync_skips_unparsable_work(self, requests_mock, settings):
        not_fully_parsable_response = copy.deepcopy(fixtures.BOOKS_BY_MULTIPLE_EANS_FIXTURE)
        del not_fully_parsable_response["result"][0]["titre"]

        self.setup_api_response_fixture(requests_mock, settings, not_fully_parsable_response, eans=["1", "2"])

        products = TiteliveBookSearch().get_product_info_from_eans(eans=["1", "2"])
        assert products[0].article[0].gencod == "9782335010046"
        assert len(products) == 1

    def test_extract_eans_from_titelive_response(self):
        eans = extract_eans_from_titelive_response(fixtures.TWO_BOOKS_RESPONSE_FIXTURE["result"])
        assert eans == {"9782370730541", "9782848018676"}

    def test_ignores_verso_image_if_it_is_a_placeholder(self, requests_mock, settings):
        # Sometimes, titelive will link a placeholder image to the verso image
        # This image should be ignored
        self.setup_api_response_fixture(requests_mock, settings, fixtures.TWO_BOOKS_RESPONSE_FIXTURE)

        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        products = db.session.query(offers_models.Product).all()
        ean_no_verso_image = "9782848018676"
        ean_verso_image = "9782370730541"

        assert len(products) == 2

        product_by_ean = {product.ean: product for product in products}

        product_without_verso_image = product_by_ean.get(ean_no_verso_image)
        product_with_verso_image = product_by_ean.get(ean_verso_image)

        assert product_without_verso_image is not None
        assert product_without_verso_image.images.get(offers_models.ImageType.VERSO.value) is None

        assert product_with_verso_image is not None
        assert product_with_verso_image.images.get(offers_models.ImageType.VERSO.value) is not None

    def test_does_serialize_if_no_image(self, requests_mock, settings):
        self.setup_api_response_fixture(requests_mock, settings, fixtures.NO_IMAGE_IN_RESULT_FIXTURE)

        sync_date = datetime.date(2022, 12, 1)
        TiteliveBookSearch().synchronize_products(from_date=sync_date, to_date=sync_date)

        (product,) = db.session.query(offers_models.Product).all()

        assert product.images.get("recto") is None
