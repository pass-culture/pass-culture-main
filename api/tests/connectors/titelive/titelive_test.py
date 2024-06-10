from copy import deepcopy
import datetime
import html

import pytest

from pcapi import settings
from pcapi.connectors import titelive
from pcapi.connectors.titelive import GtlIdError
from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.providers.constants as providers_constants
from pcapi.core.testing import override_settings
from pcapi.domain.titelive import parse_things_date_to_string

from tests.connectors.titelive import fixtures


@override_settings(TITELIVE_EPAGINE_API_USERNAME="test@example.com")
@override_settings(TITELIVE_EPAGINE_API_PASSWORD="qwerty123")
class TiteliveTest:
    def _configure_mock(self, requests_mock, **kwargs):
        requests_mock.post(
            f"{settings.TITELIVE_EPAGINE_API_AUTH_URL}/login/test@example.com/token",
            json={"token": "XYZ"},
        )
        if "ean" in kwargs:
            requests_mock.get(
                f"{settings.TITELIVE_EPAGINE_API_URL}/ean/{kwargs['ean']}",
                json=kwargs.get("fixture", fixtures.BOOK_BY_EAN_FIXTURE),
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
        assert product.lastProvider.name == providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME
        assert product.extraData["author"] == oeuvre["auteurs"]
        assert product.extraData["ean"] == ean
        assert product.extraData["prix_livre"] == article["prix"]
        assert product.extraData["collection"] == article["collection"]
        assert product.extraData["comic_series"] == article["serie"]
        assert product.extraData["date_parution"] == parse_things_date_to_string(article["dateparution"])
        assert product.extraData["distributeur"] == article["distributeur"]
        assert product.extraData["editeur"] == article["editeur"]
        assert product.extraData["num_in_collection"] == article["collection_no"]
        assert product.extraData["schoolbook"] == (article["scolaire"] == "1")
        assert product.extraData["csr_id"] == "0105"
        assert product.extraData["gtl_id"] == "01050000"
        assert product.extraData["code_clil"] == "3665"

    def test_get_new_product_without_resume_from_ean_13(self, requests_mock):
        ean = "9782070455379"
        json = deepcopy(fixtures.BOOK_BY_EAN_FIXTURE)
        del json["oeuvre"]["article"][0]["resume"]
        self._configure_mock(requests_mock, ean=ean, fixture=json)

        product = titelive.get_new_product_from_ean13(ean)

        assert product.idAtProviders == ean
        assert product.description is None

    def test_get_new_product_from_ean_13_without_gtl(self, requests_mock):
        ean = "9782070455379"
        json = deepcopy(fixtures.BOOK_BY_EAN_FIXTURE)

        del json["oeuvre"]["article"][0]["gtl"]

        self._configure_mock(requests_mock, ean=ean, fixture=json)

        with pytest.raises(GtlIdError) as error:
            titelive.get_new_product_from_ean13(ean)
        assert f"EAN {ean} does not have a titelive gtl_id" in str(error.value)

    def test_titelive_search_query_params(self, requests_mock):
        self._configure_mock(requests_mock)
        requests_mock.get(f"{settings.TITELIVE_EPAGINE_API_URL}/search", json={"result": {}})

        titelive.search_products(titelive.TiteliveBase.MUSIC, datetime.date(2022, 12, 1), 2)

        assert requests_mock.last_request.qs["base"] == ["music"]
        assert requests_mock.last_request.qs["nombre"] == ["25"]
        assert requests_mock.last_request.qs["page"] == ["2"]
        assert requests_mock.last_request.qs["tri"] == ["datemodification"]
        assert requests_mock.last_request.qs["tri_ordre"] == ["asc"]
        assert requests_mock.last_request.qs["dateminm"] == ["01/12/2022"]
