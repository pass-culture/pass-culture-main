import datetime
from unittest.mock import patch

from flask import url_for
import pytest

from pcapi.core.categories import subcategories
import pcapi.core.criteria.factories as criteria_factories
import pcapi.core.criteria.models as criteria_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.core.offers.models import Offer
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.offer_mixin import OfferValidationType

from .helpers import button as button_helpers
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

    def test_search_product_with_offers(self, authenticated_client):
        offers_factories.ThingOfferFactory(
            product__name="Product with EAN",
            product__extraData={"isbn": "9783161484100", "ean": "9783161484100"},
            product__subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, ean="978-3-16-148410-0"))
            assert response.status_code == 200

        cards = html_parser.extract_cards_text(response.data)
        assert len(cards) == 2  # left and right cards when active offers exist
        left_card = cards[0]

        assert "Titre du produit : Product with EAN " in left_card
        assert "Catégorie : Livre " in left_card
        assert "Nombre d'offres associées : 1 " in left_card
        assert "Approuvées actives : 1 " in left_card
        assert "Approuvées inactives : 0 " in left_card
        assert "En attente : 0 " in left_card
        assert "Rejetées : 0 " in left_card
        assert "compatible avec les CGU : Oui" in left_card
        assert "EAN : 9783161484100 " in left_card

    def test_search_product_without_offer(self, authenticated_client):
        offers_factories.ThingProductFactory(
            name="Product without offer",
            extraData={"isbn": "9783161484100", "ean": "9783161484100"},
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, ean="978 3161484100"))
            assert response.status_code == 200

        cards = html_parser.extract_cards_text(response.data)
        assert len(cards) == 1  # no offer => no card about tags
        left_card = cards[0]

        assert "Titre du produit : Product without offer " in left_card
        assert "Catégorie : Livre " in left_card
        assert "Nombre d'offres associées : 0 " in left_card
        assert "Approuvées actives : 0 " in left_card
        assert "Approuvées inactives : 0 " in left_card
        assert "En attente : 0 " in left_card
        assert "Rejetées : 0 " in left_card
        assert "compatible avec les CGU : Oui" in left_card
        assert "EAN : 9783161484100 " in left_card

    @pytest.mark.parametrize(
        "first_compatibility,second_compatibility,expected_cgu_display",
        [
            (True, True, "Oui"),
            (False, False, "Non"),
            (True, False, "Partiellement"),
        ],
    )
    def test_product_compatibility(
        self, authenticated_client, first_compatibility, second_compatibility, expected_cgu_display
    ):
        offers_factories.ThingProductFactory(
            extraData={"isbn": "9781234567890", "ean": "9781234567890"},
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            isGcuCompatible=first_compatibility,
        )
        offers_factories.ThingProductFactory(
            extraData={"isbn": "9781234567890", "ean": "9781234567890"},
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            isGcuCompatible=second_compatibility,
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, ean="9781234567890"))
            assert response.status_code == 200

        left_card = html_parser.extract_cards_text(response.data)[0]

        assert f"compatible avec les CGU : {expected_cgu_display}" in left_card

    def test_get_current_criteria_on_active_offers(self, authenticated_client):
        criterion1 = criteria_models.Criterion(name="One criterion")
        criterion2 = criteria_models.Criterion(name="Another criterion")
        product = offers_factories.ThingProductFactory(extraData={"isbn": "9783161484100", "ean": "9783161484100"})
        offers_factories.ThingOfferFactory(product=product, criteria=[criterion1], isActive=True)
        offers_factories.ThingOfferFactory(product=product, criteria=[criterion1, criterion2], isActive=True)
        offers_factories.ThingOfferFactory(product=product, criteria=[], isActive=True)
        offers_factories.ThingOfferFactory(product=product, criteria=[criterion1, criterion2], isActive=False)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, ean="978-3-16-148410-0"))
            assert response.status_code == 200

        (_, right_card) = html_parser.extract_cards_text(response.data)

        assert "2/3 offres actives ont déjà le tag One criterion " in right_card
        assert "1/3 offre active a déjà le tag Another criterion " in right_card
        assert "Tag des offres ⚠️ 3 offres actives associées à cet ISBN seront affectées" in right_card

    def test_search_product_from_ean_with_invalid_ean(self, authenticated_client):
        with assert_num_queries(2):
            response = authenticated_client.get(url_for(self.endpoint, ean="978-3-16-14840-0"))
            assert response.status_code == 400

        assert "La recherche ne correspond pas au format d'un EAN" in html_parser.extract_alert(response.data)


class AddCriteriaToOffersTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.multiple_offers.add_criteria_to_offers"
    endpoint_kwargs = {"ean": "9781234567890"}
    needed_permission = perm_models.Permissions.MULTIPLE_OFFERS_ACTIONS

    @patch("pcapi.core.search.async_index_offer_ids")
    def test_edit_product_offers_criteria_from_ean(self, mocked_async_index_offer_ids, authenticated_client):
        criterion1 = criteria_factories.CriterionFactory(name="Pretty good books")
        criterion2 = criteria_factories.CriterionFactory(name="Other pretty good books")
        product = offers_factories.ProductFactory(extraData={"isbn": "9783161484100", "ean": "9783161484100"})
        offer1 = offers_factories.OfferFactory(
            product=product, extraData={"isbn": "9783161484100", "ean": "9783161484100"}, criteria=[criterion1]
        )
        offer2 = offers_factories.OfferFactory(
            product=product, extraData={"isbn": "9783161484100", "ean": "9783161484100"}
        )
        inactive_offer = offers_factories.OfferFactory(
            product=product, extraData={"isbn": "9783161484100", "ean": "9783161484100"}, isActive=False
        )
        unmatched_offer = offers_factories.OfferFactory()

        response = self.post_to_endpoint(
            authenticated_client, form={"ean": "9783161484100", "criteria": [criterion1.id, criterion2.id]}
        )

        assert response.status_code == 303
        assert response.location == url_for(
            "backoffice_v3_web.multiple_offers.search_multiple_offers", ean="9783161484100", _external=True
        )
        assert set(offer1.criteria) == {criterion1, criterion2}
        assert set(offer2.criteria) == {criterion1, criterion2}
        assert not inactive_offer.criteria
        assert not unmatched_offer.criteria
        mocked_async_index_offer_ids.assert_called_once_with([offer1.id, offer2.id])

    def test_edit_product_offers_criteria_from_ean_without_offers(self, authenticated_client):
        offers_factories.ProductFactory(extraData={"isbn": "9783161484100", "ean": "9783161484100"})
        criterion = criteria_factories.CriterionFactory(name="Pretty good books")

        response = self.post_to_endpoint(
            authenticated_client, form={"ean": "9783161484100", "criteria": [criterion.id]}
        )

        assert response.status_code == 303


class SetProductGcuIncompatibleButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.FRAUD_ACTIONS
    button_label = "Rendre le livre et les offres associées incompatibles avec les CGU"

    @property
    def path(self):
        offers_factories.ThingProductFactory(extraData={"isbn": "9781234567890", "ean": "9781234567890"})
        return url_for("backoffice_v3_web.multiple_offers.search_multiple_offers", ean="9781234567890")


class SetProductGcuIncompatibleTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.multiple_offers.set_product_gcu_incompatible"
    endpoint_kwargs = {"ean": "9781234567890"}
    needed_permission = perm_models.Permissions.FRAUD_ACTIONS

    @pytest.mark.parametrize(
        "validation_status",
        [
            OfferValidationStatus.DRAFT,
            OfferValidationStatus.PENDING,
            OfferValidationStatus.REJECTED,
            OfferValidationStatus.APPROVED,
        ],
    )
    @patch("pcapi.core.search.async_index_offer_ids")
    def test_edit_product_gcu_compatibility(
        self, mocked_async_index_offer_ids, authenticated_client, validation_status
    ):
        product_1 = offers_factories.ThingProductFactory(
            description="premier produit inapproprié",
            extraData={"isbn": "9781234567890", "ean": "9781234567890"},
            isGcuCompatible=not validation_status == OfferValidationStatus.REJECTED,
        )
        venue = offerers_factories.VenueFactory()
        offers_factories.OfferFactory(product=product_1, venue=venue, validation=validation_status)
        offers_factories.OfferFactory(product=product_1, venue=venue)

        initially_rejected = {
            offer.id: {"type": offer.lastValidationType, "date": offer.lastValidationDate}
            for offer in Offer.query.filter(Offer.validation == OfferValidationStatus.REJECTED)
        }

        response = self.post_to_endpoint(authenticated_client, form={"ean": "9781234567890"})

        assert response.status_code == 303
        assert response.location == url_for(
            "backoffice_v3_web.multiple_offers.search_multiple_offers", ean="9781234567890", _external=True
        )

        product = offers_models.Product.query.one()
        offers = Offer.query.order_by("id").all()

        assert not product.isGcuCompatible
        for offer in offers:
            assert offer.validation == offers_models.OfferValidationStatus.REJECTED
            if offer.id in initially_rejected:
                assert offer.lastValidationType == initially_rejected[offer.id]["type"]
                assert offer.lastValidationDate == initially_rejected[offer.id]["date"]
            else:
                assert offer.lastValidationType == OfferValidationType.CGU_INCOMPATIBLE_PRODUCT
                assert datetime.datetime.utcnow() - offer.lastValidationDate < datetime.timedelta(seconds=5)
        mocked_async_index_offer_ids.assert_called_once_with(
            [offer.id for offer in offers if offer.id not in initially_rejected]
        )
