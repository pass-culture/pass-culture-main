import pathlib
import re
from unittest.mock import patch

import pytest
from flask import url_for

import pcapi.core.finance.utils as finance_utils
import pcapi.core.fraud.models as fraud_models
import pcapi.core.offers.exceptions as offers_exceptions
import pcapi.core.offers.models as offer_models
from pcapi.connectors.titelive import GtlIdError
from pcapi.core.categories import subcategories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.permissions import factories as perm_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.routes.backoffice.filters import format_titelive_id_lectorat
from pcapi.routes.backoffice.products.forms import ProductFilterTypeEnum

import tests
from tests.connectors.titelive import fixtures

from .helpers import button as button_helpers
from .helpers import html_parser
from .helpers import search as search_helpers
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class SearchProductTest(search_helpers.SearchHelper, GetEndpointHelper):
    endpoint = "backoffice_web.product.search_product"
    needed_permission = perm_models.Permissions.READ_OFFERS

    # session + product
    expected_num_queries = 2

    @pytest.mark.parametrize("ean", ["1234567891234", "1234 5678 9123 4", "1234-5678-9123-4"])
    def test_search_by_ean_existing_product(self, ean, authenticated_client):
        product = offers_factories.ProductFactory.create(
            description="Une offre pour tester",
            ean="1234567891234",
            extraData={"author": "Author", "editeur": "Editor", "gtl_id": "08010000"},
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    q=ean,
                    product_filter_type=ProductFilterTypeEnum.EAN.name,
                )
            )
            assert response.status_code == 303

        expected_url = url_for("backoffice_web.product.get_product_details", product_id=product.id)
        assert response.location == expected_url

    @pytest.mark.parametrize(
        "additional_permission,titelive_data, alert_message",
        [
            (
                None,
                fixtures.BOOK_BY_SINGLE_EAN_FIXTURE,
                "Ce produit n'est pas encore dans la base de données du pass Culture.",
            ),
            (
                None,
                fixtures.INELIGIBLE_BOOK_BY_EAN_FIXTURE,
                "Attention : Ce produit est considéré comme inéligible par le pass Culture.",
            ),
            (
                perm_models.Permissions.PRO_FRAUD_ACTIONS,
                fixtures.BOOK_BY_SINGLE_EAN_FIXTURE,
                "Ce produit n'est pas encore dans la base de données du pass Culture. Vous pouvez l'ajouter en cliquant sur le bouton ci-dessous.",
            ),
            (
                perm_models.Permissions.PRO_FRAUD_ACTIONS,
                fixtures.INELIGIBLE_BOOK_BY_EAN_FIXTURE,
                "Attention : Ce produit est considéré comme inéligible par le pass Culture. Cependant, vous pouvez quand même l'ajouter si nécessaire en cliquant sur le bouton ci-dessous. Cela rendra le produit automatiquement éligible.",
            ),
        ],
    )
    @patch("pcapi.routes.backoffice.products.blueprint.get_by_ean13")
    def test_search_by_ean_unexisting_product_on_database_but_exist_on_titelive(
        self, mock_get_by_ean13, additional_permission, titelive_data, alert_message, client
    ):
        mock_get_by_ean13.return_value = titelive_data
        article = titelive_data["oeuvre"]["article"][0]

        user = users_factories.AdminFactory()
        permissions = [db.session.query(perm_models.Permission).filter_by(name=self.needed_permission.name).one()]
        if additional_permission:
            permissions.append(
                db.session.query(perm_models.Permission).filter_by(name=additional_permission.name).one()
            )
        role = perm_factories.RoleFactory(permissions=permissions)
        user.backoffice_profile.roles.append(role)
        db.session.flush()

        authenticated_client = client.with_bo_session_auth(user)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    q="1234567891235",
                    product_filter_type=ProductFilterTypeEnum.EAN.name,
                )
            )
            assert response.status_code == 200

        assert alert_message in html_parser.extract_alert(response.data)

        buttons = html_parser.extract(response.data, "button")
        if additional_permission == perm_models.Permissions.PRO_FRAUD_ACTIONS:
            assert "Importer ce produit dans la base de données du pass Culture" in buttons
        else:
            assert "Importer ce produit dans la base de données du pass Culture" not in buttons

        soup = html_parser.get_soup(response.data)
        card_titles = html_parser.extract_cards_titles(response.data)
        card_text = html_parser.extract_cards_text(response.data)
        card_ean = soup.find(id="titelive-data")

        assert card_ean
        assert card_titles[0] == "Détails du Produit"
        assert soup.select(
            f'div.pc-ean-result img[src="{titelive_data["oeuvre"]["article"][0]["imagesUrl"]["recto"]}"]'
        )
        assert titelive_data["oeuvre"]["titre"] in card_text[0]
        assert "EAN-13 " + titelive_data["ean"] in card_text[0]
        assert "Lectorat " + format_titelive_id_lectorat(article["id_lectorat"]) in card_text[0]

        assert (
            f"Prix HT {finance_utils.format_currency_for_backoffice(article['prixpays']['fr']['value'])}"
            in card_text[0]
        )
        assert "Taux TVA 5,50 %" in card_text[0]
        assert "Code CLIL " + article["code_clil"] in card_text[0]
        assert "Code support " + article["libellesupport"] + " (" + article["codesupport"] + ")" in card_text[0]

        if titelive_data["oeuvre"]["titre"] == fixtures.BOOK_BY_SINGLE_EAN_FIXTURE["oeuvre"]["titre"]:
            assert "Inéligible pass Culture " not in card_text[0]
        else:
            assert "Inéligible pass Culture " in card_text[0]

        assert "EAN whitelisté Non" in card_text[0]

    @patch("pcapi.routes.backoffice.products.blueprint.get_by_ean13")
    def test_search_by_ean_unexisting_product_either_on_database_and_titelive(
        self, mock_get_by_ean13, authenticated_client
    ):
        mock_get_by_ean13.return_value = fixtures.NO_RESULT_BY_EAN_FIXTURE

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    q="1234567891235",
                    product_filter_type=ProductFilterTypeEnum.EAN.name,
                )
            )

        assert response.status_code == 200
        assert (
            "Le produit est introuvable. Il ne figure ni dans notre base de données ni sur Titelive"
            in html_parser.content_as_text(response.data)
        )

    def test_search_by_visa_existing_product(self, authenticated_client):
        product = offers_factories.ProductFactory.create(
            description="Une offre pour tester",
            extraData={"visa": "123456"},
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    q="123456",
                    product_filter_type=ProductFilterTypeEnum.VISA.name,
                )
            )
            assert response.status_code == 303

        expected_url = url_for("backoffice_web.product.get_product_details", product_id=product.id)
        assert response.location == expected_url

    def test_search_by_visa_unexisting_product(self, authenticated_client):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    q="123456",
                    product_filter_type=ProductFilterTypeEnum.ALLOCINE_ID.name,
                )
            )

        assert response.status_code == 200
        assert "Le produit est introuvable" in html_parser.content_as_text(response.data)

    @pytest.mark.parametrize(
        "search_query",
        [
            "123456",
            "000123456",
        ],
    )
    def test_search_by_allocine_id_existing_product(self, authenticated_client, search_query):
        product = offers_factories.ProductFactory.create(
            description="Une offre pour tester",
            extraData={"allocineId": 123456},
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    q=search_query,
                    product_filter_type=ProductFilterTypeEnum.ALLOCINE_ID.name,
                )
            )
            assert response.status_code == 303

        expected_url = url_for("backoffice_web.product.get_product_details", product_id=product.id)
        assert response.location == expected_url

    def test_search_by_allocine_id_unexisting_product(self, authenticated_client):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    q="123456",
                    product_filter_type=ProductFilterTypeEnum.ALLOCINE_ID.name,
                )
            )

        assert response.status_code == 200
        assert "Le produit est introuvable" in html_parser.content_as_text(response.data)


class ImportProductFromTiteliveButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS
    button_label = "Importer ce produit dans la base de données du pass Culture"

    @property
    def path(self):
        return url_for(
            "backoffice_web.product.search_product",
            q="9782070455379",
            product_filter_type=ProductFilterTypeEnum.EAN.name,
        )

    def test_button_when_can_add_one(self, authenticated_client):
        with patch(
            "pcapi.routes.backoffice.products.blueprint.get_by_ean13", return_value=fixtures.BOOK_BY_SINGLE_EAN_FIXTURE
        ):
            super().test_button_when_can_add_one(authenticated_client)

    def test_no_button(self, client, roles_with_permissions):
        with patch(
            "pcapi.routes.backoffice.products.blueprint.get_by_ean13", return_value=fixtures.BOOK_BY_SINGLE_EAN_FIXTURE
        ):
            super().test_no_button(client, roles_with_permissions)


class GetImportProductFromTiteliveFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.product.get_import_product_from_titelive_form"
    endpoint_kwargs = {"ean": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    # session
    expected_num_queries = 1

    def test_confirm_import_eligible_product_from_titelive_form(self, authenticated_client):
        url = url_for(self.endpoint, ean="1234567899999", is_ineligible=False, _external=True)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert "Voulez-vous importer ce produit" in response_text
        assert "Commentaire interne" not in response_text

        buttons = html_parser.extract(response.data, "button")
        assert "Annuler" in buttons
        assert "Importer" in buttons

    def test_confirm_import_uneligible_product_from_titelive_form(self, authenticated_client):
        url = url_for(self.endpoint, ean="1234567899999", is_ineligible=True, _external=True)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert "Voulez-vous importer ce produit" in response_text
        assert "Commentaire interne" in response_text

        buttons = html_parser.extract(response.data, "button")
        assert "Annuler" in buttons
        assert "Importer" in buttons


class PostImportProductFromTiteliveTest(PostEndpointHelper):
    endpoint = "backoffice_web.product.import_product_from_titelive"
    endpoint_kwargs = {"ean": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    @patch("pcapi.connectors.titelive.get_by_ean13")
    def test_import_eligible_product_from_titelive(self, mock_get_by_ean13, requests_mock, authenticated_client):
        image_path = pathlib.Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(image_path, "rb") as thumb_file:
            requests_mock.get(re.compile("image"), content=thumb_file.read())

        mock_get_by_ean13.return_value = fixtures.BOOK_BY_SINGLE_EAN_FIXTURE
        oeuvre = fixtures.BOOK_BY_SINGLE_EAN_FIXTURE["oeuvre"]
        article = oeuvre["article"][0]

        ean = "1234567899990"
        response = self.post_to_endpoint(authenticated_client, ean=ean, is_ineligible=False)
        assert response.status_code == 303

        product = db.session.query(offer_models.Product).one_or_none()
        assert product
        assert product.name == oeuvre["titre"]
        assert product.description == article["resume"]
        assert product.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert product.thumbCount == int(article.get("image", 0))
        assert product.extraData == {
            "rayon": "Littérature française Récits, Aventures, Voyages",
            "author": "Jean-Christophe Rufin",
            "csr_id": "0105",
            "gtl_id": "01050000",
            "editeur": "FOLIO",
            "code_clil": "3665",
            "collection": "Folio",
            "prix_livre": 8.3,
            "schoolbook": False,
            "comic_series": "Non précisée",
            "distributeur": "SODIS",
            "date_parution": "2014-10-02 00:00:00",
            "num_in_collection": "5833",
        }
        assert product.gcuCompatibilityType == offer_models.GcuCompatibilityType.COMPATIBLE
        assert len(product.productMediations) == 2

        whitelist_product = db.session.query(fraud_models.ProductWhitelist).filter_by(ean=ean).one_or_none()
        assert not whitelist_product

        expected_url = url_for("backoffice_web.product.get_product_details", product_id=product.id)
        assert response.location == expected_url

        redirection = authenticated_client.get(response.location)
        assert f"Le produit {product.name} a été créé" in html_parser.extract_alerts(redirection.data)

    @patch("pcapi.connectors.titelive.get_by_ean13")
    def test_import_uneligible_product_from_titelive(self, mock_get_by_ean13, requests_mock, authenticated_client):
        image_path = pathlib.Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(image_path, "rb") as thumb_file:
            requests_mock.get(re.compile("image"), content=thumb_file.read())

        mock_get_by_ean13.return_value = fixtures.BOOK_BY_SINGLE_EAN_FIXTURE
        oeuvre = fixtures.BOOK_BY_SINGLE_EAN_FIXTURE["oeuvre"]
        article = oeuvre["article"][0]

        ean = "1234567899991"
        response = self.post_to_endpoint(
            authenticated_client,
            ean=ean,
            is_ineligible=True,
            form={
                "comment": "Ce produit doit etre eligible",
            },
        )
        assert response.status_code == 303

        product = db.session.query(offer_models.Product).one_or_none()
        assert product
        assert product.name == oeuvre["titre"]
        assert product.description == article["resume"]
        assert product.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert product.thumbCount == int(article.get("image", 0))
        assert product.extraData == {
            "rayon": "Littérature française Récits, Aventures, Voyages",
            "author": "Jean-Christophe Rufin",
            "csr_id": "0105",
            "gtl_id": "01050000",
            "editeur": "FOLIO",
            "code_clil": "3665",
            "collection": "Folio",
            "prix_livre": 8.3,
            "schoolbook": False,
            "comic_series": "Non précisée",
            "distributeur": "SODIS",
            "date_parution": "2014-10-02 00:00:00",
            "num_in_collection": "5833",
        }
        assert product.gcuCompatibilityType == offer_models.GcuCompatibilityType.COMPATIBLE
        assert len(product.productMediations) == 2

        whitelist_product = db.session.query(fraud_models.ProductWhitelist).filter_by(ean=ean).one_or_none()
        assert whitelist_product

        expected_url = url_for("backoffice_web.product.get_product_details", product_id=product.id)
        assert response.location == expected_url

        redirection = authenticated_client.get(response.location)
        assert f"Le produit {product.name} a été créé" in html_parser.extract_alerts(redirection.data)

    @pytest.mark.parametrize(
        "whitelist_product_raise, alert_message",
        [
            (offers_exceptions.TiteLiveAPINotExistingEAN, "L'EAN 1234567899999 n'existe pas chez Titelive"),
            (GtlIdError, "L'EAN 1234567899999 n'a pas de GTL ID chez Titelive"),
        ],
    )
    @patch("pcapi.connectors.titelive.get_by_ean13")
    def test_fail_import_eligible_product_from_titelive(
        self, mock_get_by_ean13, whitelist_product_raise, alert_message, authenticated_client
    ):
        mock_get_by_ean13.side_effect = whitelist_product_raise

        ean = "1234567899999"
        response = self.post_to_endpoint(authenticated_client, ean=ean, is_ineligible=False)
        assert response.status_code == 303

        expected_url = url_for("backoffice_web.product.search_product")
        assert response.location == expected_url

        redirection = authenticated_client.get(response.location)
        assert alert_message in html_parser.extract_alerts(redirection.data)
