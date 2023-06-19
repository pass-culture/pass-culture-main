import datetime
import html
from unittest.mock import patch

from flask import url_for
import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.factories import ProductWhitelistFactory
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
import pcapi.core.permissions.models as perm_models
from pcapi.routes.backoffice_v3.filters import format_titelive_id_lectorat

from ...connectors.titelive.fixtures import EAN_SEARCH_FIXTURE
from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class SearchEanTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.titelive.search_titelive"
    endpoint_kwargs = {"ean": "9782070455379"}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_search_ean_initial(self, authenticated_client):
        response = authenticated_client.get(url_for(self.endpoint))
        soup = html_parser.get_soup(response.data)

        assert response.status_code == 200
        card_ean = soup.select("div.pc-ean-result")
        assert not card_ean

    @patch("pcapi.routes.backoffice_v3.titelive.blueprint.get_by_ean13")
    def test_search_ean_not_whitelisted(self, mock_get_by_ean13, authenticated_client):
        mock_get_by_ean13.return_value = EAN_SEARCH_FIXTURE
        article = EAN_SEARCH_FIXTURE["oeuvre"]["article"][0]

        response = authenticated_client.get(url_for(self.endpoint, **self.endpoint_kwargs))
        soup = html_parser.get_soup(response.data)
        card_titles = html_parser.extract_cards_titles(response.data)
        card_text = html_parser.extract_cards_text(response.data)

        assert response.status_code == 200
        card_ean = soup.select("div.pc-ean-result")
        assert card_ean
        assert EAN_SEARCH_FIXTURE["oeuvre"]["titre"] in card_titles[0]
        assert soup.select(
            f"div.pc-ean-result img[src=\"{EAN_SEARCH_FIXTURE['oeuvre']['article'][0]['imagesUrl']['recto']}\"]"
        )
        assert EAN_SEARCH_FIXTURE["oeuvre"]["titre"] in card_text[0]
        assert "EAN-13 : " + EAN_SEARCH_FIXTURE["ean"] in card_text[0]
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
        assert "Code GTL : Littérature (1000000)Récit (1050000)" in card_text[0]
        assert "EAN white listé : Non" in card_text[0]

    @patch("pcapi.routes.backoffice_v3.titelive.blueprint.get_by_ean13")
    def test_search_ean_whitelisted(self, mock_get_by_ean13, authenticated_client):
        ProductWhitelistFactory(
            ean=self.endpoint_kwargs["ean"],
            comment="Superbe livre !",
            author__firstName="Frank",
            author__lastName="Columbo",
        )
        mock_get_by_ean13.return_value = EAN_SEARCH_FIXTURE

        response = authenticated_client.get(url_for(self.endpoint, **self.endpoint_kwargs))
        card_text = html_parser.extract_cards_text(response.data)

        assert response.status_code == 200
        assert "EAN white listé : Oui" in card_text[0]

        assert f"Date d'ajout : {datetime.datetime.utcnow().strftime('%d/%m/%Y')}" in card_text[0]
        assert "Auteur : Frank Columbo" in card_text[0]
        assert "Commentaire : Superbe livre !" in card_text[0]


class ProductBlackListFormTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.titelive.get_add_product_whitelist_confirmation_form"
    endpoint_kwargs = {"ean": "9782070455379", "title": "Immortelle randonnée ; Compostelle malgré moi"}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_get_search_form(self, authenticated_client):
        response = authenticated_client.get(url_for(self.endpoint, **self.endpoint_kwargs))
        assert response.status_code == 200


class AddProductWhitelistTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.titelive.add_product_whitelist"
    endpoint_kwargs = {"ean": "9782070455379", "title": "Immortelle randonnée ; Compostelle malgré moi"}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS
    form_data = {"comment": "OK!"}

    @patch("pcapi.routes.backoffice_v3.titelive.blueprint.get_by_ean13")
    @patch("pcapi.routes.backoffice_v3.titelive.blueprint.whitelist_existing_product")
    @pytest.mark.parametrize(
        "form_data",
        [
            form_data,
            {"comment": ""},
        ],
    )
    def test_add_product_whitelist(
        self, mock_whitelist_existing_product, mock_get_by_ean13, authenticated_client, form_data
    ):
        mock_get_by_ean13.return_value = EAN_SEARCH_FIXTURE
        assert not fraud_models.ProductWhitelist.query.filter(
            fraud_models.ProductWhitelist.ean == self.endpoint_kwargs["ean"]
        ).one_or_none()

        response = self.post_to_endpoint(authenticated_client, form=form_data, **self.endpoint_kwargs)
        assert response.status_code == 303
        response_redirect = authenticated_client.get(response.location)
        alert = html_parser.extract_alert(response_redirect.data)
        product_whitelist = fraud_models.ProductWhitelist.query.filter(
            fraud_models.ProductWhitelist.ean == self.endpoint_kwargs["ean"]
        ).one()

        assert "a été ajouté dans la whitelist" in alert
        assert product_whitelist.comment == form_data["comment"]
        assert product_whitelist.ean == self.endpoint_kwargs["ean"]
        mock_whitelist_existing_product.assert_called_with(self.endpoint_kwargs["ean"])

    @patch("pcapi.routes.backoffice_v3.titelive.blueprint.get_by_ean13")
    @patch("pcapi.routes.backoffice_v3.titelive.blueprint.whitelist_existing_product")
    def test_add_product_whitelist_already_whitelisted(
        self, mock_whitelist_existing_product, mock_get_by_ean13, authenticated_client
    ):
        mock_get_by_ean13.return_value = EAN_SEARCH_FIXTURE
        ProductWhitelistFactory(ean=self.endpoint_kwargs["ean"])
        assert fraud_models.ProductWhitelist.query.filter(
            fraud_models.ProductWhitelist.ean == self.endpoint_kwargs["ean"]
        ).one()

        response = self.post_to_endpoint(authenticated_client, form=self.form_data, **self.endpoint_kwargs)
        assert response.status_code == 303
        response_redirect = authenticated_client.get(response.location)
        alert = html_parser.extract_alert(response_redirect.data)

        assert "est déjà dans la whitelist" in alert
        mock_whitelist_existing_product.assert_not_called()


class DeleteProductWhitelistTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.titelive.delete_product_whitelist"
    endpoint_kwargs = {"ean": "9782070455379"}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    @patch("pcapi.routes.backoffice_v3.titelive.blueprint.get_by_ean13")
    @patch("pcapi.routes.backoffice_v3.titelive.blueprint.delete_unwanted_existing_product")
    def test_delete_product_whitelist(
        self, mock_delete_unwanted_existing_product, mock_get_by_ean13, authenticated_client
    ):
        mock_get_by_ean13.return_value = EAN_SEARCH_FIXTURE
        ProductWhitelistFactory(ean=self.endpoint_kwargs["ean"])
        response = authenticated_client.get(url_for(self.endpoint, **self.endpoint_kwargs))

        assert response.status_code == 303
        response_redirect = authenticated_client.get(response.location)
        alert = html_parser.extract_alert(response_redirect.data)

        assert "a été supprimé de la whitelist" in alert
        mock_delete_unwanted_existing_product.assert_called_with(self.endpoint_kwargs["ean"])

    @patch("pcapi.routes.backoffice_v3.titelive.blueprint.get_by_ean13")
    @patch("pcapi.routes.backoffice_v3.titelive.blueprint.delete_unwanted_existing_product")
    def test_delete_product_whitelist_not_in_whitelist(
        self, mock_delete_unwanted_existing_product, mock_get_by_ean13, authenticated_client
    ):
        mock_get_by_ean13.return_value = EAN_SEARCH_FIXTURE
        response = authenticated_client.get(url_for(self.endpoint, **self.endpoint_kwargs))

        assert response.status_code == 303
        response_redirect = authenticated_client.get(response.location)
        alert = html_parser.extract_alert(response_redirect.data)

        assert "n'existe pas dans la whitelist" in alert
        mock_delete_unwanted_existing_product.assert_not_called()

    @patch("pcapi.routes.backoffice_v3.titelive.blueprint.get_by_ean13")
    def test_delete_product_white_list_but_keep_product_if_booked(self, mock_get_by_ean13, authenticated_client):
        mock_get_by_ean13.return_value = EAN_SEARCH_FIXTURE
        ProductWhitelistFactory(ean=self.endpoint_kwargs["ean"])

        product = offers_factories.ProductFactory(
            idAtProviders=self.endpoint_kwargs["ean"],
            isGcuCompatible=True,
            isSynchronizationCompatible=True,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )
        bookings_factories.BookingFactory(stock__offer__product=product)

        response = authenticated_client.get(url_for(self.endpoint, **self.endpoint_kwargs))

        assert response.status_code == 303
        response_redirect = authenticated_client.get(response.location)
        alert = html_parser.extract_alert(response_redirect.data)

        offer = offers_models.Offer.query.one()
        assert offer.isActive is False
        assert offers_models.Product.query.one() == product
        assert not product.isGcuCompatible
        assert not product.isSynchronizationCompatible
        assert (
            f"Le produit \"{self.endpoint_kwargs['ean']}\" ayant encore des réservations, il a été désactivé au lieu d'être supprimé"
            in alert
        )
