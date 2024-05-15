import copy
import datetime
import pathlib
import re

import pytest
import time_machine

from pcapi import settings
from pcapi.connectors import titelive
from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.fraud.factories import ProductWhitelistFactory
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
import pcapi.core.providers.constants as providers_constants
import pcapi.core.providers.factories as providers_factories
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
from pcapi.core.providers.titelive_book_search import TiteliveBookSearch
from pcapi.core.providers.titelive_music_search import TiteliveMusicSearch
from pcapi.core.testing import override_settings
from pcapi.core.users.factories import FavoriteFactory
from pcapi.core.users.models import Favorite
from pcapi.domain import music_types
from pcapi.local_providers.titelive_things import titelive_things as ttl_constants
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.utils import requests

import tests
from tests.connectors.titelive import fixtures


def _configure_login_and_images(requests_mock):
    requests_mock.post(
        f"{settings.TITELIVE_EPAGINE_API_AUTH_URL}/login/test@example.com/token",
        json={"token": "XYZ"},
    )
    image_path = pathlib.Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
    with open(image_path, "rb") as thumb_file:
        requests_mock.get(re.compile("image"), content=thumb_file.read())


@override_settings(TITELIVE_EPAGINE_API_USERNAME="test@example.com")
@override_settings(TITELIVE_EPAGINE_API_PASSWORD="qwerty123")
@pytest.mark.usefixtures("db_session")
class TiteliveSearchTest:
    def test_titelive_music_sync(self, requests_mock):
        _configure_login_and_images(requests_mock)
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=1", json=fixtures.MUSIC_SEARCH_FIXTURE)
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=2", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE
        )
        titelive_epagine_provider = providers_repository.get_provider_by_name(
            providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME
        )
        offers_factories.ProductFactory(
            extraData={"ean": "3700187679323"}, idAtProviders="3700187679323", lastProvider=titelive_epagine_provider
        )

        TiteliveMusicSearch().synchronize_products(datetime.date(2022, 12, 1))

        cd_product = offers_models.Product.query.filter(
            offers_models.Product.idAtProviders == "3700187679323",
            offers_models.Product.lastProvider == titelive_epagine_provider,  # pylint: disable=comparison-with-callable
        ).one()
        assert cd_product is not None
        assert cd_product.name == "Les dernières volontés de Mozart (symphony)"
        assert cd_product.description == 'GIMS revient avec " Les dernières volontés de Mozart ", un album de tubes.'
        assert cd_product.subcategoryId == subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id
        assert cd_product.extraData["artist"] == "Gims"
        assert cd_product.extraData["author"] == "Gims"
        assert cd_product.extraData["contenu_explicite"] == "0"
        assert cd_product.extraData["date_parution"] == "2022-12-02"
        assert cd_product.extraData["dispo"] == "1"
        assert cd_product.extraData["distributeur"] == "Believe"
        assert cd_product.extraData["ean"] == "3700187679323"
        assert cd_product.extraData["editeur"] == "BELIEVE"
        assert cd_product.extraData["music_label"] == "PLAY TWO"
        assert cd_product.extraData["nb_galettes"] == "1"
        assert cd_product.extraData["performer"] == "Gims"
        assert cd_product.extraData["prix_musique"] == "14.99"
        assert cd_product.extraData["musicType"] == str(
            music_types.MUSIC_TYPES_BY_SLUG["HIP_HOP_RAP-RAP_FRANCAIS"].code
        )
        assert cd_product.extraData["musicSubType"] == str(
            music_types.MUSIC_SUB_TYPES_BY_SLUG["HIP_HOP_RAP-RAP_FRANCAIS"].code
        )

        shared_gtl_product = offers_models.Product.query.filter(
            offers_models.Product.idAtProviders == "3700187679324",
            offers_models.Product.lastProvider == titelive_epagine_provider,  # pylint: disable=comparison-with-callable
        ).one()
        assert shared_gtl_product is not None
        assert shared_gtl_product.name == "Les dernières volontés de Mozart (symphony)"
        assert (
            shared_gtl_product.description
            == 'GIMS revient avec " Les dernières volontés de Mozart ", un album de tubes.'
        )
        assert shared_gtl_product.subcategoryId == subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id
        assert shared_gtl_product.extraData["artist"] == "Gims"
        assert shared_gtl_product.extraData["author"] == "Gims"
        assert shared_gtl_product.extraData["contenu_explicite"] == "0"
        assert shared_gtl_product.extraData["date_parution"] == "2022-12-02"
        assert shared_gtl_product.extraData["dispo"] == "1"
        assert shared_gtl_product.extraData["distributeur"] == "Believe"
        assert shared_gtl_product.extraData["ean"] == "3700187679324"
        assert shared_gtl_product.extraData["editeur"] == "BELIEVE"
        assert shared_gtl_product.extraData["music_label"] == "PLAY TWO"
        assert shared_gtl_product.extraData["nb_galettes"] == "1"
        assert shared_gtl_product.extraData["performer"] == "Gims"
        assert shared_gtl_product.extraData["prix_musique"] == "14.99"
        assert shared_gtl_product.extraData["musicType"] == str(
            music_types.MUSIC_TYPES_BY_SLUG["HIP_HOP_RAP-RAP_FRANCAIS"].code
        )
        assert shared_gtl_product.extraData["musicSubType"] == str(
            music_types.MUSIC_SUB_TYPES_BY_SLUG["HIP_HOP_RAP-RAP_FRANCAIS"].code
        )

        vinyle_product = offers_models.Product.query.filter(
            offers_models.Product.idAtProviders == "5054197199738",
            offers_models.Product.lastProvider == titelive_epagine_provider,  # pylint: disable=comparison-with-callable
        ).one()
        assert vinyle_product.name is not None
        assert vinyle_product.name == "Cracker Island"
        assert (
            vinyle_product.description
            == "Ce huitième album studio de Gorillaz est une collection énergique, optimiste et riche en genres de 10 titres mettant en vedette un line-up stellaire de collaborateurs : Thundercat, Tame Impala, Bad Bunny, Stevie Nicks, Adeleye Omotayo, Bootie Brown et Beck."
        )
        assert vinyle_product.subcategoryId == subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id
        assert vinyle_product.extraData["artist"] == "Gorillaz"
        assert vinyle_product.extraData["author"] == "Gorillaz"
        assert vinyle_product.extraData["contenu_explicite"] == "0"
        assert vinyle_product.extraData["date_parution"] == "2023-02-24"
        assert vinyle_product.extraData["dispo"] == "1"
        assert vinyle_product.extraData["distributeur"] == "Warner Music France"
        assert vinyle_product.extraData["ean"] == "5054197199738"
        assert vinyle_product.extraData["editeur"] == "WARNER MUSIC UK"
        assert vinyle_product.extraData["music_label"] == "WARNER MUSIC UK"
        assert vinyle_product.extraData["nb_galettes"] == "1"
        assert vinyle_product.extraData["performer"] == "Gorillaz"
        assert vinyle_product.extraData["musicType"] == str(music_types.MUSIC_TYPES_BY_SLUG["POP-BRITPOP"].code)
        assert vinyle_product.extraData["musicSubType"] == str(music_types.MUSIC_SUB_TYPES_BY_SLUG["POP-BRITPOP"].code)
        assert "prix_musique" not in vinyle_product.extraData

    @time_machine.travel("2023-01-01", tick=False)
    def test_titelive_sync_event(self, requests_mock):
        _configure_login_and_images(requests_mock)
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/search", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE)
        titelive_epagine_provider = providers_repository.get_provider_by_name(
            providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME
        )
        providers_factories.LocalProviderEventFactory(
            provider=titelive_epagine_provider,
            type=providers_models.LocalProviderEventType.SyncEnd,
            date=datetime.datetime(2022, 5, 5),
            payload=titelive.TiteliveBase.MUSIC.value,
        )

        TiteliveMusicSearch().synchronize_products()

        assert requests_mock.last_request.qs["dateminm"] == ["05/05/2022"]

        stop_event, start_event = providers_models.LocalProviderEvent.query.order_by(
            providers_models.LocalProviderEvent.id.desc()
        ).limit(2)
        assert stop_event.provider == start_event.provider == titelive_epagine_provider
        assert stop_event.date == start_event.date == datetime.datetime(2023, 1, 1)
        assert stop_event.payload == start_event.payload == titelive.TiteliveBase.MUSIC.value
        assert stop_event.type == providers_models.LocalProviderEventType.SyncEnd
        assert start_event.type == providers_models.LocalProviderEventType.SyncStart

    def test_titelive_sync_failure_event(self, requests_mock):
        _configure_login_and_images(requests_mock)
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

        start_sync_events_query = providers_models.LocalProviderEvent.query.filter(
            providers_models.LocalProviderEvent.provider == titelive_epagine_provider,
            providers_models.LocalProviderEvent.type == providers_models.LocalProviderEventType.SyncStart,
            providers_models.LocalProviderEvent.payload == titelive.TiteliveBase.MUSIC.value,
        )
        assert start_sync_events_query.count() == 1

        end_sync_events_query = providers_models.LocalProviderEvent.query.filter(
            providers_models.LocalProviderEvent.provider == titelive_epagine_provider,
            providers_models.LocalProviderEvent.type == providers_models.LocalProviderEventType.SyncEnd,
            providers_models.LocalProviderEvent.payload == titelive.TiteliveBase.MUSIC.value,
        )
        assert end_sync_events_query.count() == 1  # no new end sync event

        error_sync_events_query = providers_models.LocalProviderEvent.query.filter(
            providers_models.LocalProviderEvent.provider == titelive_epagine_provider,
            providers_models.LocalProviderEvent.type == providers_models.LocalProviderEventType.SyncError,
        )
        assert error_sync_events_query.count() == 1

    def test_sync_skips_products_already_synced_by_other_provider(self, requests_mock):
        _configure_login_and_images(requests_mock)
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=1", json=fixtures.MUSIC_SEARCH_FIXTURE)
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=2", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE
        )
        other_provider = providers_factories.ProviderFactory()
        offers_factories.ProductFactory(extraData={"ean": "3700187679323"}, lastProvider=other_provider)

        TiteliveMusicSearch().synchronize_products(datetime.date(2022, 12, 1))

        products_with_same_ean_query = offers_models.Product.query.filter(
            offers_models.Product.extraData["ean"].astext == "3700187679323"
        )
        assert products_with_same_ean_query.count() == 1

        titelive_epagine_provider = providers_repository.get_provider_by_name(
            providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME
        )
        titelive_synced_products_query = offers_models.Product.query.filter(
            offers_models.Product.lastProvider == titelive_epagine_provider  # pylint: disable=comparison-with-callable
        )
        assert titelive_synced_products_query.count() == 2

    def test_sync_thumbnails(self, requests_mock):
        _configure_login_and_images(requests_mock)
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=1", json=fixtures.MUSIC_SEARCH_FIXTURE)
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=2", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE
        )

        TiteliveMusicSearch().synchronize_products(datetime.date(2022, 12, 1))

        synced_products = offers_models.Product.query.all()
        assert len(synced_products) == 3
        assert all(
            offers_models.ProductMediation.query.filter(
                offers_models.ProductMediation.productId == synced_product.id
            ).count()
            > 0
            for synced_product in synced_products
        )

    def test_sync_thumbnails_deletes_old_mediations(self, requests_mock):
        _configure_login_and_images(requests_mock)
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=1", json=fixtures.MUSIC_SEARCH_FIXTURE)
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=2", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE
        )

        TiteliveMusicSearch().synchronize_products(datetime.date(2022, 12, 1))

        synced_products = offers_models.Product.query.all()
        assert len(synced_products) == 3

        old_mediations = offers_models.ProductMediation.query.all()
        assert len(old_mediations) == 6
        TiteliveMusicSearch().synchronize_products(datetime.date(2022, 12, 1))
        new_mediations = offers_models.ProductMediation.query.all()
        assert len(new_mediations) == 6
        assert all(old_mediation not in new_mediations for old_mediation in old_mediations)

    def test_sync_thumbnails_network_failure_is_silent(self, requests_mock):
        _configure_login_and_images(requests_mock)
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=1", json=fixtures.MUSIC_SEARCH_FIXTURE)
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=2", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE
        )
        requests_mock.get("https://images.epagine.fr/323/3700187679324.jpg", exc=requests.exceptions.RequestException)
        requests_mock.get("https://images.epagine.fr/738/5054197199738_2.jpg", exc=requests.exceptions.RequestException)

        assert TiteliveMusicSearch().synchronize_products(datetime.date(2022, 12, 1)) is None

        synced_products = offers_models.Product.query.all()
        assert len(synced_products) == 3
        assert offers_models.ProductMediation.query.count() == 2

        no_thumbnail_product_1 = next(
            (product for product in synced_products if product.idAtProviders == "3700187679324"), None
        )

        assert no_thumbnail_product_1 is not None
        assert (
            offers_models.ProductMediation.query.filter(
                offers_models.ProductMediation.productId == no_thumbnail_product_1.id
            ).count()
            == 0
        )
        no_thumbnail_product_2 = next(
            (product for product in synced_products if product.idAtProviders == "5054197199738"), None
        )
        assert no_thumbnail_product_2 is not None
        assert (
            offers_models.ProductMediation.query.filter(
                offers_models.ProductMediation.productId == no_thumbnail_product_2.id
            ).count()
            == 0
        )

    def test_sync_thumbnails_open_failure_is_silent(self, requests_mock):
        _configure_login_and_images(requests_mock)
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=1", json=fixtures.MUSIC_SEARCH_FIXTURE)
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=2", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE
        )
        requests_mock.get("https://images.epagine.fr/323/3700187679324.jpg", body=b"")

        assert TiteliveMusicSearch().synchronize_products(datetime.date(2022, 12, 1)) is None

        synced_products = offers_models.Product.query.all()
        assert len(synced_products) == 3
        assert offers_models.ProductMediation.query.count() == 4
        no_thumbnail_product = next(
            (product for product in synced_products if product.idAtProviders == "3700187679324"), None
        )
        assert no_thumbnail_product is not None
        assert (
            offers_models.ProductMediation.query.filter(
                offers_models.ProductMediation.productId == no_thumbnail_product.id
            ).count()
            == 0
        )

    def test_sync_skips_unallowed_format(self, requests_mock):
        _configure_login_and_images(requests_mock)
        not_fully_allowed_response = copy.deepcopy(fixtures.MUSIC_SEARCH_FIXTURE)
        not_fully_allowed_response["result"][-1]["article"]["1"]["codesupport"] = 35
        del not_fully_allowed_response["result"][0]["article"]["2"]["codesupport"]
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=1", json=not_fully_allowed_response)
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=2",
            json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE,
        )

        TiteliveMusicSearch().synchronize_products(datetime.date(2022, 12, 1))

        synced_product = offers_models.Product.query.one()
        assert synced_product.idAtProviders == "3700187679323"

    def test_titelive_music_sync_from_page(self, requests_mock):
        _configure_login_and_images(requests_mock)
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=1", json=fixtures.MUSIC_SEARCH_FIXTURE)
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=2", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE
        )

        TiteliveMusicSearch().synchronize_products(datetime.date(2022, 12, 1), 2)

        assert offers_models.Product.query.count() == 0


@override_settings(TITELIVE_EPAGINE_API_USERNAME="test@example.com")
@override_settings(TITELIVE_EPAGINE_API_PASSWORD="qwerty123")
@pytest.mark.usefixtures("db_session")
class TiteliveBookSearchTest:
    EAN_TEST = "9782370730541"
    SCHOLAR_BOOK_GTL_ID = ttl_constants.GTL_LEVEL_01_SCHOOL + "040300"
    EXTRACURRICULAR_GTL_ID = ttl_constants.GTL_LEVEL_01_EXTRACURRICULAR + "080000"

    def setup_api_response_fixture(self, requests_mock, fixture):
        _configure_login_and_images(requests_mock)
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=1", json=fixture)
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/search?page=2", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE
        )

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
            extraData=extra_data,
            idAtProviders=ean,
            gcuCompatibilityType=gcuCompatibilityType,
            lastProviderId=titelive_provider.id,
            name=name if name else "The Book",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )
        return product

    def test_create_1_thing(self, requests_mock):
        self.setup_api_response_fixture(requests_mock, fixtures.build_titelive_one_book_response())

        # When
        TiteliveBookSearch().synchronize_products(datetime.date(2022, 12, 1), 1)

        # Then
        product = offers_models.Product.query.one()

        assert product.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert product.extraData.get("bookFormat") == providers_constants.BookFormat.BEAUX_LIVRES.value
        assert product.extraData.get("ean") == self.EAN_TEST

        assert product.extraData.get("gtl_id") == "03020300"
        closest_csr = {"label": "Bandes dessinées adultes / Comics", "csr_id": "1901"}
        assert product.extraData.get("csr_id") == closest_csr.get("csr_id")
        assert product.extraData.get("rayon") == closest_csr.get("label")
        assert product.extraData.get("code_clil") == "3774"

    def test_handle_bad_product_by_ignoring_it(self, requests_mock):
        self.setup_api_response_fixture(
            requests_mock, fixtures.build_titelive_one_book_response(title="Long title with more than 140 chars" * 10)
        )

        # When
        TiteliveBookSearch().synchronize_products(datetime.date(2022, 12, 1), 1)

        # Then
        assert offers_models.Product.query.count() == 0

    def test_handle_bad_product_by_skipping_it(self, requests_mock):
        TWO_BOOKS_RESPONSE_FIXTURE_WITH_LONG_TITLE = copy.deepcopy(fixtures.TWO_BOOKS_RESPONSE_FIXTURE)
        TWO_BOOKS_RESPONSE_FIXTURE_WITH_LONG_TITLE["result"][0][
            "titre"
        ] = "L'Arabe du futur Tome 2 : une jeunesse au Moyen-Orient (1984-1985) - Edition spéciale avec un titre très long pour tester la longueur de la description"

        self.setup_api_response_fixture(requests_mock, TWO_BOOKS_RESPONSE_FIXTURE_WITH_LONG_TITLE)

        # When
        TiteliveBookSearch().synchronize_products(datetime.date(2022, 12, 1), 1)

        # Then
        product = offers_models.Product.query.one()
        assert product.name == "Mortelle Adèle Tome 1 : tout ça finira mal"

    def test_create_1_thing_when_gtl_not_has_lpad_zero(self, requests_mock):
        self.setup_api_response_fixture(
            requests_mock, fixtures.build_titelive_one_book_response(gtl_id="03020300", gtl_level=3)
        )

        # When
        TiteliveBookSearch().synchronize_products(datetime.date(2022, 12, 1), 1)

        # Then
        product = offers_models.Product.query.one()

        assert product.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert product.extraData.get("bookFormat") == providers_constants.BookFormat.BEAUX_LIVRES.value
        assert product.extraData.get("ean") == self.EAN_TEST

        assert product.extraData.get("gtl_id") == "03020300"
        closest_csr = {"label": "Bandes dessinées adultes / Comics", "csr_id": "1901"}
        assert product.extraData.get("csr_id") == closest_csr.get("csr_id")
        assert product.extraData.get("rayon") == closest_csr.get("label")
        assert product.extraData.get("code_clil") == "3774"

    def test_does_not_create_product_when_product_is_gtl_school_book(self, requests_mock):
        # Given
        self.setup_api_response_fixture(
            requests_mock, fixtures.build_titelive_one_book_response(gtl_id=self.SCHOLAR_BOOK_GTL_ID, gtl_level=3)
        )

        # When
        TiteliveBookSearch().synchronize_products(datetime.date(2022, 12, 1), 1)

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.parametrize("taux_tva", ["20", "20.00"])
    def test_does_not_create_product_when_product_is_vat_20(self, requests_mock, taux_tva):
        # Given
        self.setup_api_response_fixture(
            requests_mock,
            fixtures.build_titelive_one_book_response(taux_tva=taux_tva, code_tva="4"),  # TODO: find real values
        )

        # When
        TiteliveBookSearch().synchronize_products(datetime.date(2022, 12, 1), 1)

        # Then
        assert offers_models.Product.query.count() == 0

    def test_does_not_create_product_when_product_is_extracurricular(self, requests_mock):
        self.setup_api_response_fixture(
            requests_mock, fixtures.build_titelive_one_book_response(gtl_id=self.EXTRACURRICULAR_GTL_ID, gtl_level=2)
        )

        # When
        TiteliveBookSearch().synchronize_products(datetime.date(2022, 12, 1), 1)

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.parametrize(
        "support_code",
        [
            ttl_constants.CALENDAR_SUPPORT_CODE,
            ttl_constants.POSTER_SUPPORT_CODE,
            ttl_constants.PAPER_CONSUMABLE_SUPPORT_CODE,
            ttl_constants.BOX_SUPPORT_CODE,
            ttl_constants.OBJECT_SUPPORT_CODE,
        ],
    )
    def test_does_not_create_product_when_product_is_non_eligible_support_code(self, requests_mock, support_code):
        # Given
        self.setup_api_response_fixture(
            requests_mock, fixtures.build_titelive_one_book_response(support_code=support_code)
        )

        # When
        TiteliveBookSearch().synchronize_products(datetime.date(2022, 12, 1), 1)

        # Then
        assert offers_models.Product.query.count() == 0

    def test_create_product_when_product_is_gtl_school_book_but_in_product_whitelist(self, requests_mock):
        # Given
        whitelisted_ean = self.EAN_TEST
        self.setup_api_response_fixture(
            requests_mock,
            fixtures.build_titelive_one_book_response(
                ean=whitelisted_ean, gtl_id=self.SCHOLAR_BOOK_GTL_ID, gtl_level=3
            ),
        )

        ProductWhitelistFactory(ean=whitelisted_ean)

        # When
        TiteliveBookSearch().synchronize_products(datetime.date(2022, 12, 1), 1)

        # Then
        # the assertion on the content is made in the previous tests
        assert offers_models.Product.query.count() == 1

    def test_does_not_create_product_when_product_is_lectorat_eighteen(self, requests_mock):
        # Given
        self.setup_api_response_fixture(
            requests_mock, fixtures.build_titelive_one_book_response(id_lectorat=ttl_constants.LECTORAT_EIGHTEEN_ID)
        )

        # When
        TiteliveBookSearch().synchronize_products(datetime.date(2022, 12, 1), 1)

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.parametrize(
        "level_02_code_gtl",
        [
            ttl_constants.GTL_LEVEL_02_BEFORE_3,
            ttl_constants.GTL_LEVEL_02_AFTER_3_AND_BEFORE_6,
        ],
    )
    def test_does_not_create_product_when_product_is_small_young(self, requests_mock, level_02_code_gtl):
        # Given
        young_gtl_id = ttl_constants.GTL_LEVEL_01_YOUNG + level_02_code_gtl + "0000"
        self.setup_api_response_fixture(
            requests_mock, fixtures.build_titelive_one_book_response(gtl_id=young_gtl_id, gtl_level=2)
        )

        # When
        TiteliveBookSearch().synchronize_products(datetime.date(2022, 12, 1), 1)

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.parametrize(
        "title",
        [
            "bryan pass toeic",
            "toefl yes we can",
        ],
    )
    def test_does_not_create_product_when_product_is_toeic_or_toefl(self, requests_mock, title):
        # Given
        self.setup_api_response_fixture(requests_mock, fixtures.build_titelive_one_book_response(title=title))

        # When
        TiteliveBookSearch().synchronize_products(datetime.date(2022, 12, 1), 1)

        # Then
        assert offers_models.Product.query.count() == 0

    def test_should_not_create_product_when_product_is_paper_press(self, requests_mock):
        # When
        # One book press with tva
        non_synced_ean = "9999999999999"
        fixtures.TWO_BOOKS_RESPONSE_FIXTURE["result"][0]["article"]["1"]["codesupport"] = "R"
        fixtures.TWO_BOOKS_RESPONSE_FIXTURE["result"][0]["article"]["1"]["taux_tva"] = "2.10"
        fixtures.TWO_BOOKS_RESPONSE_FIXTURE["result"][0]["article"]["1"]["code_tva"] = "1"
        fixtures.TWO_BOOKS_RESPONSE_FIXTURE["result"][1]["article"]["1"]["gencod"] = non_synced_ean

        # One book not press with tva
        fixtures.TWO_BOOKS_RESPONSE_FIXTURE["result"][1]["article"]["1"]["taux_tva"] = "2.10"
        fixtures.TWO_BOOKS_RESPONSE_FIXTURE["result"][1]["article"]["1"]["code_tva"] = "1"
        fixtures.TWO_BOOKS_RESPONSE_FIXTURE["result"][1]["article"]["1"]["gencod"] = self.EAN_TEST
        self.setup_api_response_fixture(requests_mock, fixtures.TWO_BOOKS_RESPONSE_FIXTURE)

        # When
        TiteliveBookSearch().synchronize_products(datetime.date(2022, 12, 1), 1)

        # Then
        product = offers_models.Product.query.one()
        assert product.extraData.get("ean") == self.EAN_TEST

    # UPDATE
    def test_update_1_thing(self, requests_mock):
        # Given
        self.build_previously_synced_book_product()
        fixture_data = fixtures.build_titelive_one_book_response(ean=self.EAN_TEST)
        self.setup_api_response_fixture(requests_mock, fixture_data)

        # When
        TiteliveBookSearch().synchronize_products(datetime.date(2022, 12, 1), 1)

        # Then
        product = offers_models.Product.query.one()
        assert product.extraData.get("ean") == self.EAN_TEST
        assert product.name == fixture_data["result"][0]["titre"]

    def test_should_reject_product_when_gtl_changes_to_school_related_product(self, requests_mock):
        # Given
        product = self.build_previously_synced_book_product()
        self.setup_api_response_fixture(
            requests_mock,
            fixtures.build_titelive_one_book_response(ean=self.EAN_TEST, gtl_id=self.SCHOLAR_BOOK_GTL_ID, gtl_level=3),
        )

        offer = offers_factories.OfferFactory(product=product)
        FavoriteFactory(offer=offer)
        assert offer.validation != offers_models.OfferValidationStatus.REJECTED

        # When
        TiteliveBookSearch().synchronize_products(datetime.date(2022, 12, 1), 1)

        # Then
        product = offers_models.Product.query.one()
        offer = offers_models.Offer.query.one()
        assert product.gcuCompatibilityType == offers_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE
        assert Favorite.query.count() == 0
        assert offer.validation == offers_models.OfferValidationStatus.REJECTED
        assert offer.lastValidationType == OfferValidationType.CGU_INCOMPATIBLE_PRODUCT

    def test_should_reject_product_when_gtl_changes_to_extracurricular_related_product(self, requests_mock):

        # Given
        self.setup_api_response_fixture(
            requests_mock,
            fixtures.build_titelive_one_book_response(
                ean=self.EAN_TEST, gtl_id=self.EXTRACURRICULAR_GTL_ID, gtl_level=2
            ),
        )

        product = self.build_previously_synced_book_product()
        offer = offers_factories.OfferFactory(product=product)
        FavoriteFactory(offer=offer)
        assert offer.validation != offers_models.OfferValidationStatus.REJECTED

        # When
        TiteliveBookSearch().synchronize_products(datetime.date(2022, 12, 1), 1)

        # Then
        product = offers_models.Product.query.one()
        offer = offers_models.Offer.query.one()
        assert product.gcuCompatibilityType == offers_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE
        assert Favorite.query.count() == 0
        assert offer.validation == offers_models.OfferValidationStatus.REJECTED
        assert offer.lastValidationType == OfferValidationType.CGU_INCOMPATIBLE_PRODUCT

    def test_should_reject_product_when_non_valid_product_type(self, requests_mock):
        product = self.build_previously_synced_book_product()
        self.setup_api_response_fixture(
            requests_mock,
            fixtures.build_titelive_one_book_response(
                ean=self.EAN_TEST, gtl_id="04050505", gtl_level=4, title="jeux de société", support_code="O"
            ),
        )

        # When
        TiteliveBookSearch().synchronize_products(datetime.date(2022, 12, 1), 1)

        # Then
        product = offers_models.Product.query.one()
        assert product.gcuCompatibilityType == offers_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE

    def test_should_reject_product_when_it_changes_to_paper_press_product(self, requests_mock):
        product = self.build_previously_synced_book_product()
        self.setup_api_response_fixture(
            requests_mock,
            fixtures.build_titelive_one_book_response(
                ean=self.EAN_TEST, support_code="R", taux_tva="2.10", code_tva="1"
            ),
        )

        # When
        TiteliveBookSearch().synchronize_products(datetime.date(2022, 12, 1), 1)

        # Then
        product = offers_models.Product.query.one()
        assert product.gcuCompatibilityType == offers_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE

    def test_should_not_reject_product_and_deactivate_associated_offer_when_it_changes_to_paper_press_product(
        self, requests_mock
    ):
        product = self.build_previously_synced_book_product()
        offerer = offerers_factories.OffererFactory(siren="123456789")
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = offers_factories.ThingOfferFactory(product=product, venue=venue)
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        BookingFactory(stock=stock)

        self.setup_api_response_fixture(
            requests_mock,
            fixtures.build_titelive_one_book_response(ean=self.EAN_TEST, support_code="R", taux_tva="2.10"),
        )

        # When
        TiteliveBookSearch().synchronize_products(datetime.date(2022, 12, 1), 1)

        # Then
        offer = offers_models.Offer.query.one()
        assert offer.validation == offers_models.OfferValidationStatus.REJECTED
        assert stock.bookings[0].status == BookingStatus.CANCELLED

        product = offers_models.Product.query.one()
        assert product.gcuCompatibilityType == offers_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE

    def test_update_should_not_override_fraud_incompatibility(self, requests_mock):
        product = self.build_previously_synced_book_product(
            gcuCompatibilityType=offers_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE
        )
        self.setup_api_response_fixture(
            requests_mock, fixtures.build_titelive_one_book_response(id_lectorat=ttl_constants.LECTORAT_EIGHTEEN_ID)
        )

        # When
        TiteliveBookSearch().synchronize_products(datetime.date(2022, 12, 1), 1)

        # Then
        product = offers_models.Product.query.one()
        assert product.gcuCompatibilityType == offers_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE

    def test_update_offers_extra_data_from_thing(self, requests_mock):
        product = self.build_previously_synced_book_product()
        self.setup_api_response_fixture(requests_mock, fixtures.build_titelive_one_book_response())

        # When
        TiteliveBookSearch().synchronize_products(datetime.date(2022, 12, 1), 1)

        # Then
        product = offers_models.Product.query.one()

        assert product.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert product.extraData.get("bookFormat") == providers_constants.BookFormat.BEAUX_LIVRES.value
        assert product.extraData.get("ean") == self.EAN_TEST

        assert product.extraData.get("gtl_id") == "03020300"
        closest_csr = {"label": "Bandes dessinées adultes / Comics", "csr_id": "1901"}
        assert product.extraData.get("csr_id") == closest_csr.get("csr_id")
        assert product.extraData.get("rayon") == closest_csr.get("label")
        assert product.extraData.get("code_clil") == "3774"

    # APPROVAL
    def test_approve_product_from_inappropriate_thing(self, requests_mock):
        product = self.build_previously_synced_book_product(
            gcuCompatibilityType=offers_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE
        )
        self.setup_api_response_fixture(
            requests_mock,
            fixtures.build_titelive_one_book_response(ean=self.EAN_TEST),
        )

        # When
        TiteliveBookSearch().synchronize_products(datetime.date(2022, 12, 1), 1)

        # Then
        product = offers_models.Product.query.one()
        assert product.isGcuCompatible

    def test_approve_product_and_offers_from_inappropriate_thing(self, requests_mock):
        product = self.build_previously_synced_book_product(
            gcuCompatibilityType=offers_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE
        )
        offer = offers_factories.ThingOfferFactory(
            product=product,
            validation=OfferValidationStatus.REJECTED,
            lastValidationType=OfferValidationType.CGU_INCOMPATIBLE_PRODUCT,
        )

        self.setup_api_response_fixture(
            requests_mock,
            fixtures.build_titelive_one_book_response(ean=self.EAN_TEST),
        )

        # When
        TiteliveBookSearch().synchronize_products(datetime.date(2022, 12, 1), 1)

        # Then
        product = offers_models.Product.query.one()
        assert product.isGcuCompatible

        offers = offers_models.Offer.query.all()
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
    def test_handles_all_authors_formats(self, requests_mock, auteurs_multi, expected_author):
        # Given
        self.setup_api_response_fixture(
            requests_mock, fixtures.build_titelive_one_book_response(auteurs_multi=auteurs_multi)
        )

        # When
        TiteliveBookSearch().synchronize_products(datetime.date(2022, 12, 1), 1)

        # Then
        product = offers_models.Product.query.one()
        assert product.extraData.get("author") == expected_author

    def test_approval_should_not_override_fraud_incompatibility(self, requests_mock):
        product = self.build_previously_synced_book_product(
            gcuCompatibilityType=offers_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE
        )
        self.setup_api_response_fixture(
            requests_mock,
            fixtures.build_titelive_one_book_response(ean=self.EAN_TEST),
        )

        # When
        TiteliveBookSearch().synchronize_products(datetime.date(2022, 12, 1), 1)

        # Then
        product = offers_models.Product.query.one()
        assert product.gcuCompatibilityType == offers_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE
