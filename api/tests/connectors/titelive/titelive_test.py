import html

from pcapi.connectors import titelive
from pcapi.core.categories import subcategories
from pcapi.core.testing import override_settings
from pcapi.domain.titelive import read_things_date

from tests.connectors.titelive import fixtures


@override_settings(TITELIVE_EPAGINE_API_USERNAME="test@example.com")
@override_settings(TITELIVE_EPAGINE_API_PASSWORD="qwerty123")
def test_get_jwt_token(requests_mock):
    requests_mock.post(
        "https://login.epagine.fr/v1/login/test@example.com/token",
        json={"token": "XYZ"},
    )
    assert titelive.get_jwt_token() == "XYZ"


@override_settings(TITELIVE_EPAGINE_API_USERNAME="test@example.com")
@override_settings(TITELIVE_EPAGINE_API_PASSWORD="qwerty123")
def test_get_by_ean13(requests_mock):
    ean = "9782070455379"
    requests_mock.post(
        "https://login.epagine.fr/v1/login/test@example.com/token",
        json={"token": "XYZ"},
    )
    requests_mock.get(
        f"https://catsearch.epagine.fr/v1/ean/{ean}",
        json=fixtures.EAN_SEARCH_FIXTURE,
    )
    assert titelive.get_by_ean13(ean) == fixtures.EAN_SEARCH_FIXTURE


@override_settings(TITELIVE_EPAGINE_API_USERNAME="test@example.com")
@override_settings(TITELIVE_EPAGINE_API_PASSWORD="qwerty123")
def test_get_new_product_from_ean_13(requests_mock):
    ean = "9782070455379"
    requests_mock.post(
        "https://login.epagine.fr/v1/login/test@example.com/token",
        json={"token": "XYZ"},
    )
    requests_mock.get(
        f"https://catsearch.epagine.fr/v1/ean/{ean}",
        json=fixtures.EAN_SEARCH_FIXTURE,
    )
    json = fixtures.EAN_SEARCH_FIXTURE
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
