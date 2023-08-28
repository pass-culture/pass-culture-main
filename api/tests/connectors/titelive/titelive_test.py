import datetime
import html

import freezegun
import pytest
import requests

from pcapi.connectors import titelive
from pcapi.connectors.titelive import GtlIdError
from pcapi.core.categories import subcategories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
import pcapi.core.providers.constants as providers_constants
import pcapi.core.providers.factories as providers_factories
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
from pcapi.core.testing import override_settings
from pcapi.domain.titelive import read_things_date
from pcapi.utils.requests import ExternalAPIException

from tests.connectors.titelive import fixtures


@override_settings(TITELIVE_EPAGINE_API_USERNAME="test@example.com")
@override_settings(TITELIVE_EPAGINE_API_PASSWORD="qwerty123")
class TiteliveTest:
    def _configure_mock(self, requests_mock, **kwargs):
        requests_mock.post(
            "https://login.epagine.fr/v1/login/test@example.com/token",
            json={"token": "XYZ"},
        )
        if "ean" in kwargs:
            requests_mock.get(
                f"https://catsearch.epagine.fr/v1/ean/{kwargs['ean']}",
                json=fixtures.BOOK_BY_EAN_FIXTURE if "fixture" not in kwargs else kwargs["fixture"],
            )

    def test_get_jwt_token(self, requests_mock):
        self._configure_mock(requests_mock)

        assert titelive.get_jwt_token() == "XYZ"

    def test_get_by_ean13(self, requests_mock):
        ean = "9782070455379"
        json = fixtures.BOOK_BY_EAN_FIXTURE
        self._configure_mock(requests_mock, ean=ean, fixture=json)

        assert titelive.get_by_ean13(ean) == json

    def test_get_new_product_from_ean_13(self, requests_mock):
        ean = "9782070455379"
        json = fixtures.BOOK_BY_EAN_FIXTURE
        self._configure_mock(requests_mock, ean=ean, fixture=json)

        oeuvre = json["oeuvre"]
        article = oeuvre["article"][0]

        product = titelive.get_new_product_from_ean13(ean)

        assert product.idAtProviders == ean
        assert product.description == html.unescape(article["resume"])
        assert product.thumbCount == article["image"]
        assert product.name == oeuvre["titre"]
        assert product.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert product.extraData["author"] == oeuvre["auteurs"]
        assert product.extraData["author"] == oeuvre["auteurs"]
        assert product.extraData["ean"] == ean
        assert product.extraData["prix_livre"] == article["prix"]
        assert product.extraData["collection"] == article["collection"]
        assert product.extraData["comic_series"] == article["serie"]
        assert product.extraData["date_parution"] == read_things_date(article["dateparution"])
        assert product.extraData["distributeur"] == article["distributeur"]
        assert product.extraData["editeur"] == article["editeur"]
        assert product.extraData["num_in_collection"] == article["collection_no"]
        assert product.extraData["schoolbook"] == (article["scolaire"] == "1")
        assert product.extraData["csr_id"] == "0105"
        assert product.extraData["gtl_id"] == "01050000"
        assert product.extraData["code_clil"] == "3665"

    def test_get_new_product_from_ean_13_without_gtl(self, requests_mock):
        ean = "9782070455379"
        json = fixtures.BOOK_BY_EAN_FIXTURE

        del json["oeuvre"]["article"][0]["gtl"]

        self._configure_mock(requests_mock, ean=ean, fixture=json)

        with pytest.raises(GtlIdError) as error:
            titelive.get_new_product_from_ean13(ean)
        assert f"EAN {ean} does not have a titelive gtl_id" in str(error.value)


@override_settings(TITELIVE_EPAGINE_API_USERNAME="test@example.com")
@override_settings(TITELIVE_EPAGINE_API_PASSWORD="qwerty123")
@pytest.mark.usefixtures("db_session")
class TiteliveSearchTest:
    def _configure_login_mock(self, requests_mock):
        requests_mock.post(
            "https://login.epagine.fr/v1/login/test@example.com/token",
            json={"token": "XYZ"},
        )

    def test_titelive_music_sync(self, requests_mock):
        self._configure_login_mock(requests_mock)
        requests_mock.get("https://catsearch.epagine.fr/v1/search", json=fixtures.MUSIC_SEARCH_FIXTURE)
        titelive_epagine_provider = providers_repository.get_provider_by_name(
            providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME
        )
        offers_factories.ProductFactory(
            extraData={"ean": "3700187679323"}, idAtProviders="3700187679323", lastProvider=titelive_epagine_provider
        )

        titelive.TiteliveMusicSearch().synchronize_products(datetime.date(2022, 12, 1))

        cd_product = offers_models.Product.query.filter(
            offers_models.Product.idAtProviders == "3700187679323",
            offers_models.Product.lastProvider == titelive_epagine_provider,  # pylint: disable=comparison-with-callable
        ).one()
        assert cd_product is not None
        assert cd_product.name == "Les dernières volontés de Mozart (symphony)"
        assert cd_product.description == 'GIMS revient avec " Les dernières volontés de Mozart ", un album de tubes.'
        assert cd_product.subcategoryId == subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id
        assert cd_product.extraData["artist"] == "Gims"
        assert cd_product.extraData["author"] == "Gims"
        assert cd_product.extraData["date_parution"] == "2022-12-02"
        assert cd_product.extraData["disponibility"] == "Disponible"
        assert cd_product.extraData["distributeur"] == "Believe"
        assert cd_product.extraData["ean"] == "3700187679323"
        assert cd_product.extraData["editeur"] == "BELIEVE"
        assert cd_product.extraData["music_label"] == "PLAY TWO"
        assert cd_product.extraData["nb_galettes"] == "1"
        assert cd_product.extraData["performer"] == "Gims"
        assert cd_product.extraData["musicType"] == "-1"
        assert cd_product.extraData["musicSubType"] == "-1"

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
        assert shared_gtl_product.subcategoryId == subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id
        assert shared_gtl_product.extraData["artist"] == "Gims"
        assert shared_gtl_product.extraData["author"] == "Gims"
        assert shared_gtl_product.extraData["date_parution"] == "2022-12-02"
        assert shared_gtl_product.extraData["disponibility"] == "Disponible"
        assert shared_gtl_product.extraData["distributeur"] == "Believe"
        assert shared_gtl_product.extraData["ean"] == "3700187679324"
        assert shared_gtl_product.extraData["editeur"] == "BELIEVE"
        assert shared_gtl_product.extraData["music_label"] == "PLAY TWO"
        assert shared_gtl_product.extraData["nb_galettes"] == "1"
        assert shared_gtl_product.extraData["performer"] == "Gims"
        assert shared_gtl_product.extraData["musicType"] == "-1"
        assert shared_gtl_product.extraData["musicSubType"] == "-1"

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
        assert vinyle_product.subcategoryId == subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id
        assert vinyle_product.extraData["artist"] == "Gorillaz"
        assert vinyle_product.extraData["author"] == "Gorillaz"
        assert vinyle_product.extraData["date_parution"] == "2023-02-24"
        assert vinyle_product.extraData["disponibility"] == "Disponible"
        assert vinyle_product.extraData["distributeur"] == "Warner Music France"
        assert vinyle_product.extraData["ean"] == "5054197199738"
        assert vinyle_product.extraData["editeur"] == "WARNER MUSIC UK"
        assert vinyle_product.extraData["music_label"] == "WARNER MUSIC UK"
        assert vinyle_product.extraData["nb_galettes"] == "1"
        assert vinyle_product.extraData["performer"] == "Gorillaz"
        assert shared_gtl_product.extraData["musicType"] == "-1"
        assert shared_gtl_product.extraData["musicSubType"] == "-1"

    def test_titelive_search_query_params(self, requests_mock):
        self._configure_login_mock(requests_mock)
        requests_mock.get("https://catsearch.epagine.fr/v1/search", json={})

        titelive.TiteliveMusicSearch().get_titelive_search_json(datetime.date(2022, 12, 1), 2)

        assert requests_mock.last_request.qs["base"] == ["music"]
        assert requests_mock.last_request.qs["nombre"] == ["25"]
        assert requests_mock.last_request.qs["page"] == ["2"]
        assert requests_mock.last_request.qs["tri"] == ["datemodification"]
        assert requests_mock.last_request.qs["tri_ordre"] == ["asc"]
        assert requests_mock.last_request.qs["dateminm"] == ["01/12/2022"]

    @freezegun.freeze_time("2023-01-01")
    def test_titelive_sync_event(self, requests_mock):
        self._configure_login_mock(requests_mock)
        requests_mock.get(
            "https://catsearch.epagine.fr/v1/search",
            json={"type": 4, "magid": "7", "nombre": 10, "page": 1, "result": []},
        )
        titelive_epagine_provider = providers_repository.get_provider_by_name(
            providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME
        )
        providers_factories.LocalProviderEventFactory(
            provider=titelive_epagine_provider,
            type=providers_models.LocalProviderEventType.SyncEnd,
            date=datetime.datetime(2022, 5, 5),
            payload=titelive.TiteliveBase.MUSIC.value,
        )

        titelive.TiteliveMusicSearch().synchronize_products()

        assert requests_mock.last_request.qs["dateminm"] == ["05/05/2022"]

        stop_event, start_event = providers_models.LocalProviderEvent.query.order_by(
            providers_models.LocalProviderEvent.id.desc()
        ).limit(2)
        assert stop_event.provider == start_event.provider == titelive_epagine_provider
        assert stop_event.date == start_event.date == datetime.datetime(2023, 1, 1)
        assert stop_event.payload == start_event.payload == titelive.TiteliveBase.MUSIC.value
        assert stop_event.type == providers_models.LocalProviderEventType.SyncEnd
        assert start_event.type == providers_models.LocalProviderEventType.SyncStart

    def test_titelive_sync_event_on_failure(self, requests_mock):
        self._configure_login_mock(requests_mock)
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
            titelive.TiteliveMusicSearch().synchronize_products()

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
        assert end_sync_events_query.count() == 1

    def test_sync_does_not_overwrite_existing_provider(self, requests_mock):
        self._configure_login_mock(requests_mock)
        requests_mock.get("https://catsearch.epagine.fr/v1/search", json=fixtures.MUSIC_SEARCH_FIXTURE)
        offers_factories.ProductFactory(extraData={"ean": "3700187679323"})

        titelive.TiteliveMusicSearch().synchronize_products(datetime.date(2022, 12, 1))

        products_with_same_ean_query = offers_models.Product.query.filter(
            offers_models.Product.extraData["ean"].astext == "3700187679323"
        )
        assert products_with_same_ean_query.count() == 2

        titelive_epagine_provider = providers_repository.get_provider_by_name(
            providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME
        )
        titelive_synced_products_query = offers_models.Product.query.filter(
            offers_models.Product.lastProvider == titelive_epagine_provider  # pylint: disable=comparison-with-callable
        )
        assert titelive_synced_products_query.count() == 3
