import datetime

from flask import g
from flask import url_for
import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import categories
from pcapi.core.categories import subcategories_v2
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import factories as offerers_factories
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.models import db

from .helpers import html_parser
from .helpers import unauthorized as unauthorized_helpers


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


@pytest.fixture(scope="function", name="bookings")
def bookings_fixture() -> tuple:
    user1 = users_factories.BeneficiaryGrant18Factory(firstName="Napoléon", lastName="Bonaparte", email="napo@leon.com")
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
    reimbursed = bookings_factories.ReimbursedBookingFactory(
        user=user3,
        token="REIMB3",
        stock__offer__product__subcategoryId=subcategories_v2.SPECTACLE_REPRESENTATION.id,
        dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=1),
    )

    return used, cancelled, confirmed, reimbursed


class ListIndividualBookingsTest:
    endpoint = "backoffice_v3_web.individual_bookings.list_individual_bookings"

    # Use assert_num_queries() instead of assert_no_duplicated_queries() which does not detect one extra query caused
    # by a field added in the jinja template.
    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch individual bookings with extra data (1 query)
    expected_num_queries = 3

    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.individual_bookings.list_individual_bookings"
        endpoint_kwargs = {"offerer_id": 1}
        needed_permission = perm_models.Permissions.READ_BOOKINGS

    def test_list_bookings_without_filter(self, authenticated_client, bookings):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint))

        # then
        assert response.status_code == 200
        assert html_parser.count_table_rows(response.data) == 0

    def test_list_bookings_by_token(self, authenticated_client, bookings):
        # when
        with assert_num_queries(self.expected_num_queries):
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
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="IENA06"))

        # then
        assert response.status_code == 200
        assert html_parser.count_table_rows(response.data) == 0

    def test_list_bookings_by_offer_id(self, authenticated_client, bookings):
        # when
        searched_id = str(bookings[2].stock.offer.id)
        with assert_num_queries(self.expected_num_queries):
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
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=search_query))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        # Warning: test may return more than 1 row when an offer id is the same as expected user id
        assert len(rows) >= 1
        assert bookings[1].token in set(row["Contremarque"] for row in rows)

    @pytest.mark.parametrize(
        "search_query", ["napoleon", "bonaparte", "Napoléon Bonaparte", "napo@leon.com", "Napo@Leon.com"]
    )
    def test_list_bookings_by_user(self, authenticated_client, bookings, search_query):
        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=search_query))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(row["Contremarque"] for row in rows) == {"WTRL00", "ELBEIT"}

    def test_list_bookings_by_category(self, authenticated_client, bookings):
        # when
        with assert_num_queries(self.expected_num_queries):
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
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, status=status))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(row["Contremarque"] for row in rows) == expected_tokens

    def test_list_bookings_by_date(self, authenticated_client, bookings):
        # when
        with assert_num_queries(self.expected_num_queries):
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
        # one more query because of offerer validation
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, offerer=offerer_id))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert rows[0]["Contremarque"] == bookings[1].token

    def test_list_bookings_by_venue(self, authenticated_client, bookings):
        # when
        venue_ids = [bookings[0].venueId, bookings[2].venueId]
        # one more query because of venue validation
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, venue=venue_ids))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(row["Contremarque"] for row in rows) == {bookings[0].token, bookings[2].token}

    def test_list_bookings_more_than_max(self, authenticated_client):
        # given
        bookings_factories.BookingFactory.create_batch(
            25,
            stock__offer__product__subcategoryId=subcategories_v2.CINE_PLEIN_AIR.id,
        )

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, category=categories.CINEMA.id, limit=20))

        # then
        assert response.status_code == 200
        assert html_parser.count_table_rows(response.data) == 20
        assert "Il y a plus de 20 résultats dans la base de données" in html_parser.extract_alert(response.data)

    def test_additional_data_when_reimbursed(self, authenticated_client, bookings):
        # give
        reimbursed = bookings[3]
        reimbursement_and_pricing_venue = offerers_factories.VenueFactory()
        pricing = finance_factories.PricingFactory(
            booking=reimbursed, status=finance_models.PricingStatus.INVOICED, venue=reimbursement_and_pricing_venue
        )
        bank_info = finance_factories.BankInformationFactory(venue=reimbursement_and_pricing_venue)
        cashflow = finance_factories.CashflowFactory(
            reimbursementPoint=reimbursement_and_pricing_venue, bankAccount=bank_info, pricings=[pricing]
        )

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, status=bookings_models.BookingStatus.REIMBURSED.name)
            )

        # then
        assert response.status_code == 200
        reimbursement_data = html_parser.extract(response.data, tag="tr", class_="collapse accordion-collapse")[0]
        assert "Total payé par l'utilisateur : 10,00 €" in reimbursement_data
        assert f"Date de remboursement : {reimbursed.reimbursementDate.strftime('%d/%m/%Y')}" in reimbursement_data
        assert f"Nom de la structure : {reimbursed.offerer.name}" in reimbursement_data
        assert f"Nom du lieu : {reimbursed.venue.name}" in reimbursement_data
        assert "Montant remboursé : 10,00 €" in reimbursement_data
        assert f"N° de virement : {cashflow.batch.label}" in reimbursement_data
        assert "Taux de remboursement : 100,0 %" in reimbursement_data


def send_request(authenticated_client, url, form_data=None):
    # generate and fetch (inside g) csrf token
    booking_list_url = url_for("backoffice_v3_web.individual_bookings.list_individual_bookings")
    authenticated_client.get(booking_list_url)

    form_data = form_data if form_data else {}
    form = {"csrf_token": g.get("csrf_token", ""), **form_data}

    return authenticated_client.post(url, form=form)


class MarkBookingAsUsedTest:
    class MarkBookingAsUsedUnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        method = "post"
        endpoint = "backoffice_v3_web.individual_bookings.mark_booking_as_used"
        endpoint_kwargs = {"booking_id": 1}
        needed_permission = perm_models.Permissions.MANAGE_BOOKINGS

    def test_uncancel_and_mark_as_used(self, authenticated_client, bookings):
        # give
        cancelled = bookings[1]

        # when
        url = url_for("backoffice_v3_web.individual_bookings.mark_booking_as_used", booking_id=cancelled.id)
        response = send_request(authenticated_client, url)

        # then
        assert response.status_code == 303

        db.session.refresh(cancelled)
        assert cancelled.status is bookings_models.BookingStatus.USED

        redirected_response = authenticated_client.get(response.headers["location"])
        assert f"La réservation {cancelled.token} a été validée" in html_parser.extract_alert(redirected_response.data)

    def test_uncancel_non_cancelled_booking(self, authenticated_client, bookings):
        # give
        non_cancelled = bookings[2]
        old_status = non_cancelled.status

        # when
        url = url_for("backoffice_v3_web.individual_bookings.mark_booking_as_used", booking_id=non_cancelled.id)
        response = send_request(authenticated_client, url)

        # then
        assert response.status_code == 303

        db.session.refresh(non_cancelled)
        assert non_cancelled.status == old_status

        redirected_response = authenticated_client.get(response.headers["location"])
        assert "Impossible de valider une réservation qui n'est pas annulée" in html_parser.extract_alert(
            redirected_response.data
        )

    def test_uncancel_booking_sql_constraint_error(self, authenticated_client, bookings):
        # given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        cancelled_booking = bookings_factories.CancelledBookingFactory(user=beneficiary, stock__price="250")
        bookings_factories.ReimbursedBookingFactory(user=beneficiary, stock__price="100")

        # when
        url = url_for("backoffice_v3_web.individual_bookings.mark_booking_as_used", booking_id=cancelled_booking.id)
        response = send_request(authenticated_client, url)

        # then
        assert response.status_code == 303

        db.session.refresh(cancelled_booking)
        assert cancelled_booking.status == bookings_models.BookingStatus.CANCELLED

        redirected_response = authenticated_client.get(response.headers["location"])
        assert "insufficientFunds" in html_parser.extract_alert(redirected_response.data)


class CancelBookingTest:
    class CancelBookingUnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        method = "post"
        endpoint = "backoffice_v3_web.individual_bookings.mark_booking_as_cancelled"
        endpoint_kwargs = {"booking_id": 1}
        needed_permission = perm_models.Permissions.MANAGE_BOOKINGS

    def test_cancel_booking(self, authenticated_client, bookings):
        # give
        confirmed = bookings[2]

        # when
        url = url_for("backoffice_v3_web.individual_bookings.mark_booking_as_cancelled", booking_id=confirmed.id)
        response = send_request(authenticated_client, url)

        # then
        assert response.status_code == 303

        db.session.refresh(confirmed)
        assert confirmed.status is bookings_models.BookingStatus.CANCELLED

        redirected_response = authenticated_client.get(response.headers["location"])
        assert f"La réservation {confirmed.token} a été annulée" in html_parser.extract_alert(redirected_response.data)

    def test_cant_cancel_reimbursed_booking(self, authenticated_client, bookings):
        # give
        reimbursed = bookings[3]
        old_status = reimbursed.status

        # when
        url = url_for("backoffice_v3_web.individual_bookings.mark_booking_as_cancelled", booking_id=reimbursed.id)
        response = send_request(authenticated_client, url)
        print(response.data.decode("utf8"))
        # then
        assert response.status_code == 303

        db.session.refresh(reimbursed)
        assert reimbursed.status == old_status

        redirected_response = authenticated_client.get(response.headers["location"])
        assert "Impossible d'annuler une réservation déjà utilisée" in html_parser.extract_alert(
            redirected_response.data
        )

    def test_cant_cancel_cancelled_booking(self, authenticated_client, bookings):
        # give
        cancelled = bookings[1]
        old_status = cancelled.status

        # when
        url = url_for("backoffice_v3_web.individual_bookings.mark_booking_as_cancelled", booking_id=cancelled.id)
        response = send_request(authenticated_client, url)

        # then
        assert response.status_code == 303

        db.session.refresh(cancelled)
        assert cancelled.status == old_status

        redirected_response = authenticated_client.get(response.headers["location"])
        print(html_parser.extract_alert(redirected_response.data))
        assert "Impossible d'annuler une réservation déjà annulée" in html_parser.extract_alert(
            redirected_response.data
        )
