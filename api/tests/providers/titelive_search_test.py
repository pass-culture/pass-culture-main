import copy
import datetime
import pathlib
import re

import freezegun
import pytest
import requests

from pcapi.connectors import titelive
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
import pcapi.core.providers.constants as providers_constants
import pcapi.core.providers.factories as providers_factories
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
from pcapi.core.providers.titelive_music_search import TiteliveMusicSearch
from pcapi.core.testing import override_settings
from pcapi.domain import music_types
from pcapi.utils.requests import ExternalAPIException

import tests
from tests.connectors.titelive import fixtures


@override_settings(TITELIVE_EPAGINE_API_USERNAME="test@example.com")
@override_settings(TITELIVE_EPAGINE_API_PASSWORD="qwerty123")
@pytest.mark.usefixtures("db_session")
class TiteliveSearchTest:
    def _configure_login_and_images(self, requests_mock):
        requests_mock.post(
            "https://login.epagine.fr/v1/login/test@example.com/token",
            json={"token": "XYZ"},
        )
        image_path = pathlib.Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(image_path, "rb") as thumb_file:
            requests_mock.get(re.compile("image"), content=thumb_file.read())

    def test_titelive_music_sync(self, requests_mock):
        self._configure_login_and_images(requests_mock)
        requests_mock.get("https://catsearch.epagine.fr/v1/search?page=1", json=fixtures.MUSIC_SEARCH_FIXTURE)
        requests_mock.get("https://catsearch.epagine.fr/v1/search?page=2", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE)
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

    @freezegun.freeze_time("2023-01-01")
    def test_titelive_sync_event(self, requests_mock):
        self._configure_login_and_images(requests_mock)
        requests_mock.get("https://catsearch.epagine.fr/v1/search", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE)
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
        self._configure_login_and_images(requests_mock)
        requests_mock.get("https://catsearch.epagine.fr/v1/search", exc=requests.exceptions.RequestException)
        titelive_epagine_provider = providers_repository.get_provider_by_name(
            providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME
        )
        providers_factories.LocalProviderEventFactory(
            provider=titelive_epagine_provider,
            type=providers_models.LocalProviderEventType.SyncEnd,
            payload=titelive.TiteliveBase.MUSIC.value,
        )

        with pytest.raises(ExternalAPIException):
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
        self._configure_login_and_images(requests_mock)
        requests_mock.get("https://catsearch.epagine.fr/v1/search?page=1", json=fixtures.MUSIC_SEARCH_FIXTURE)
        requests_mock.get("https://catsearch.epagine.fr/v1/search?page=2", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE)
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
        self._configure_login_and_images(requests_mock)
        requests_mock.get("https://catsearch.epagine.fr/v1/search?page=1", json=fixtures.MUSIC_SEARCH_FIXTURE)
        requests_mock.get("https://catsearch.epagine.fr/v1/search?page=2", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE)

        TiteliveMusicSearch().synchronize_products(datetime.date(2022, 12, 1))

        synced_products = offers_models.Product.query.all()
        assert len(synced_products) == 3
        assert all(synced_product.thumbUrl is not None for synced_product in synced_products)

    def test_sync_thumbnails_failure_is_silent(self, requests_mock):
        self._configure_login_and_images(requests_mock)
        requests_mock.get("https://catsearch.epagine.fr/v1/search?page=1", json=fixtures.MUSIC_SEARCH_FIXTURE)
        requests_mock.get("https://catsearch.epagine.fr/v1/search?page=2", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE)
        requests_mock.get("https://images.epagine.fr/323/3700187679324.jpg", exc=requests.exceptions.RequestException)

        assert TiteliveMusicSearch().synchronize_products(datetime.date(2022, 12, 1)) is None

        synced_products = offers_models.Product.query.all()
        assert len(synced_products) == 3
        assert len([product for product in synced_products if product.thumbUrl is not None]) == 2

        no_thumbnail_product = next(
            (product for product in synced_products if product.idAtProviders == "3700187679324"), None
        )
        assert no_thumbnail_product is not None
        assert no_thumbnail_product.thumbUrl is None

    def test_sync_skips_unallowed_format(self, requests_mock):
        self._configure_login_and_images(requests_mock)
        not_fully_allowed_response = copy.deepcopy(fixtures.MUSIC_SEARCH_FIXTURE)
        not_fully_allowed_response["result"][-1]["article"]["1"]["codesupport"] = 35
        del not_fully_allowed_response["result"][0]["article"]["2"]["codesupport"]
        requests_mock.get("https://catsearch.epagine.fr/v1/search?page=1", json=not_fully_allowed_response)
        requests_mock.get(
            "https://catsearch.epagine.fr/v1/search?page=2",
            json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE,
        )

        TiteliveMusicSearch().synchronize_products(datetime.date(2022, 12, 1))

        synced_product = offers_models.Product.query.one()
        assert synced_product.idAtProviders == "3700187679323"

    def test_titelive_music_sync_from_page(self, requests_mock):
        self._configure_login_and_images(requests_mock)
        requests_mock.get("https://catsearch.epagine.fr/v1/search?page=1", json=fixtures.MUSIC_SEARCH_FIXTURE)
        requests_mock.get("https://catsearch.epagine.fr/v1/search?page=2", json=fixtures.EMPTY_MUSIC_SEARCH_FIXTURE)

        TiteliveMusicSearch().synchronize_products(datetime.date(2022, 12, 1), 2)

        assert offers_models.Product.query.count() == 0
