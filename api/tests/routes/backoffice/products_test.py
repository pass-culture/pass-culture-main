import html
import json
import re
from unittest.mock import patch

from flask import url_for
import pytest

from pcapi.core.categories import subcategories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.routes.backoffice.filters import format_titelive_id_lectorat

from tests.connectors.titelive import fixtures

from .helpers import html_parser
from .helpers.get import GetEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class GetProductDetailsTest(GetEndpointHelper):
    endpoint = "backoffice_web.product.get_product_details"
    endpoint_kwargs = {"product_id": 1}
    needed_permission = perm_models.Permissions.READ_OFFERS

    # session + user + product + unlinked offers + whitelist product
    expected_num_queries = 5

    @patch("pcapi.routes.backoffice.products.blueprint.get_by_ean13")
    def test_get_detail_product(self, mock_get_by_ean13, authenticated_client):
        article = fixtures.BOOK_BY_SINGLE_EAN_FIXTURE["oeuvre"]["article"][0]
        mock_get_by_ean13.return_value = fixtures.BOOK_BY_SINGLE_EAN_FIXTURE

        product = offers_factories.ProductFactory.create(
            description="Une offre pour tester",
            ean="1234567891234",
            extraData={"author": "Author", "editeur": "Editor", "gtl_id": "08010000"},
        )

        offers_factories.OfferFactory.create(product=product, ean="1234567891234")

        # offre non liées au produit
        offers_factories.OfferFactory.create(ean="1234567891234")

        url = url_for(self.endpoint, product_id=product.id, _external=True)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        descriptions = html_parser.extract_descriptions(response.data)
        assert str(product.id) == descriptions["Product ID"]

        assert descriptions["Catégorie"] == "Livre"
        assert descriptions["Sous-catégorie"] == "Livre papier"
        assert descriptions["Type de musique"] == "Alternatif"
        assert descriptions["Nombre d'offres associées"] == "1"
        assert descriptions["Approuvées actives"] == "1"
        assert descriptions["Approuvées inactives"] == "0"
        assert descriptions["En attente"] == "0"
        assert descriptions["Rejetées"] == "0"
        assert descriptions["Offres non liées"] == "1"
        assert descriptions["Auteur"] == "Author"
        assert descriptions["EAN"] == "1234567891234"
        assert descriptions["Éditeur"] == "Editor"
        assert descriptions["Description"] == "Une offre pour tester"

        soup = html_parser.get_soup(response.data)
        card_titles = html_parser.extract_cards_titles(response.data)
        card_text = html_parser.extract_cards_text(response.data)
        card_ean = soup.find(id="titelive-data")

        assert card_ean
        assert fixtures.BOOK_BY_SINGLE_EAN_FIXTURE["oeuvre"]["titre"] in card_titles[0]
        assert soup.select(
            f'div.pc-ean-result img[src="{fixtures.BOOK_BY_SINGLE_EAN_FIXTURE["oeuvre"]["article"][0]["imagesUrl"]["recto"]}"]'
        )
        assert fixtures.BOOK_BY_SINGLE_EAN_FIXTURE["oeuvre"]["titre"] in card_text[0]
        assert "EAN-13 : " + fixtures.BOOK_BY_SINGLE_EAN_FIXTURE["ean"] in card_text[0]
        assert "Lectorat : " + format_titelive_id_lectorat(article["id_lectorat"]) in card_text[0]

        assert (
            "Prix HT : "
            + str(article["prixpays"]["fr"]["value"])
            + " "
            + html.unescape(article["prixpays"]["fr"]["devise"])
            in card_text[0]
        )
        assert "Taux TVA : " + article["taux_tva"] + " %" in card_text[0]
        assert "Code CLIL : " + article["code_clil"] in card_text[0]
        assert "Code support : " + article["libellesupport"] + " (" + article["codesupport"] + ")" in card_text[0]
        assert "Code GTL : Littérature (01000000) Rayon (CSR): Littérature française (0100)" in card_text[0]
        assert "Récit (01050000) Rayon (CSR): Littérature française Récits, Aventures, Voyages (0105)" in card_text[0]
        assert "Inéligible pass Culture :" not in card_text[0]
        assert "EAN white listé : Non" in card_text[0]

        buttons = html_parser.extract(response.data, "button")
        assert "Offres liées" in buttons
        assert "Offres non liées" in buttons

        badges = html_parser.extract_badges(response.data)
        assert "• Compatible" in badges

    @patch("pcapi.routes.backoffice.products.blueprint.get_by_ean13")
    def test_get_detail_product_without_ean(self, mock_get_by_ean13, authenticated_client):
        product = offers_factories.ProductFactory.create(subcategoryId=subcategories.SEANCE_CINE.id)

        url = url_for(self.endpoint, product_id=product.id, _external=True)
        with assert_num_queries(self.expected_num_queries - 2):  # remove query unlinked offers and whitelist product
            response = authenticated_client.get(url)
            assert response.status_code == 200

        soup = html_parser.get_soup(response.data)
        card_ean = soup.find(id="titelive-data")
        assert not card_ean

        mock_get_by_ean13.assert_not_called()

    @patch("pcapi.routes.backoffice.products.blueprint.get_by_ean13")
    def test_get_detail_product_check_offer_format(self, mock_get_by_ean13, authenticated_client):
        product = offers_factories.ProductFactory.create(
            description="Une offre pour tester",
            ean="1234567891234",
            extraData={"author": "Author", "editeur": "Editor", "gtl_id": "08010000"},
        )

        offer = offers_factories.OfferFactory.create(
            product=product, venue=offerers_factories.VenueFactory.create(name="Venue 1"), ean="1234567891234"
        )
        offers_factories.StockFactory.create(offer=offer, price=10)

        # offre non liées au produit
        unlinked_offer = offers_factories.OfferFactory.create(
            venue=offerers_factories.VenueFactory.create(name="Venue 2"), ean="1234567891234"
        )

        url = url_for(self.endpoint, product_id=product.id, _external=True)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        soup = html_parser.get_soup(response.data)
        scripts = soup.find_all("script")
        for script in scripts:
            if "offers = " in str(script):
                offers_json = re.search(r"const (unlinked_offers|offers) = (\[\{.*?\}\]);", str(script))
                if offers_json:
                    offers = json.loads(offers_json.group(2))
                    if offers_json.group(1) == "offers":
                        assert offers[0]["id"] == offer.id
                        assert offers[0]["name"] == offer.name
                        assert offers[0]["venue_name"] == offer.venue.name
                        assert offers[0]["status"] == "Publiée"
                    elif offers_json.group(1) == "unlinked_offers":
                        assert offers[0]["id"] == unlinked_offer.id
                        assert offers[0]["name"] == unlinked_offer.name
                        assert offers[0]["venue_name"] == unlinked_offer.venue.name
                        assert offers[0]["status"] == "Épuisée"
