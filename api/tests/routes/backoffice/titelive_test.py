import datetime
import html
from unittest.mock import patch

import pytest
from flask import url_for

from pcapi import settings
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.factories import ProductWhitelistFactory
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.search.models import IndexationReason
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.models.utils import get_or_404
from pcapi.routes.backoffice.filters import format_titelive_id_lectorat
from pcapi.utils import date as date_utils

from ...connectors.titelive import fixtures
from ...connectors.titelive.fixtures import BOOK_BY_SINGLE_EAN_FIXTURE
from .helpers import button as button_helpers
from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class SearchEanTest(GetEndpointHelper):
    endpoint = "backoffice_web.titelive.search_titelive"
    endpoint_kwargs = {"ean": "9782070455379"}
    needed_permission = perm_models.Permissions.READ_OFFERS

    # session + query
    expected_num_queries = 2

    def test_search_ean_initial(self, authenticated_client):
        with assert_num_queries(self.expected_num_queries - 1):  # no query, only session + user
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        soup = html_parser.get_soup(response.data)
        card_ean = soup.select("div.pc-ean-result")
        assert not card_ean

    @patch("pcapi.routes.backoffice.titelive.blueprint.get_by_ean13")
    def test_search_ean_not_whitelisted(self, mock_get_by_ean13, authenticated_client):
        mock_get_by_ean13.return_value = BOOK_BY_SINGLE_EAN_FIXTURE
        article = BOOK_BY_SINGLE_EAN_FIXTURE["oeuvre"]["article"][0]

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **self.endpoint_kwargs))
            assert response.status_code == 200

        soup = html_parser.get_soup(response.data)
        card_titles = html_parser.extract_cards_titles(response.data)
        card_text = html_parser.extract_cards_text(response.data)

        card_ean = soup.select("div.pc-ean-result")
        assert card_ean
        assert BOOK_BY_SINGLE_EAN_FIXTURE["oeuvre"]["titre"] in card_titles[0]
        assert soup.select(
            f'div.pc-ean-result img[src="{BOOK_BY_SINGLE_EAN_FIXTURE["oeuvre"]["article"][0]["imagesUrl"]["recto"]}"]'
        )
        assert BOOK_BY_SINGLE_EAN_FIXTURE["oeuvre"]["titre"] in card_text[0]
        assert "EAN-13 : " + BOOK_BY_SINGLE_EAN_FIXTURE["ean"] in card_text[0]
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

    @patch("pcapi.routes.backoffice.titelive.blueprint.get_by_ean13")
    def test_search_ean_whitelisted(self, mock_get_by_ean13, authenticated_client):
        ProductWhitelistFactory(
            ean=self.endpoint_kwargs["ean"],
            comment="Superbe livre !",
            author__firstName="Frank",
            author__lastName="Columbo",
        )
        mock_get_by_ean13.return_value = BOOK_BY_SINGLE_EAN_FIXTURE

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **self.endpoint_kwargs))
            assert response.status_code == 200

        card_text = html_parser.extract_cards_text(response.data)
        assert "Inéligible pass Culture :" not in card_text[0]
        assert "EAN white listé : Oui" in card_text[0]
        assert f"Date d'ajout : {date_utils.get_naive_utc_now().strftime('%d/%m/%Y')}" in card_text[0]
        assert "Auteur : Frank Columbo" in card_text[0]
        assert "Commentaire : Superbe livre !" in card_text[0]

    @patch(
        "pcapi.routes.backoffice.titelive.blueprint.get_by_ean13", return_value=fixtures.INELIGIBLE_BOOK_BY_EAN_FIXTURE
    )
    def test_search_ean_with_ineligibility_reasons(self, mock_get_by_ean13, authenticated_client):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **self.endpoint_kwargs))
            assert response.status_code == 200

        card_text = html_parser.extract_cards_text(response.data)
        assert "Inéligible pass Culture : extracurricular" in card_text[0]
        assert "EAN white listé : Non" in card_text[0]


class WhitelistButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS
    button_label = "Ajouter le livre dans la whitelist"

    @property
    def path(self):
        return url_for("backoffice_web.titelive.search_titelive", ean="9782070455379")

    def test_button_when_can_add_one(self, authenticated_client):
        with patch("pcapi.routes.backoffice.titelive.blueprint.get_by_ean13", return_value=BOOK_BY_SINGLE_EAN_FIXTURE):
            super().test_button_when_can_add_one(authenticated_client)

    def test_no_button(self, client, roles_with_permissions):
        with patch("pcapi.routes.backoffice.titelive.blueprint.get_by_ean13", return_value=BOOK_BY_SINGLE_EAN_FIXTURE):
            super().test_no_button(client, roles_with_permissions)


class ProductBlackListFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.titelive.get_add_product_whitelist_confirmation_form"
    endpoint_kwargs = {"ean": "9782070455379", "title": "Immortelle randonnée ; Compostelle malgré moi"}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_get_search_form(self, authenticated_client):
        with assert_num_queries(1):  # session
            response = authenticated_client.get(url_for(self.endpoint, **self.endpoint_kwargs))
            assert response.status_code == 200


class AddProductWhitelistTest(PostEndpointHelper):
    endpoint = "backoffice_web.titelive.add_product_whitelist"
    endpoint_kwargs = {"ean": "9782070455379", "title": "Immortelle randonnée ; Compostelle malgré moi"}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS
    form_data = {"comment": "OK!"}

    @patch("pcapi.core.search.async_index_offer_ids")
    @patch("pcapi.routes.backoffice.titelive.blueprint.get_by_ean13")
    @patch("pcapi.routes.backoffice.titelive.blueprint.offers_api.whitelist_product")
    @pytest.mark.parametrize(
        "form_data",
        [
            form_data,
            {"comment": ""},
        ],
    )
    def test_add_product_with_already_rejected_offers_to_whitelist(
        self, mock_whitelist_product, mock_get_by_ean13, mocked_async_index_offer_ids, authenticated_client, form_data
    ):
        thing_product = offers_factories.ThingProductFactory(
            ean=BOOK_BY_SINGLE_EAN_FIXTURE["ean"],
            description="Tome 1",
            name="Immortelle randonnée ; Compostelle malgré moi",
            subcategoryId="LIVRE_PAPIER",
        )
        mock_get_by_ean13.return_value = BOOK_BY_SINGLE_EAN_FIXTURE
        mock_whitelist_product.return_value = thing_product
        offers_to_restore = [
            offers_factories.ThingOfferFactory(
                idAtProvider=BOOK_BY_SINGLE_EAN_FIXTURE["ean"],
                product=thing_product,
                validation=offers_models.OfferValidationStatus.REJECTED,
                lastValidationType=OfferValidationType.CGU_INCOMPATIBLE_PRODUCT,
                lastValidationDate=datetime.date.today() - datetime.timedelta(days=2),
            ),
            offers_factories.ThingOfferFactory(
                product=thing_product,
                validation=offers_models.OfferValidationStatus.REJECTED,
                lastValidationType=OfferValidationType.CGU_INCOMPATIBLE_PRODUCT,
                lastValidationDate=datetime.date.today() - datetime.timedelta(days=2),
            ),
        ]
        offers_not_to_restore = [
            offers_factories.ThingOfferFactory(
                idAtProvider=BOOK_BY_SINGLE_EAN_FIXTURE["ean"],
                product=thing_product,
                validation=offers_models.OfferValidationStatus.REJECTED,
                lastValidationType=OfferValidationType.AUTO,
                lastValidationDate=datetime.date.today() - datetime.timedelta(days=2),
            ),
            offers_factories.ThingOfferFactory(
                idAtProvider=BOOK_BY_SINGLE_EAN_FIXTURE["ean"],
                product=thing_product,
                validation=offers_models.OfferValidationStatus.PENDING,
                lastValidationType=OfferValidationType.AUTO,
                lastValidationDate=datetime.date.today() - datetime.timedelta(days=2),
            ),
            offers_factories.ThingOfferFactory(
                idAtProvider=BOOK_BY_SINGLE_EAN_FIXTURE["ean"],
                product=thing_product,
                validation=offers_models.OfferValidationStatus.DRAFT,
                lastValidationType=OfferValidationType.CGU_INCOMPATIBLE_PRODUCT,
                lastValidationDate=datetime.date.today() - datetime.timedelta(days=2),
            ),
        ]

        assert (
            not db.session.query(fraud_models.ProductWhitelist)
            .filter(fraud_models.ProductWhitelist.ean == self.endpoint_kwargs["ean"])
            .one_or_none()
        )

        response = self.post_to_endpoint(authenticated_client, form=form_data, **self.endpoint_kwargs)
        assert response.status_code == 303
        response_redirect = authenticated_client.get(response.location)
        alert = html_parser.extract_alert(response_redirect.data)
        product_whitelist = (
            db.session.query(fraud_models.ProductWhitelist)
            .filter(fraud_models.ProductWhitelist.ean == self.endpoint_kwargs["ean"])
            .one()
        )

        assert "a été ajouté dans la whitelist" in alert
        assert product_whitelist.comment == form_data["comment"]
        assert product_whitelist.ean == self.endpoint_kwargs["ean"]
        mock_whitelist_product.assert_called_with(self.endpoint_kwargs["ean"])

        for offer in offers_to_restore:
            offer = get_or_404(offers_models.Offer, offer.id)
            assert offer.validation == offers_models.OfferValidationStatus.APPROVED
            assert offer.lastValidationDate.strftime("%d/%m/%Y") == datetime.date.today().strftime("%d/%m/%Y")
            assert offer.lastValidationType == OfferValidationType.MANUAL

        for offer in offers_not_to_restore:
            offer = get_or_404(offers_models.Offer, offer.id)
            assert not offer.validation == offers_models.OfferValidationStatus.APPROVED
            assert offer.lastValidationDate.strftime("%d/%m/%Y") == (
                datetime.date.today() - datetime.timedelta(days=2)
            ).strftime("%d/%m/%Y")
            assert not offer.lastValidationType == OfferValidationType.MANUAL

        mocked_async_index_offer_ids.assert_called_once_with(
            [o.id for o in offers_to_restore],
            reason=IndexationReason.PRODUCT_WHITELIST_ADDITION,
            log_extra={"ean": "9782070455379"},
        )

    @patch("pcapi.routes.backoffice.titelive.blueprint.get_by_ean13")
    @patch("pcapi.routes.backoffice.titelive.blueprint.offers_api.whitelist_product")
    def test_create_whitelisted_product_if_not_existing(
        self, mock_whitelist_product, mock_get_by_ean13, authenticated_client, requests_mock
    ):
        thing_product = offers_factories.ThingProductFactory(
            ean=BOOK_BY_SINGLE_EAN_FIXTURE["ean"],
            description="Tome 1",
            name="Immortelle randonnée ; Compostelle malgré moi",
            subcategoryId="LIVRE_PAPIER",
        )
        mock_get_by_ean13.return_value = BOOK_BY_SINGLE_EAN_FIXTURE
        mock_whitelist_product.return_value = thing_product
        requests_mock.post(
            f"{settings.TITELIVE_EPAGINE_API_AUTH_URL}/login/test@example.com/token",
            json={"token": "XYZ"},
        )
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/ean/{self.endpoint_kwargs['ean']}",
            json=fixtures.BOOK_BY_SINGLE_EAN_FIXTURE,
        )
        assert (
            not db.session.query(fraud_models.ProductWhitelist)
            .filter(fraud_models.ProductWhitelist.ean == self.endpoint_kwargs["ean"])
            .one_or_none()
        )

        response = self.post_to_endpoint(authenticated_client, form=self.form_data, **self.endpoint_kwargs)
        assert response.status_code == 303
        assert (
            db.session.query(fraud_models.ProductWhitelist)
            .filter(fraud_models.ProductWhitelist.ean == self.endpoint_kwargs["ean"])
            .one()
        )

        response_redirect = authenticated_client.get(response.location)
        alert = html_parser.extract_alert(response_redirect.data)

        assert "a été ajouté dans la whitelist" in alert
        mock_whitelist_product.assert_called_with(self.endpoint_kwargs["ean"])

    @pytest.mark.settings(TITELIVE_EPAGINE_API_USERNAME="test@example.com", TITELIVE_EPAGINE_API_PASSWORD="qwerty123")
    def test_fail_add_product_whitelist_not_existing(self, requests_mock, authenticated_client):
        requests_mock.post(
            f"{settings.TITELIVE_EPAGINE_API_AUTH_URL}/login/test@example.com/token",
            json={"token": "XYZ"},
        )
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/ean/{fixtures.NO_RESULT_BY_EAN_FIXTURE['ean']}",
            json=fixtures.NO_RESULT_BY_EAN_FIXTURE,
            status_code=404,
        )
        response = self.post_to_endpoint(
            authenticated_client,
            form=self.form_data,
            ean=fixtures.NO_RESULT_BY_EAN_FIXTURE["ean"],
            title=self.endpoint_kwargs["title"],
        )
        assert response.status_code == 303
        response_redirect = authenticated_client.get(response.location)
        alert = html_parser.extract_alert(response_redirect.data)

        assert "n'existe pas chez Titelive" in alert

    @pytest.mark.settings(TITELIVE_EPAGINE_API_USERNAME="test@example.com", TITELIVE_EPAGINE_API_PASSWORD="qwerty123")
    def test_fail_no_gtl_id(self, requests_mock, authenticated_client):
        requests_mock.post(
            f"{settings.TITELIVE_EPAGINE_API_AUTH_URL}/login/test@example.com/token",
            json={"token": "XYZ"},
        )
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/ean/{fixtures.NO_GTL_IN_RESULT_FIXTURE['ean']}",
            json=fixtures.NO_GTL_IN_RESULT_FIXTURE,
            status_code=200,
        )
        response = self.post_to_endpoint(
            authenticated_client,
            form=self.form_data,
            ean=fixtures.NO_GTL_IN_RESULT_FIXTURE["ean"],
            title=fixtures.NO_GTL_IN_RESULT_FIXTURE["oeuvre"]["titre"],
        )
        assert response.status_code == 303
        response_redirect = authenticated_client.get(response.location)
        alert = html_parser.extract_alert(response_redirect.data)

        assert alert == "L'EAN 9791030204704 n'a pas de GTL ID chez Titelive"

    @patch("pcapi.core.search.async_index_offer_ids")
    @patch("pcapi.routes.backoffice.titelive.blueprint.get_by_ean13")
    @patch("pcapi.routes.backoffice.titelive.blueprint.offers_api.whitelist_product")
    def test_add_product_to_whitelist_should_set_validation_author(
        self, mock_whitelist_product, mock_get_by_ean13, mocked_async_index_offer_ids, authenticated_client, legit_user
    ):
        thing_product = offers_factories.ThingProductFactory(
            ean=BOOK_BY_SINGLE_EAN_FIXTURE["ean"],
            description="Tome 1",
            name="Immortelle randonnée ; Compostelle malgré moi",
            subcategoryId="LIVRE_PAPIER",
        )
        mock_get_by_ean13.return_value = BOOK_BY_SINGLE_EAN_FIXTURE
        mock_whitelist_product.return_value = thing_product

        offer = offers_factories.ThingOfferFactory(
            idAtProvider=BOOK_BY_SINGLE_EAN_FIXTURE["ean"],
            product=thing_product,
            validation=offers_models.OfferValidationStatus.REJECTED,
            lastValidationType=OfferValidationType.CGU_INCOMPATIBLE_PRODUCT,
            lastValidationDate=datetime.date.today() - datetime.timedelta(days=2),
        )

        self.post_to_endpoint(authenticated_client, form=self.form_data, **self.endpoint_kwargs)

        offer = get_or_404(offers_models.Offer, offer.id)
        assert offer.validation == offers_models.OfferValidationStatus.APPROVED
        assert offer.lastValidationDate.strftime("%d/%m/%Y") == datetime.date.today().strftime("%d/%m/%Y")
        assert offer.lastValidationType == OfferValidationType.MANUAL
        assert offer.lastValidationAuthor == legit_user
        mocked_async_index_offer_ids.assert_called_once_with(
            [offer.id],
            reason=IndexationReason.PRODUCT_WHITELIST_ADDITION,
            log_extra={"ean": "9782070455379"},
        )


class DeleteProductWhitelistTest(GetEndpointHelper):
    endpoint = "backoffice_web.titelive.delete_product_whitelist"
    endpoint_kwargs = {"ean": "9782070455379"}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    @patch("pcapi.routes.backoffice.titelive.blueprint.get_by_ean13")
    def test_remove_product_from_whitelist(self, mock_get_by_ean13, authenticated_client):
        mock_get_by_ean13.return_value = BOOK_BY_SINGLE_EAN_FIXTURE
        ProductWhitelistFactory(ean=self.endpoint_kwargs["ean"])
        response = authenticated_client.get(url_for(self.endpoint, **self.endpoint_kwargs))

        assert response.status_code == 303
        response_redirect = authenticated_client.get(response.location)
        alert = html_parser.extract_alert(response_redirect.data)

        assert "a été supprimé de la whitelist" in alert

    @patch("pcapi.routes.backoffice.titelive.blueprint.get_by_ean13")
    def test_remove_product_whitelist_not_in_whitelist(self, mock_get_by_ean13, authenticated_client):
        mock_get_by_ean13.return_value = BOOK_BY_SINGLE_EAN_FIXTURE
        response = authenticated_client.get(url_for(self.endpoint, **self.endpoint_kwargs))

        assert response.status_code == 303
        response_redirect = authenticated_client.get(response.location)
        alert = html_parser.extract_alert(response_redirect.data)

        assert "n'existe pas dans la whitelist" in alert
