from flask import url_for
import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.categories import subcategories_v2
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.users import factories as users_factories

from .helpers import html_parser
from .helpers import unauthorized as unauthorized_helpers


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


@pytest.fixture(scope="function", name="bookings")
def bookings_fixture() -> tuple:
    user = users_factories.BeneficiaryGrant18Factory(firstName="Napoléon", lastName="Bonaparte")
    confirmed = bookings_factories.BookingFactory(
        user=user,
        quantity=2,
        token="WTRL00",
        stock__price="15.2",
        stock__quantity="212",
        stock__offer__product__name="Guide du Routard Sainte-Hélène",
        stock__offer__product__subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
    )
    cancelled = bookings_factories.CancelledBookingFactory(user=user, quantity=1, amount=12.5)
    used = bookings_factories.UsedBookingFactory(user=user, quantity=1, amount=20)

    return confirmed, cancelled, used


class ListIndividualBookingsTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.bookings.list_individual_bookings"
        endpoint_kwargs = {"offerer_id": 1}
        needed_permission = perm_models.Permissions.MANAGE_BOOKINGS

    def test_list_bookings_without_filter(self, authenticated_client, bookings):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for("backoffice_v3_web.bookings.list_individual_bookings"))

        # then
        assert response.status_code == 200
        assert html_parser.count_table_rows(response.data) == 0

    def test_list_bookings_by_token(self, authenticated_client, bookings):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(
                url_for("backoffice_v3_web.bookings.list_individual_bookings", q="WTRL00")
            )

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["Code"] == "WTRL00"
        assert rows[0]["Bénéficiaire"].startswith("Napoléon Bonaparte (")
        assert rows[0]["Nom de l'offre"] == "Guide du Routard Sainte-Hélène"
        assert rows[0]["ID offre"].isdigit()
        assert rows[0]["Catégorie"] == "Livre"
        assert rows[0]["Sous-catégorie"] == "Livre papier"
        assert rows[0]["Stock"] == "212"
        assert rows[0]["Statut"] == "Confirmée"
        assert not rows[0]["Date d'annulation"]

        assert html_parser.extract_pagination_info(response.data) == (1, 1, 1)

    def test_list_bookings_by_invalid_token(self, authenticated_client, bookings):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(
                url_for("backoffice_v3_web.bookings.list_individual_bookings", q="ELBE")
            )

        # then
        assert response.status_code == 400
        assert html_parser.extract_warnings(response.data) == ["Le format de la contremarque est incorrect"]
        assert html_parser.count_table_rows(response.data) == 0

    def test_list_bookings_by_token_not_found(self, authenticated_client, bookings):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(
                url_for("backoffice_v3_web.bookings.list_individual_bookings", q="IENA06")
            )

        # then
        assert response.status_code == 200
        assert html_parser.count_table_rows(response.data) == 0
