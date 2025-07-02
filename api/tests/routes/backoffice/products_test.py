from unittest.mock import patch

import pytest
from flask import url_for

from pcapi.core.categories import subcategories
from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.models.offer_mixin import OfferStatus
from pcapi.routes.backoffice.filters import format_titelive_id_lectorat
from pcapi.utils import requests

from tests.connectors.titelive import fixtures

from .helpers import button as button_helpers
from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class GetProductDetailsTest(GetEndpointHelper):
    endpoint = "backoffice_web.product.get_product_details"
    endpoint_kwargs = {"product_id": 1}
    needed_permission = perm_models.Permissions.READ_OFFERS

    # Expected SQL queries:
    # 1) Session
    # 2) User

    # Product and related data
    # 3) Product
    # 4) ProductMediation (via selectinload)

    # Linked offers and stock
    # 5) Linked Offer
    # 6) Linked Offer -> Criteria (via selectinload)
    # 7) Linked Offer -> Stock (via selectinload)

    # Unlinked offers and stock
    # 8) Unlinked Offer
    # 9) Unlinked Offer -> Criteria (via selectinload)
    # 10) Unlinked Offer -> Stock (via selectinload)

    # Whitelist
    # 11) Whitelisted Product
    expected_num_queries = 11

    expected_num_queries += 1  # FF WIP_REFACTO_FUTURE_OFFER

    @patch("pcapi.routes.backoffice.products.blueprint.get_by_ean13")
    def test_get_detail_product(self, mock_get_by_ean13, authenticated_client):
        article = fixtures.BOOK_BY_SINGLE_EAN_FIXTURE["oeuvre"]["article"][0]
        mock_get_by_ean13.return_value = fixtures.BOOK_BY_SINGLE_EAN_FIXTURE

        allocine_provider = providers_factories.AllocineProviderFactory.create(isActive=True)
        product = offers_factories.ProductFactory.create(
            description="Une offre pour tester",
            ean="1234567891234",
            extraData={"author": "Jean-Christophe Rufin", "editeur": "Editor", "gtl_id": "08010000"},
            lastProvider=allocine_provider,
        )

        criteria = criteria_factories.CriterionFactory.create()
        linked_offer = offers_factories.OfferFactory.create(product=product, ean="1234567891234", criteria=[criteria])

        # offre non liées au produit
        unlinked_offer = offers_factories.OfferFactory.create(ean="1234567891234")

        url = url_for(self.endpoint, product_id=product.id, _external=True)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        descriptions = html_parser.extract_descriptions(response.data)
        assert str(product.id) == descriptions["Product ID"]

        assert descriptions["Catégorie"] == "Livre"
        assert descriptions["Sous-catégorie"] == "Livre papier"
        assert descriptions["Nombre d'offres"] == "2"
        assert descriptions["Nombre d'offres associées"] == "1"
        assert descriptions["Nombre d'offres non liées"] == "1"
        assert descriptions["Approuvées actives"] == "2"
        assert descriptions["Approuvées inactives"] == "0"
        assert descriptions["En attente"] == "0"
        assert descriptions["Rejetées"] == "0"
        assert descriptions["Tags des offres"] == f"1/2 offre active a déjà le tag {criteria.name}"
        assert descriptions["Auteur"] == "Jean-Christophe Rufin"
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
        assert "EAN-13 " + fixtures.BOOK_BY_SINGLE_EAN_FIXTURE["ean"] in card_text[0]
        assert "Lectorat " + format_titelive_id_lectorat(article["id_lectorat"]) in card_text[0]

        assert "Prix HT 8,30 €" in card_text[0]
        assert "Taux TVA 5,50 %" in card_text[0]
        assert "Code CLIL " + article["code_clil"] in card_text[0]
        assert "Code support " + article["libellesupport"] + " (" + article["codesupport"] + ")" in card_text[0]
        assert "Code GTL Littérature (01000000) Rayon (CSR): Littérature française (0100)" in card_text[0]
        assert "Récit (01050000) Rayon (CSR): Littérature française Récits, Aventures, Voyages (0105)" in card_text[0]
        assert "Inéligible pass Culture " not in card_text[0]
        assert "EAN whitelisté Non" in card_text[0]

        buttons = html_parser.extract(response.data, "button")
        assert "Offres liées" in buttons
        assert "Offres non liées" in buttons

        badges = html_parser.extract_badges(response.data)
        assert "• Compatible" in badges

        product_offer = html_parser.extract_table_rows(response.data, table_id="offers-table")
        assert product_offer[0]["ID"] == str(linked_offer.id)
        assert product_offer[0]["Nom"] == linked_offer.name
        assert product_offer[0]["Statut"] == "Épuisée"

        product_unlinked_offer = html_parser.extract_table_rows(response.data, table_id="unlinked-offers-table")
        assert product_unlinked_offer[0]["ID"] == str(unlinked_offer.id)
        assert product_unlinked_offer[0]["Nom"] == unlinked_offer.name
        assert product_unlinked_offer[0]["Statut"] == "Épuisée"

    @pytest.mark.parametrize(
        "subcategory_id",
        (
            subcategories.LIVRE_PAPIER.id,
            subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
            subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
        ),
    )
    @patch("pcapi.routes.backoffice.products.blueprint.get_by_ean13")
    def test_get_detail_product_display_music_type_only_for_music_support(
        self, mock_get_by_ean13, subcategory_id, authenticated_client
    ):
        product = offers_factories.ProductFactory(
            subcategoryId=subcategory_id,
            extraData={"gtl_id": "08010000"},
        )

        url = url_for(self.endpoint, product_id=product.id, _external=True)
        # The following 5 queries are not executed in this case:
        # 1) No Criteria associated with the linked Offer
        # 2) No Stock associated with the linked Offer
        # 3) No Criteria associated with the Unlinked Offer
        # 4) No Stock associated with Unlinked Offer
        # 5) No FF WIP_REFACTO_FUTURE_OFFER
        with assert_num_queries(self.expected_num_queries - 5):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        descriptions = html_parser.extract_descriptions(response.data)
        if subcategory_id in (
            subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
            subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
        ):
            assert descriptions["Type de musique"] == "Alternatif"
        else:
            assert "Type de musique" not in descriptions

    @patch("pcapi.routes.backoffice.products.blueprint.get_by_ean13")
    def test_get_detail_product_without_ean(self, mock_get_by_ean13, authenticated_client):
        product = offers_factories.ProductFactory.create(subcategoryId=subcategories.SEANCE_CINE.id)

        url = url_for(self.endpoint, product_id=product.id, _external=True)
        # The following 7 queries are not executed in this case:
        # 1) No Stock associated with the linked Offer
        # 2) No Criteria associated with the linked Offer
        # 3) No Unlinked Offer
        # 4) No Stock associated with Unlinked Offer
        # 5) No Criteria associated with the Unlinked Offer
        # 6) No Whitelisted Product (missing EAN)
        # 7) No FF WIP_REFACTO_FUTURE_OFFER
        with assert_num_queries(self.expected_num_queries - 7):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        soup = html_parser.get_soup(response.data)
        card_ean = soup.find(id="titelive-data")
        assert not card_ean

        mock_get_by_ean13.assert_not_called()

    @pytest.mark.parametrize(
        "titelive_error",
        (offers_exceptions.TiteLiveAPINotExistingEAN, requests.exceptions.Timeout, requests.ExternalAPIException),
    )
    @patch("pcapi.routes.backoffice.products.blueprint.get_by_ean13")
    def test_get_detail_product_titelive_api_raise_error(self, mock_get_by_ean13, titelive_error, authenticated_client):
        mock_get_by_ean13.side_effect = titelive_error
        product = offers_factories.ProductFactory.create(
            description="Une offre pour tester",
            ean="1234567891234",
            extraData={"author": "Jean-Christophe Rufin", "editeur": "Editor", "gtl_id": "08010000"},
        )
        offers_factories.OfferFactory.create(product=product, ean="1234567891234")
        offers_factories.OfferFactory.create(ean="1234567891234")

        url = url_for(self.endpoint, product_id=product.id, _external=True)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        if titelive_error != offers_exceptions.TiteLiveAPINotExistingEAN:
            error_instance = (
                titelive_error(is_retryable=True)
                if titelive_error == requests.ExternalAPIException
                else titelive_error()
            )
            assert (
                f"Une erreur s’est produite lors de la récupération des informations via l’API Titelive: {error_instance.__class__.__name__}"
                in html_parser.extract_alert(response.data)
            )


class ProductSynchronizationWithTiteliveButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS
    button_label = "Synchronisation Titelive"

    @property
    def path(self):
        product = offers_factories.ProductFactory.create()
        return url_for("backoffice_web.product.get_product_details", product_id=product.id)

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


class GetProductSynchronizationWithTiteliveFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.product.get_product_synchronize_with_titelive_form"
    endpoint_kwargs = {"product_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    # session + user + product
    expected_num_queries = 3

    @patch("pcapi.routes.backoffice.products.blueprint.get_by_ean13")
    def test_confirm_product_synchronization_with_titelive_form(self, mock_get_by_ean13, authenticated_client):
        article = fixtures.BOOK_BY_SINGLE_EAN_FIXTURE["oeuvre"]["article"][0]
        mock_get_by_ean13.return_value = fixtures.BOOK_BY_SINGLE_EAN_FIXTURE

        product = offers_factories.ProductFactory.create()

        url = url_for(self.endpoint, product_id=product.id, _external=True)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        soup = html_parser.get_soup(response.data)
        card_titles = html_parser.extract_cards_titles(response.data)
        card_text = html_parser.extract_cards_text(response.data)
        card_ean = soup.select("div.pc-ean-result")

        assert card_ean
        assert fixtures.BOOK_BY_SINGLE_EAN_FIXTURE["oeuvre"]["titre"] in card_titles[0]
        assert soup.select(
            f'div.pc-ean-result img[src="{fixtures.BOOK_BY_SINGLE_EAN_FIXTURE["oeuvre"]["article"][0]["imagesUrl"]["recto"]}"]'
        )
        assert fixtures.BOOK_BY_SINGLE_EAN_FIXTURE["oeuvre"]["titre"] in card_text[0]
        assert "EAN-13 " + fixtures.BOOK_BY_SINGLE_EAN_FIXTURE["ean"] in card_text[0]
        assert "Lectorat " + format_titelive_id_lectorat(article["id_lectorat"]) in card_text[0]

        assert "Prix HT 8,30 €" in card_text[0]
        assert "Taux TVA 5,50 %" in card_text[0]
        assert "Code CLIL " + article["code_clil"] in card_text[0]
        assert "Code support " + article["libellesupport"] + " (" + article["codesupport"] + ")" in card_text[0]
        assert "Code GTL Littérature (01000000) Rayon (CSR): Littérature française (0100)" in card_text[0]
        assert "Récit (01050000) Rayon (CSR): Littérature française Récits, Aventures, Voyages (0105)" in card_text[0]
        assert "Inéligible pass Culture " not in card_text[0]
        assert "EAN whitelisté Non" in card_text[0]

        buttons = html_parser.extract(response.data, "button")
        assert "Annuler" in buttons
        assert "Mettre le produit à jour avec ces informations" in buttons

    @patch("pcapi.routes.backoffice.products.blueprint.get_by_ean13")
    def test_confirm_product_synchronization_fails_to_retrieve_titelive_data_form(
        self, mock_get_by_ean13, authenticated_client
    ):
        mock_get_by_ean13.side_effect = requests.ExternalAPIException(is_retryable=True)

        product = offers_factories.ProductFactory.create()

        url = url_for(self.endpoint, product_id=product.id, _external=True)
        with assert_num_queries(self.expected_num_queries + 1):  # +1 for ROLLBACK
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert (
            "Une erreur s’est produite lors de la récupération des informations via l’API Titelive: ExternalAPIException"
            in html_parser.extract_alert(response.data)
        )


class PostProductSynchronizationWithTiteliveTest(PostEndpointHelper):
    endpoint = "backoffice_web.product.synchronize_product_with_titelive"
    endpoint_kwargs = {"product_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    @patch("pcapi.connectors.titelive.get_by_ean13")
    def test_whitelist_product(self, mock_get_by_ean13, authenticated_client):
        mock_get_by_ean13.return_value = fixtures.BOOK_BY_SINGLE_EAN_FIXTURE
        article = fixtures.BOOK_BY_SINGLE_EAN_FIXTURE["oeuvre"]["article"][0]
        oeuvre = fixtures.BOOK_BY_SINGLE_EAN_FIXTURE["oeuvre"]

        ean = "1234567899999"
        product = offers_factories.ProductFactory.create(ean=ean, extraData={})
        response = self.post_to_endpoint(authenticated_client, product_id=product.id)
        assert response.status_code == 303

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


class WhitelistProductButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS
    button_label = "Whitelist"

    @property
    def path(self):
        product = offers_factories.ProductFactory.create(
            gcuCompatibilityType=offers_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE
        )
        return url_for("backoffice_web.product.get_product_details", product_id=product.id)


class GetProductWhitelistConfirmationFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.product.get_product_whitelist_form"
    endpoint_kwargs = {"product_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    # session + user + product
    expected_num_queries = 3

    def test_confirm_product_whitelist_form(self, authenticated_client):
        product = offers_factories.ProductFactory.create(name="One Piece")

        url = url_for(self.endpoint, product_id=product.id, _external=True)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert f"Whitelister le produit {product.name}" in response_text

        buttons = html_parser.extract(response.data, "button")
        assert "Annuler" in buttons
        assert "Whitelister le produit" in buttons


class PostProductWhitelistTest(PostEndpointHelper):
    endpoint = "backoffice_web.product.whitelist_product"
    endpoint_kwargs = {"product_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_whitelist_product(self, authenticated_client):
        ean = "1234567899999"
        product = offers_factories.ProductFactory.create(
            ean=ean,
            gcuCompatibilityType=offers_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE,
        )

        response = self.post_to_endpoint(authenticated_client, product_id=product.id, follow_redirects=True)

        assert response.status_code == 200
        assert "Le produit a été marqué compatible avec les CGU" in html_parser.extract_alerts(response.data)
        assert product.gcuCompatibilityType == offers_models.GcuCompatibilityType.COMPATIBLE


class BlacklistProductButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS
    button_label = "Blacklist"

    @property
    def path(self):
        product = offers_factories.ProductFactory.create(
            gcuCompatibilityType=offers_models.GcuCompatibilityType.COMPATIBLE
        )
        return url_for("backoffice_web.product.get_product_details", product_id=product.id)


class GetProductBlacklistConfirmationFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.product.get_product_blacklist_form"
    endpoint_kwargs = {"product_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    # session + user + product
    expected_num_queries = 3

    def test_confirm_product_blacklist_form(self, authenticated_client):
        product = offers_factories.ProductFactory.create(name="One Piece")

        url = url_for(self.endpoint, product_id=product.id, _external=True)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert f"Blacklister le produit {product.name}" in response_text

        buttons = html_parser.extract(response.data, "button")
        assert "Annuler" in buttons
        assert "Blacklister le produit" in buttons


class PostProductBlacklistTest(PostEndpointHelper):
    endpoint = "backoffice_web.product.blacklist_product"
    endpoint_kwargs = {"product_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_blacklist_product(self, authenticated_client):
        ean = "1234567899999"
        product = offers_factories.ProductFactory.create(
            ean=ean, gcuCompatibilityType=offers_models.GcuCompatibilityType.COMPATIBLE
        )
        offer = offers_factories.OfferFactory.create(product=product)
        offers_factories.StockFactory.create(offer=offer, price=10)

        unlinked_offer = offers_factories.OfferFactory.create(ean=ean)
        offers_factories.StockFactory.create(offer=unlinked_offer, price=10)

        response = self.post_to_endpoint(authenticated_client, product_id=product.id, follow_redirects=True)

        assert response.status_code == 200
        assert (
            "Le produit a été marqué incompatible avec les CGU et les offres ont été désactivées"
            in html_parser.extract_alerts(response.data)
        )
        assert product.gcuCompatibilityType == offers_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE
        assert offer.status == OfferStatus.REJECTED
        assert unlinked_offer.status == OfferStatus.REJECTED


class LinkUnlinkedOfferToProductButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS
    button_label = "Associer les offres au produit"

    @property
    def path(self):
        ean = "1234567899999"
        product = offers_factories.ProductFactory.create(ean=ean)
        offers_factories.OfferFactory.create(ean=ean)
        return url_for("backoffice_web.product.get_product_details", product_id=product.id)


class GetProductLinkOfferFormTest(PostEndpointHelper):
    endpoint = "backoffice_web.product.confirm_link_offers_forms"
    endpoint_kwargs = {"product_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    @pytest.mark.parametrize(
        "identifier_props, offers_count",
        [
            ({"ean": "1234567891234"}, 10),
            ({"extraData": {"visa": "123456"}}, 5),
            ({"extraData": {"allocineId": 98765}}, 3),
        ],
    )
    def test_confirm_product_link_offers_form(self, authenticated_client, identifier_props, offers_count):
        product = offers_factories.ProductFactory.create(**identifier_props)
        unlinked_offers = offers_factories.OfferFactory.create_batch(offers_count, **identifier_props)

        response = self.post_to_endpoint(
            authenticated_client,
            product_id=product.id,
            form={"object_ids": ",".join([str(offer.id) for offer in unlinked_offers])},
        )
        assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert f"Voulez-vous associer {offers_count} offre" in response_text


class LinkUnlinkedOfferToProductTest(PostEndpointHelper):
    endpoint = "backoffice_web.product.batch_link_offers_to_product"
    endpoint_kwargs = {"product_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    @pytest.mark.parametrize(
        "identifier_props, offers_count",
        [
            ({"ean": "1234567891234"}, 10),
            ({"extraData": {"visa": "123456"}}, 5),
            ({"extraData": {"allocineId": 98765}}, 3),
        ],
    )
    def test_link_offers_to_product(self, authenticated_client, identifier_props, offers_count):
        product = offers_factories.ProductFactory.create(**identifier_props)
        unlinked_offers = offers_factories.OfferFactory.create_batch(offers_count, **identifier_props)

        response = self.post_to_endpoint(
            authenticated_client,
            product_id=product.id,
            form={"object_ids": ",".join([str(offer.id) for offer in unlinked_offers])},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert "Les offres ont été associées au produit avec succès" in html_parser.extract_alerts(response.data)
        assert len(product.offers) == len(unlinked_offers)
        assert len(product.offers) == offers_count


class TagOffersButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.MULTIPLE_OFFERS_ACTIONS
    button_label = "Tag les offres"

    @property
    def path(self):
        ean = "1234567890123"
        product = offers_factories.ProductFactory.create(ean=ean)
        offers_factories.OfferFactory.create(product=product)
        return url_for("backoffice_web.product.get_product_details", product_id=product.id)


class GetTagOffersFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.product.get_tag_offers_form"
    endpoint_kwargs = {"product_id": 1}
    needed_permission = perm_models.Permissions.MULTIPLE_OFFERS_ACTIONS

    # Expected SQL queries:
    # 1. session
    # 2. user
    # 3. product + linked offers
    # 4. unlinked offers
    expected_num_queries = 4

    @pytest.mark.parametrize(
        "identifier_props, identifier_string",
        [
            ({"ean": "1234567891234"}, "cet EAN-13"),
            ({"extraData": {"visa": "123456"}, "ean": None}, "ce visa"),
            ({"extraData": {"allocineId": 98765}, "ean": None}, "cet ID Allociné"),
        ],
    )
    def test_get_tag_offers_form_with_active_offers(self, authenticated_client, identifier_props, identifier_string):
        product = offers_factories.ProductFactory.create(**identifier_props)
        offers_factories.OfferFactory.create_batch(3, product=product, isActive=True)
        offers_factories.OfferFactory.create_batch(4, product=product, isActive=False)
        offers_factories.OfferFactory.create_batch(2, productId=None, isActive=True, **identifier_props)
        offers_factories.OfferFactory.create(productId=None, isActive=False, **identifier_props)

        url = url_for(self.endpoint, product_id=product.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)

        assert response.status_code == 200
        response_text = html_parser.content_as_text(response.data)
        assert "Tag des offres" in response_text

        total_active_offers_count = 5
        expected_message = (
            f"⚠️ {total_active_offers_count} offres actives associées à {identifier_string} seront affectées"
        )
        assert expected_message in response_text

        buttons = html_parser.extract(response.data, "button")
        assert "Annuler" in buttons
        assert "Enregistrer" in buttons


class AddCriteriaToOffersTest(PostEndpointHelper):
    endpoint = "backoffice_web.product.add_criteria_to_offers"
    endpoint_kwargs = {"product_id": 1}
    needed_permission = perm_models.Permissions.MULTIPLE_OFFERS_ACTIONS

    @pytest.mark.parametrize(
        "identifier_props",
        [
            {"ean": "1234567890123"},
            {"extraData": {"visa": "123456"}, "ean": None},
            {"extraData": {"allocineId": 98765}, "ean": None},
        ],
    )
    def test_add_criteria_to_offers_success(self, db_session, authenticated_client, identifier_props):
        product = offers_factories.ProductFactory.create(**identifier_props)
        criterion_to_add = criteria_factories.CriterionFactory()

        linked_offer = offers_factories.OfferFactory.create(product=product, **identifier_props)
        unlinked_offer = offers_factories.OfferFactory.create(**identifier_props)

        unrelated_offer = offers_factories.OfferFactory.create(ean="9999999999999")

        response = self.post_to_endpoint(
            authenticated_client,
            product_id=product.id,
            form={"criteria": [criterion_to_add.id]},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert "Les offres du produit ont été taguées" in html_parser.extract_alerts(response.data)
        assert criterion_to_add in linked_offer.criteria
        assert criterion_to_add in unlinked_offer.criteria
        assert criterion_to_add not in unrelated_offer.criteria
