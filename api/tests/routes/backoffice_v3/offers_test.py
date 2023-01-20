import datetime

from flask import url_for
import pytest

from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.offers import factories as offers_factories
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_no_duplicated_queries

from .helpers import html_parser
from .helpers import unauthorized as unauthorized_helpers


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


@pytest.fixture(scope="function", name="offers")
def offers_fixture() -> tuple:
    criterion = criteria_factories.CriterionFactory()
    offer_with_unlimited_stock = offers_factories.OfferFactory(criteria=[criterion])
    offer_with_limited_stock = offers_factories.OfferFactory(
        name="A Very Specific Name", lastValidationDate=datetime.date(2022, 2, 22)
    )
    offers_factories.OfferFactory(name="A Very Specific Name That Is Longer")
    offers_factories.StockFactory(quantity=None, offer=offer_with_unlimited_stock)
    offers_factories.StockFactory(offer=offer_with_unlimited_stock)
    offers_factories.StockFactory(quantity=10, dnBookedQuantity=0, offer=offer_with_limited_stock)
    offers_factories.StockFactory(quantity=10, dnBookedQuantity=5, offer=offer_with_limited_stock)
    return offer_with_unlimited_stock, offer_with_limited_stock


class ListOffersTest:
    endpoint = "backoffice_v3_web.offer.list_offers"

    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.offer.list_offers"
        endpoint_kwargs = {"offerer_id": 1}
        needed_permission = perm_models.Permissions.MANAGE_OFFERS

    def test_list_offers_without_filter(self, authenticated_client, offers):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint))

        # then
        assert response.status_code == 200
        assert html_parser.count_table_rows(response.data) == 0

    def test_list_offers_by_id(self, authenticated_client, offers):
        # when
        searched_id = str(offers[0].id)
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint, q=searched_id))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == searched_id
        assert rows[0]["Nom de l'offre"] == offers[0].name
        assert rows[0]["Catégorie"] == offers[0].category.pro_label
        assert rows[0]["Sous-catégorie"] == offers[0].subcategory_v2.pro_label
        assert rows[0]["Stock initial"] == "Illimité"
        assert rows[0]["Stock restant"] == "Illimité"
        assert rows[0]["Tag"] == offers[0].criteria[0].name
        assert rows[0]["Pondération"] == ""
        assert rows[0]["État"] == "Validée"
        assert rows[0]["Dernière date de validation"] == ""

    def test_list_offers_by_name(self, authenticated_client, offers):
        # when
        searched_name = str(offers[1].name)
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint, q=searched_name))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert rows[0]["ID"] == str(offers[1].id)
        assert rows[0]["Nom de l'offre"] == offers[1].name
        assert rows[0]["Catégorie"] == offers[1].category.pro_label
        assert rows[0]["Sous-catégorie"] == offers[1].subcategory_v2.pro_label
        assert rows[0]["Stock initial"] == "20"
        assert rows[0]["Stock restant"] == "15"
        assert rows[0]["Tag"] == ""
        assert rows[0]["Pondération"] == ""
        assert rows[0]["État"] == "Validée"
        assert rows[0]["Dernière date de validation"] == "22/02/2022"
