import html

import pytest

from pcapi.connectors import titelive
from pcapi.connectors.titelive import GtlIdError
from pcapi.core.categories import subcategories
from pcapi.core.testing import override_settings
from pcapi.domain.titelive import read_things_date

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
                json=fixtures.EAN_SEARCH_FIXTURE if "fixture" not in kwargs else kwargs["fixture"],
            )

    def test_get_jwt_token(self, requests_mock):
        self._configure_mock(requests_mock)

        assert titelive.get_jwt_token() == "XYZ"

    def test_get_by_ean13(self, requests_mock):
        ean = "9782070455379"
        json = fixtures.EAN_SEARCH_FIXTURE
        self._configure_mock(requests_mock, ean=ean, fixture=json)

        assert titelive.get_by_ean13(ean) == json

    def test_get_new_product_from_ean_13(self, requests_mock):
        ean = "9782070455379"
        json = fixtures.EAN_SEARCH_FIXTURE
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
        json = fixtures.EAN_SEARCH_FIXTURE

        del json["oeuvre"]["article"][0]["gtl"]

        self._configure_mock(requests_mock, ean=ean, fixture=json)

        with pytest.raises(GtlIdError) as error:
            titelive.get_new_product_from_ean13(ean)
        assert f"EAN {ean} does not have a titelive gtl_id" in str(error.value)
