import datetime

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
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


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
        stock__offer__isDuo=True,
        stock__offer__product__name="Guide du Routard Sainte-Hélène",
        stock__offer__product__subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
        dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=4),
    )
    cancelled = bookings_factories.CancelledBookingFactory(
        user=user2,
        quantity=1,
        amount=12.5,
        token="CNCL02",
        stock__offer__product__subcategoryId=subcategories_v2.FESTIVAL_SPECTACLE.id,
        stock__beginningDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=11),
        dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=3),
    )
    confirmed = bookings_factories.BookingFactory(
        user=user1,
        quantity=1,
        token="ELBEIT",
        stock__price=13.95,
        stock__quantity="2",
        stock__offer__product__name="Guide Ile d'Elbe 1814 Petit Futé",
        stock__offer__product__subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
        dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=2),
    )
    reimbursed = bookings_factories.ReimbursedBookingFactory(
        user=user3,
        token="REIMB3",
        stock__offer__product__subcategoryId=subcategories_v2.SPECTACLE_REPRESENTATION.id,
        stock__beginningDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=12),
        dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=1),
    )

    return used, cancelled, confirmed, reimbursed


class ListIndividualBookingsTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.individual_bookings.list_individual_bookings"
    needed_permission = perm_models.Permissions.READ_BOOKINGS

    # Use assert_num_queries() instead of assert_no_duplicated_queries() which does not detect one extra query caused
    # by a field added in the jinja template.
    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch individual bookings with extra data (1 query)
    expected_num_queries = 3

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
        assert rows[0]["ID résa"] == str(bookings[0].id)
        assert rows[0]["Contremarque"] == "WTRL00"
        assert rows[0]["Bénéficiaire"].startswith("Napoléon Bonaparte (")
        assert rows[0]["Nom de l'offre"] == "Guide du Routard Sainte-Hélène"
        assert rows[0]["ID offre"].isdigit()
        assert rows[0]["Résa duo"] == "Oui"
        assert rows[0]["Stock"] == "212"
        assert rows[0]["Montant"] == "30,40 €"
        assert rows[0]["Statut"] == "Validée"
        assert rows[0]["Date de réservation"].startswith(
            (datetime.date.today() - datetime.timedelta(days=4)).strftime("%d/%m/%Y")
        )
        assert rows[0]["Structure"] == bookings[0].offerer.name
        assert rows[0]["Lieu"] == bookings[0].venue.name

        extra_data = html_parser.extract(response.data, tag="tr", class_="collapse accordion-collapse")[0]
        assert f"Catégorie : {categories.LIVRE.pro_label}" in extra_data
        assert f"Sous-catégorie : {subcategories_v2.LIVRE_PAPIER.pro_label}" in extra_data
        assert f"Date de validation : {datetime.date.today().strftime('%d/%m/%Y')} à " in extra_data
        assert "Date limite de réservation" not in extra_data
        assert "Date d'annulation" not in extra_data

        assert html_parser.extract_pagination_info(response.data) == (1, 1, 1)

    def test_list_bookings_by_offer_name(self, authenticated_client, bookings):
        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="Routard Sainte-Hélène"))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID résa"] == str(bookings[0].id)
        assert rows[0]["Nom de l'offre"] == "Guide du Routard Sainte-Hélène"
        assert html_parser.extract_pagination_info(response.data) == (1, 1, 1)

    def test_list_bookings_by_booking_id(self, authenticated_client, bookings):
        searched_booking_id = bookings[0].id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=searched_booking_id))

        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID résa"] == str(bookings[0].id)

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
        for row_index, row in enumerate(rows):
            if row["ID offre"] == searched_id:
                break
        else:
            row_index, row = 0, {}  # for pylint
            assert False, f"Expected offer {searched_id} not found in results"
        assert row["ID résa"] == str(bookings[2].id)
        assert row["Contremarque"] == "ELBEIT"
        assert row["Bénéficiaire"].startswith("Napoléon Bonaparte (")
        assert row["Nom de l'offre"] == "Guide Ile d'Elbe 1814 Petit Futé"
        assert row["Résa duo"] == "Non"
        assert row["Stock"] == "2"
        assert row["Montant"] == "13,95 €"
        assert row["Statut"] == "Confirmée"
        assert row["Date de réservation"].startswith(
            (datetime.date.today() - datetime.timedelta(days=2)).strftime("%d/%m/%Y à")
        )
        assert row["Structure"] == bookings[2].offerer.name
        assert row["Lieu"] == bookings[2].venue.name

        extra_data = html_parser.extract(response.data, tag="tr", class_="collapse accordion-collapse")[row_index]
        assert f"Catégorie : {categories.LIVRE.pro_label}" in extra_data
        assert f"Sous-catégorie : {subcategories_v2.LIVRE_PAPIER.pro_label}" in extra_data
        assert "Date" not in extra_data

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

    @pytest.mark.parametrize("search_query", ["bonaparte", "Napoléon Bonaparte", "napo@leon.com", "Napo@Leon.com"])
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

    def test_list_bookings_by_cashflow_batch(self, authenticated_client):
        # given
        cashflows = finance_factories.CashflowFactory.create_batch(
            3,
            reimbursementPoint=finance_factories.BankInformationFactory(venue=offerers_factories.VenueFactory()).venue,
        )

        finance_factories.PricingFactory(booking=bookings_factories.UsedBookingFactory())
        finance_factories.PricingFactory(
            booking=bookings_factories.ReimbursedBookingFactory(), cashflows=[cashflows[1]]
        )

        reimbursed_pricing1 = finance_factories.PricingFactory(
            booking=bookings_factories.ReimbursedBookingFactory(), cashflows=[cashflows[0]]
        )
        reimbursed_pricing3 = finance_factories.PricingFactory(
            booking=bookings_factories.ReimbursedBookingFactory(), cashflows=[cashflows[2]]
        )

        # when
        searched_cashflow_batches = [cashflows[0].batch.id, cashflows[2].batch.id]
        # one more query because of cashflow_batches validation
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, cashflow_batches=searched_cashflow_batches))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID résa"]) for row in rows) == {
            reimbursed_pricing1.bookingId,
            reimbursed_pricing3.bookingId,
        }

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

    def test_list_bookings_by_event_date(self, authenticated_client, bookings):
        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    event_from_date=(datetime.date.today() + datetime.timedelta(days=12)).isoformat(),
                    event_to_date=(datetime.date.today() + datetime.timedelta(days=12)).isoformat(),
                )
            )

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(row["Contremarque"] for row in rows) == {"REIMB3"}

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
        assert html_parser.count_table_rows(response.data) == 2 * 20  # extra data in second row for each booking
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
        assert "Total payé par l'utilisateur : 10,10 €" in reimbursement_data
        assert f"Date de remboursement : {reimbursed.reimbursementDate.strftime('%d/%m/%Y à ')}" in reimbursement_data
        assert "Montant remboursé : 10,10 €" in reimbursement_data
        assert f"N° de virement : {cashflow.batch.label}" in reimbursement_data
        assert "Taux de remboursement : 100,0 %" in reimbursement_data


class MarkBookingAsUsedTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.individual_bookings.mark_booking_as_used"
    endpoint_kwargs = {"booking_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_BOOKINGS

    def test_uncancel_and_mark_as_used(self, authenticated_client, bookings):
        # give
        cancelled = bookings[1]

        # when
        response = self.post_to_endpoint(authenticated_client, booking_id=cancelled.id)

        # then
        assert response.status_code == 302

        db.session.refresh(cancelled)
        assert cancelled.status is bookings_models.BookingStatus.USED

        redirected_response = authenticated_client.get(response.headers["location"])
        assert html_parser.extract_alert(redirected_response.data) == f"La réservation {cancelled.token} a été validée"

    def test_uncancel_non_cancelled_booking(self, authenticated_client, bookings):
        # give
        non_cancelled = bookings[2]
        old_status = non_cancelled.status

        # when
        response = self.post_to_endpoint(authenticated_client, booking_id=non_cancelled.id)

        # then
        assert response.status_code == 302

        db.session.refresh(non_cancelled)
        assert non_cancelled.status == old_status

        redirected_response = authenticated_client.get(response.headers["location"])
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Impossible de valider une réservation qui n'est pas annulée"
        )

    def test_uncancel_booking_insufficient_funds(self, authenticated_client, bookings):
        # given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        cancelled_booking = bookings_factories.CancelledBookingFactory(user=beneficiary, stock__price="250")
        bookings_factories.ReimbursedBookingFactory(user=beneficiary, stock__price="100")

        # when
        response = self.post_to_endpoint(authenticated_client, booking_id=cancelled_booking.id)

        # then
        assert response.status_code == 302

        db.session.refresh(cancelled_booking)
        assert cancelled_booking.status == bookings_models.BookingStatus.CANCELLED

        redirected_response = authenticated_client.get(response.headers["location"])
        assert "The user does not have enough credit to book" in html_parser.extract_alert(redirected_response.data)

    def test_uncancel_booking_no_stock(self, authenticated_client, bookings):
        # given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        cancelled_booking = bookings_factories.CancelledBookingFactory(user=beneficiary, quantity=2, stock__quantity=1)

        # when
        response = self.post_to_endpoint(authenticated_client, booking_id=cancelled_booking.id)

        # then
        assert response.status_code == 302

        db.session.refresh(cancelled_booking)
        assert cancelled_booking.status == bookings_models.BookingStatus.CANCELLED

        redirected_response = authenticated_client.get(response.headers["location"])
        assert 'Number of bookings cannot exceed "stock.quantity"' in html_parser.extract_alert(
            redirected_response.data
        )


class CancelBookingTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.individual_bookings.mark_booking_as_cancelled"
    endpoint_kwargs = {"booking_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_BOOKINGS

    def test_cancel_booking(self, authenticated_client, bookings):
        # give
        confirmed = bookings[2]

        # when
        response = self.post_to_endpoint(authenticated_client, booking_id=confirmed.id)

        # then
        assert response.status_code == 302

        db.session.refresh(confirmed)
        assert confirmed.status is bookings_models.BookingStatus.CANCELLED

        redirected_response = authenticated_client.get(response.headers["location"])
        assert html_parser.extract_alert(redirected_response.data) == f"La réservation {confirmed.token} a été annulée"

    def test_cant_cancel_booking_with_pricing_processed(self, authenticated_client, bookings):
        # given
        pricing = finance_factories.PricingFactory(status=finance_models.PricingStatus.PROCESSED)

        # when
        response = self.post_to_endpoint(authenticated_client, booking_id=pricing.bookingId)

        # then
        assert response.status_code == 302

        db.session.refresh(pricing)
        assert pricing.booking.status == bookings_models.BookingStatus.USED

        redirected_response = authenticated_client.get(response.headers["location"])
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Impossible d'annuler une réservation déjà valorisée ou remboursée"
        )

    @pytest.mark.parametrize(
        "with_pricing,expected_message",
        [
            (False, "Impossible d'annuler une réservation déjà utilisée"),
            (True, "Impossible d'annuler une réservation déjà valorisée ou remboursée"),
        ],
    )
    def test_cant_cancel_reimbursed_booking(self, authenticated_client, bookings, with_pricing, expected_message):
        # give
        reimbursed = bookings[3]
        old_status = reimbursed.status
        if with_pricing:
            finance_factories.PricingFactory(booking=reimbursed, status=finance_models.PricingStatus.INVOICED)
            finance_factories.PaymentFactory(booking=reimbursed)

        # when
        response = self.post_to_endpoint(authenticated_client, booking_id=reimbursed.id)

        # then
        assert response.status_code == 302

        db.session.refresh(reimbursed)
        assert reimbursed.status == old_status

        redirected_response = authenticated_client.get(response.headers["location"])
        assert html_parser.extract_alert(redirected_response.data) == expected_message

    def test_cant_cancel_cancelled_booking(self, authenticated_client, bookings):
        # give
        cancelled = bookings[1]
        old_status = cancelled.status

        # when
        response = self.post_to_endpoint(authenticated_client, booking_id=cancelled.id)

        # then
        assert response.status_code == 302

        db.session.refresh(cancelled)
        assert cancelled.status == old_status

        redirected_response = authenticated_client.get(response.headers["location"])
        assert (
            html_parser.extract_alert(redirected_response.data) == "Impossible d'annuler une réservation déjà annulée"
        )


class GetBatchMarkAsUsedIndividualBookingsFormTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.individual_bookings.get_batch_validate_individual_bookings_form"
    needed_permission = perm_models.Permissions.MANAGE_BOOKINGS

    def test_get_batch_mark_as_used_booking_form(self, legit_user, authenticated_client):
        # given
        bookings_factories.BookingFactory()
        with assert_num_queries(2):  # session + tested_query
            # when
            response = authenticated_client.get(url_for(self.endpoint))
            # then
            # Rendering is not checked, but at least the fetched frame does not crash
            assert response.status_code == 200


class BatchMarkBookingAsUsedTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.individual_bookings.batch_validate_individual_bookings"
    needed_permission = perm_models.Permissions.MANAGE_BOOKINGS

    def test_batch_mark_as_used_bookings(self, legit_user, authenticated_client):
        bookings = bookings_factories.BookingFactory.create_batch(3)
        parameter_ids = ",".join(str(booking.id) for booking in bookings)
        response = self.post_to_endpoint(authenticated_client, form={"object_ids": parameter_ids})

        assert response.status_code == 302
        for booking in bookings:
            db.session.refresh(booking)
            assert booking.status is bookings_models.BookingStatus.USED

    def test_batch_mark_as_used_cancelled_bookings(self, legit_user, authenticated_client):
        bookings = bookings_factories.BookingFactory.create_batch(3, status=bookings_models.BookingStatus.CANCELLED)
        parameter_ids = ",".join(str(booking.id) for booking in bookings)
        response = self.post_to_endpoint(authenticated_client, form={"object_ids": parameter_ids})

        assert response.status_code == 302
        for booking in bookings:
            db.session.refresh(booking)
            assert booking.status is bookings_models.BookingStatus.USED


class GetBatchCancelIndividualBookingsFormTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.individual_bookings.get_batch_cancel_individual_bookings_form"
    needed_permission = perm_models.Permissions.MANAGE_BOOKINGS

    def test_get_batch_cancel_booking_form(self, legit_user, authenticated_client):
        # given
        bookings_factories.BookingFactory()
        with assert_num_queries(2):  # session + tested_query
            # when
            url = url_for(self.endpoint)
            response = authenticated_client.get(url)
            # then
            # Rendering is not checked, but at least the fetched frame does not crash
            assert response.status_code == 200


class BatchOfferCancelTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.individual_bookings.batch_cancel_individual_bookings"
    needed_permission = perm_models.Permissions.MANAGE_BOOKINGS

    def test_batch_cancel_bookings(self, legit_user, authenticated_client):
        bookings = bookings_factories.BookingFactory.create_batch(3)
        parameter_ids = ",".join(str(booking.id) for booking in bookings)
        response = self.post_to_endpoint(authenticated_client, form={"object_ids": parameter_ids})

        assert response.status_code == 302
        for booking in bookings:
            db.session.refresh(booking)
            assert booking.status is bookings_models.BookingStatus.CANCELLED
