import datetime

from flask import url_for
import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import categories
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
    user1 = users_factories.BeneficiaryGrant18Factory(firstName="Napoléon", lastName="Bonaparte")
    user2 = users_factories.UnderageBeneficiaryFactory(firstName="Joséphine", lastName="de Beauharnais")
    user3 = users_factories.UnderageBeneficiaryFactory(firstName="Marie-Louise", lastName="d'Autriche")
    used = bookings_factories.UsedBookingFactory(
        user=user1,
        quantity=2,
        token="WTRL00",
        stock__price="15.2",
        stock__quantity="212",
        stock__offer__product__name="Guide du Routard Sainte-Hélène",
        stock__offer__product__subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
        dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=4),
    )
    cancelled = bookings_factories.CancelledBookingFactory(
        user=user2,
        quantity=1,
        amount=12.5,
        token="CNCL02",
        stock__offer__product__subcategoryId=subcategories_v2.ABO_SPECTACLE.id,
        dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=3),
    )
    confirmed = bookings_factories.BookingFactory(
        user=user1,
        quantity=1,
        token="ELBEIT",
        stock__price="13.95",
        stock__quantity="2",
        stock__offer__product__name="Guide Ile d'Elbe 1814 Petit Futé",
        stock__offer__product__subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
        dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=2),
    )
    bookings_factories.ReimbursedBookingFactory(
        user=user3,
        token="REIMB3",
        stock__offer__product__subcategoryId=subcategories_v2.SPECTACLE_REPRESENTATION.id,
        dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=1),
    )

    return used, cancelled, confirmed


class ListIndividualBookingsTest:
    endpoint = "backoffice_v3_web.individual_bookings.list_individual_bookings"

    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.individual_bookings.list_individual_bookings"
        endpoint_kwargs = {"offerer_id": 1}
        needed_permission = perm_models.Permissions.MANAGE_BOOKINGS

    def test_list_bookings_without_filter(self, authenticated_client, bookings):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint))

        # then
        assert response.status_code == 200
        assert html_parser.count_table_rows(response.data) == 0

    def test_list_bookings_by_token(self, authenticated_client, bookings):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint, q="WTRL00"))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["Contremarque"] == "WTRL00"
        assert rows[0]["Bénéficiaire"].startswith("Napoléon Bonaparte (")
        assert rows[0]["Nom de l'offre"] == "Guide du Routard Sainte-Hélène"
        assert rows[0]["ID offre"].isdigit()
        assert rows[0]["Catégorie"] == categories.LIVRE.pro_label
        assert rows[0]["Sous-catégorie"] == subcategories_v2.LIVRE_PAPIER.pro_label
        assert rows[0]["Stock"] == "212"
        assert rows[0]["Statut"] == "Validée"
        assert rows[0]["Date de réservation"] == (datetime.date.today() - datetime.timedelta(days=4)).strftime(
            "%d/%m/%Y"
        )
        assert rows[0]["Date d'utilisation"] == datetime.date.today().strftime("%d/%m/%Y")
        assert not rows[0]["Date d'annulation"]

        assert html_parser.extract_pagination_info(response.data) == (1, 1, 1)

    def test_list_bookings_by_token_not_found(self, authenticated_client, bookings):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint, q="IENA06"))

        # then
        assert response.status_code == 200
        assert html_parser.count_table_rows(response.data) == 0

    def test_list_bookings_by_offer_id(self, authenticated_client, bookings):
        # when
        searched_id = str(bookings[2].stock.offer.id)
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint, q=searched_id))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        # Warning: test may return more than 1 row when a user id is the same as expected offer id
        assert len(rows) >= 1
        result = [row for row in rows if row["ID offre"] == searched_id][0]
        assert result["Contremarque"] == "ELBEIT"
        assert result["Bénéficiaire"].startswith("Napoléon Bonaparte (")
        assert result["Nom de l'offre"] == "Guide Ile d'Elbe 1814 Petit Futé"
        assert result["Catégorie"] == categories.LIVRE.pro_label
        assert result["Sous-catégorie"] == subcategories_v2.LIVRE_PAPIER.pro_label
        assert result["Stock"] == "2"
        assert result["Statut"] == "Confirmée"
        assert result["Date de réservation"] == (datetime.date.today() - datetime.timedelta(days=2)).strftime(
            "%d/%m/%Y"
        )
        assert not result["Date d'utilisation"]
        assert not result["Date d'annulation"]

        assert html_parser.extract_pagination_info(response.data) == (1, 1, len(rows))

    def test_list_bookings_by_user_id(self, authenticated_client, bookings):
        # when
        search_query = str(bookings[1].user.id)
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint, q=search_query))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        # Warning: test may return more than 1 row when an offer id is the same as expected user id
        assert len(rows) >= 1
        assert bookings[1].token in set(row["Contremarque"] for row in rows)

    @pytest.mark.parametrize("search_query", ["napoleon", "bonaparte", "Napoléon Bonaparte"])
    def test_list_bookings_by_user_name(self, authenticated_client, bookings, search_query):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint, q=search_query))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(row["Contremarque"] for row in rows) == {"WTRL00", "ELBEIT"}

    def test_list_bookings_by_category(self, authenticated_client, bookings):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint, category=categories.SPECTACLE.id))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(row["Contremarque"] for row in rows) == {"CNCL02", "REIMB3"}

    @pytest.mark.parametrize(
        "status, expected_tokens",
        [
            ([bookings_models.BookingStatus.CONFIRMED.name], {"ELBEIT"}),
            ([bookings_models.BookingStatus.USED.name], {"WTRL00"}),
            ([bookings_models.BookingStatus.CANCELLED.name], {"CNCL02"}),
            ([bookings_models.BookingStatus.REIMBURSED.name], {"REIMB3"}),
            (
                [bookings_models.BookingStatus.CONFIRMED.name, bookings_models.BookingStatus.USED.name],
                {"ELBEIT", "WTRL00"},
            ),
        ],
    )
    def test_list_bookings_by_status(self, authenticated_client, bookings, status, expected_tokens):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint, status=status))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(row["Contremarque"] for row in rows) == expected_tokens

    def test_list_bookings_by_date(self, authenticated_client, bookings):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    from_date=(datetime.date.today() - datetime.timedelta(days=3)).isoformat(),
                    to_date=(datetime.date.today() - datetime.timedelta(days=2)).isoformat(),
                )
            )

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(row["Contremarque"] for row in rows) == {"CNCL02", "ELBEIT"}

    def test_list_bookings_by_offerer(self, authenticated_client, bookings):
        # when
        offerer_id = bookings[1].offererId
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint, offerer=offerer_id))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert rows[0]["Contremarque"] == bookings[1].token

    def test_list_bookings_by_venue(self, authenticated_client, bookings):
        # when
        venue_ids = [bookings[0].venueId, bookings[2].venueId]
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint, venue=venue_ids))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(row["Contremarque"] for row in rows) == {bookings[0].token, bookings[2].token}
