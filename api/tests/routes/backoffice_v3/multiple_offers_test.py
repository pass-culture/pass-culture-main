from flask import url_for
import pytest

from pcapi.core.categories import subcategories
from pcapi.core.offers import factories as offers_factories
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_num_queries

from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class MultipleOffersHomeTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.multiple_offers.multiple_offers_home"
    needed_permission = perm_models.Permissions.MULTIPLE_OFFERS_ACTIONS

    def test_get_search_form(self, authenticated_client):
        with assert_num_queries(2):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200


class SearchMultipleOffersTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.multiple_offers.search_multiple_offers"
    needed_permission = perm_models.Permissions.MULTIPLE_OFFERS_ACTIONS

    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch product and offers with joinedload including extra data (1 query)
    expected_num_queries = 3

    def test_search_product_from_isbn(self, authenticated_client):
        offers_factories.ThingOfferFactory(
            product__extraData={"isbn": "9783161484100"}, product__subcategoryId=subcategories.LIVRE_PAPIER.id
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, isbn="978-3-16-148410-0"))
            assert response.status_code == 200

        (left_card, _) = html_parser.extract_cards_text(response.data)

        assert "Titre du produit : Product 0 " in left_card
        assert "Catégorie : Livre " in left_card
        assert "Nombre d'offres associées : 1 " in left_card
        assert "Approuvées actives : 1 " in left_card
        assert "Approuvées inactives : 0 " in left_card
        assert "En attente : 0 " in left_card
        assert "Rejetées : 0 " in left_card
        assert "compatible avec les CGU : Oui" in left_card
        assert "ISBN : 9783161484100 " in left_card

    def test_search_product_from_isbn_with_offers_and_tags(self, authenticated_client):
        # TODO many offers with tags
        pass

    def test_search_product_from_isbn_with_invalid_isbn(self, authenticated_client):
        with assert_num_queries(self.expected_num_queries - 1):
            response = authenticated_client.get(url_for(self.endpoint, isbn="978-3-16-14840-0"))
            assert response.status_code == 400

        assert "La recherche ne correspond pas au format d'un ISBN" in html_parser.extract_alert(response.data)


class AddCriteriaToOffers(PostEndpointHelper):
    endpoint = "backoffice_v3_web.multiple_offers.add_criteria_to_offers"
    endpoint_kwargs = {"isbn": "9781234567890"}
    needed_permission = perm_models.Permissions.MULTIPLE_OFFERS_ACTIONS

    def test_post(self, authenticated_client):
        pass


class SetProductGcuIncompatibleTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.multiple_offers.set_product_gcu_incompatible"
    endpoint_kwargs = {"isbn": "9781234567890"}
    needed_permission = perm_models.Permissions.FRAUD_ACTIONS

    def test_post(self, authenticated_client):
        pass

    #
    # @patch("pcapi.core.search.async_index_offer_ids")
    # @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    # def test_edit_product_offers_criteria_from_isbn(
    #     self, mocked_validate_csrf_token, mocked_async_index_offer_ids, app
    # ):
    #     # Given
    #     users_factories.AdminFactory(email="admin@example.com")
    #     product = offers_factories.ProductFactory(extraData={"isbn": "9783161484100"})
    #     offer1 = offers_factories.OfferFactory(product=product, extraData={"isbn": "9783161484100"})
    #     offer2 = offers_factories.OfferFactory(product=product, extraData={"isbn": "9783161484100"})
    #     inactive_offer = offers_factories.OfferFactory(
    #         product=product, extraData={"isbn": "9783161484100"}, isActive=False
    #     )
    #     unmatched_offer = offers_factories.OfferFactory()
    #     criterion1 = criteria_factories.CriterionFactory(name="Pretty good books")
    #     criterion2 = criteria_factories.CriterionFactory(name="Other pretty good books")
    #
    #     data = dict(
    #         criteria=[criterion1.id, criterion2.id],
    #     )
    #
    #     # When
    #     client = TestClient(app.test_client()).with_session_auth("admin@example.com")
    #     response = client.post(
    #         "/pc/back-office/many_offers_operations/add_criteria_to_offers?isbn=9783161484100", form=data
    #     )
    #
    #     # Then
    #     assert response.status_code == 302
    #     assert response.headers["location"] == "http://localhost/pc/back-office/many_offers_operations/"
    #     assert offer1.criteria == [criterion1, criterion2]
    #     assert offer2.criteria == [criterion1, criterion2]
    #     assert not inactive_offer.criteria
    #     assert not unmatched_offer.criteria
    #     mocked_async_index_offer_ids.assert_called_once_with([offer1.id, offer2.id])
    #

    # @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    # def test_edit_product_offers_criteria_from_isbn_without_offers(self, mocked_validate_csrf_token, app):
    #     # Given
    #     users_factories.AdminFactory(email="admin@example.com")
    #
    #     # When
    #     client = TestClient(app.test_client()).with_session_auth("admin@example.com")
    #     response = client.get("/pc/back-office/many_offers_operations/edit?isbn=9783161484100")
    #
    #     # Then
    #     assert response.status_code == 302
    #     assert response.headers["location"] == "http://localhost/pc/back-office/many_offers_operations/"
    #
    #
    # def test_get_current_criteria_on_active_offers(self):
    #     # Given
    #     criterion1 = criteria_models.Criterion(name="One criterion")
    #     criterion2 = criteria_models.Criterion(name="Another criterion")
    #     offer1 = Offer(criteria=[criterion1], isActive=True)
    #     offer2 = Offer(criteria=[criterion1, criterion2], isActive=True)
    #     offer3 = Offer(criteria=[], isActive=True)
    #     offer4 = Offer(criteria=[criterion1, criterion2], isActive=False)
    #     expected_result = {
    #         "One criterion": {"count": 2, "criterion": criterion1},
    #         "Another criterion": {"count": 1, "criterion": criterion2},
    #     }
    #
    #     # When
    #     result = _get_current_criteria_on_active_offers([offer1, offer2, offer3, offer4])
    #
    #     # Then
    #     assert result == expected_result
    #
    # @pytest.mark.parametrize(
    #     "validation_status",
    #     [
    #         OfferValidationStatus.DRAFT,
    #         OfferValidationStatus.PENDING,
    #         OfferValidationStatus.REJECTED,
    #         OfferValidationStatus.APPROVED,
    #     ],
    # )
    # @patch("pcapi.core.search.async_index_offer_ids")
    # @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    # def test_edit_product_gcu_compatibility(
    #     self, mocked_validate_csrf_token, mocked_async_index_offer_ids, app, db_session, validation_status
    # ):
    #     # Given
    #     users_factories.AdminFactory(email="admin@example.com")
    #     offerer = offerers_factories.OffererFactory()
    #     product_1 = offers_factories.ThingProductFactory(
    #         description="premier produit inapproprié",
    #         extraData={"isbn": "isbn-de-test"},
    #         isGcuCompatible=not validation_status == OfferValidationStatus.REJECTED,
    #     )
    #     venue = offerers_factories.VenueFactory(managingOfferer=offerer)
    #     offers_factories.OfferFactory(product=product_1, venue=venue, validation=validation_status)
    #     offers_factories.OfferFactory(product=product_1, venue=venue)
    #
    #     initially_rejected = {
    #         offer.id: {"type": offer.lastValidationType, "date": offer.lastValidationDate}
    #         for offer in Offer.query.filter(Offer.validation == OfferValidationStatus.REJECTED)
    #     }
    #
    #     # When
    #     client = TestClient(app.test_client()).with_session_auth("admin@example.com")
    #     response = client.post("/pc/back-office/many_offers_operations/product_gcu_compatibility?isbn=isbn-de-test")
    #
    #     # Then
    #     assert response.status_code == 302
    #     assert response.headers["location"] == "http://localhost/pc/back-office/many_offers_operations/"
    #     products = offers_models.Product.query.all()
    #     offers = Offer.query.order_by("id").all()
    #     first_product = products[0]
    #
    #     assert not first_product.isGcuCompatible
    #     for offer in offers:
    #         assert offer.validation == offers_models.OfferValidationStatus.REJECTED
    #         if offer.id in initially_rejected:
    #             assert offer.lastValidationType == initially_rejected[offer.id]["type"]
    #             assert offer.lastValidationDate == initially_rejected[offer.id]["date"]
    #         else:
    #             assert offer.lastValidationType == OfferValidationType.CGU_INCOMPATIBLE_PRODUCT
    #             assert datetime.utcnow() - offer.lastValidationDate < timedelta(seconds=5)
    #     mocked_async_index_offer_ids.assert_called_once_with(
    #         [offer.id for offer in offers if offer.id not in initially_rejected]
    #     )
    #
    # def test_get_products_compatible_status(self):
    #     # Given
    #     products = []
    #     products.append(offers_models.Product(isGcuCompatible=True))
    #     products.append(offers_models.Product(isGcuCompatible=True))
    #
    #     # Then
    #     assert _get_products_compatible_status(products) == {
    #         "status": "compatible_products",
    #         "text": "Oui",
    #     }
    #
    #     products[0].isGcuCompatible = False
    #     assert _get_products_compatible_status(products) == {
    #         "status": "partially_incompatible_products",
    #         "text": "Partiellement",
    #     }
    #
    #     products[1].isGcuCompatible = False
    #     assert _get_products_compatible_status(products) == {
    #         "status": "incompatible_products",
    #         "text": "Non",
    #     }
