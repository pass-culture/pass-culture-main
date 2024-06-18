import dataclasses
import datetime
from io import BytesIO
import re

import factory
from flask import url_for
import openpyxl
import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import categories
from pcapi.core.categories import subcategories_v2
from pcapi.core.external_bookings import factories as external_bookings_factories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.routes.backoffice.bookings import forms

from tests.connectors.cgr import soap_definitions
from tests.local_providers.cinema_providers.cgr import fixtures as cgr_fixtures

from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


@pytest.fixture(scope="function", name="bookings")
def bookings_fixture() -> tuple:
    user1 = users_factories.BeneficiaryGrant18Factory(firstName="Napoléon", lastName="Bonaparte", email="napo@leon.com")
    user2 = users_factories.UnderageBeneficiaryFactory(firstName="Joséphine", lastName="de Beauharnais")
    user3 = users_factories.UnderageBeneficiaryFactory(firstName="Marie-Louise", lastName="d'Autriche")
    user4 = users_factories.UnderageBeneficiaryFactory(firstName="Marie-Louise", lastName="d'Autriche")
    used = bookings_factories.UsedBookingFactory(
        id=1000001,  # Avoid flaky test because of same ids in bookings and offers
        user=user1,
        quantity=2,
        token="WTRL00",
        stock__price="15.2",
        stock__quantity="212",
        stock__offer__isDuo=True,
        stock__offer__name="Guide du Routard Sainte-Hélène",
        stock__offer__subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
        dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=4),
        validationAuthorType=bookings_models.BookingValidationAuthorType.BACKOFFICE,
    )
    offerers_factories.UserOffererFactory(offerer=used.offerer)
    cancelled = bookings_factories.CancelledBookingFactory(
        id=1000002,
        user=user2,
        quantity=1,
        amount=12.5,
        token="CNCL02",
        stock__offer__subcategoryId=subcategories_v2.FESTIVAL_SPECTACLE.id,
        stock__beginningDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=11),
        dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=3),
    )
    confirmed = bookings_factories.BookingFactory(
        id=1000003,
        user=user1,
        quantity=1,
        token="ELBEIT",
        stock__price=13.95,
        stock__quantity="2",
        stock__offer__name="Guide Ile d'Elbe 1814 Petit Futé",
        stock__offer__subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
        dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=2),
        cancellation_limit_date=datetime.datetime.utcnow() - datetime.timedelta(days=1),
    )
    reimbursed = bookings_factories.ReimbursedBookingFactory(
        id=1000004,
        user=user3,
        token="REIMB3",
        stock__offer__subcategoryId=subcategories_v2.SPECTACLE_REPRESENTATION.id,
        stock__beginningDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=12),
        dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=1),
    )
    booked = bookings_factories.BookingFactory(
        id=1000005,
        user=user4,
        quantity=1,
        token="ADFTH9",
        stock__price=12.34,
        stock__quantity="1",
        stock__offer__name="Guide Ile d'Elbe 1814 Petit Futé",
        stock__offer__subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
        dateCreated=datetime.datetime.utcnow(),
    )

    return used, cancelled, confirmed, reimbursed, booked


class ListIndividualBookingsTest(GetEndpointHelper):
    endpoint = "backoffice_web.individual_bookings.list_individual_bookings"
    needed_permission = perm_models.Permissions.READ_BOOKINGS

    # Use assert_num_queries() instead of assert_no_duplicated_queries() which does not detect one extra query caused
    # by a field added in the jinja template.
    # - fetch session (1 query)
    # - fetch user (1 query)
    expected_num_queries_when_no_query = 2
    # - fetch individual bookings with extra data (1 query)
    # - check finance incident FF
    expected_num_queries = expected_num_queries_when_no_query + 2

    def test_list_bookings_without_filter(self, authenticated_client, bookings):
        with assert_num_queries(self.expected_num_queries_when_no_query):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        assert html_parser.count_table_rows(response.data) == 0

    def test_list_bookings_by_token(self, authenticated_client, bookings):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="WTRL00"))
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
        assert rows[0]["Crédit actif"] == "Oui"
        assert rows[0]["Auteur de la validation"] == "Backoffice"
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

    def test_list_bookings_with_expired_deposit(self, authenticated_client):
        user = users_factories.BeneficiaryGrant18Factory()
        booking = bookings_factories.UsedBookingFactory(
            user=user,
            token="WTRL00",
        )

        users_factories.DepositGrantFactory(
            bookings=[booking],
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=5),
            expirationDate=datetime.datetime.utcnow() - datetime.timedelta(days=1),
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="WTRL00"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert rows[0]["Crédit actif"] == "Non"

    def test_list_bookings_by_list_of_tokens(self, authenticated_client, bookings):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="WTRL00 ELBEIT\tREIMB3\n"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 3
        assert set(row["Contremarque"] for row in rows) == {"WTRL00", "ELBEIT", "REIMB3"}

    @pytest.mark.parametrize(
        "incident_status, display_alert",
        [
            (finance_models.IncidentStatus.VALIDATED, True),
            (finance_models.IncidentStatus.CREATED, False),
            (finance_models.IncidentStatus.CANCELLED, False),
        ],
    )
    def test_display_incident_alert(self, authenticated_client, incident_status, display_alert):
        booking = bookings_factories.ReimbursedBookingFactory(
            incidents=[
                finance_factories.IndividualBookingFinanceIncidentFactory(
                    incident=finance_factories.FinanceIncidentFactory(status=incident_status)
                )
            ]
        )

        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint, q=booking.id))
            assert response.status_code == 200

        if display_alert:
            assert "bi-exclamation-triangle-fill" in str(response.data)
        else:
            assert "bi-exclamation-triangle-fill" not in str(response.data)

    @pytest.mark.parametrize(
        "query_args",
        [
            {},
            {"from_to_date": [datetime.datetime(1970, 1, 1), None]},
            {"from_to_date": [None, datetime.datetime(2037, 12, 31)]},
            {"from_to_date": [datetime.datetime(1970, 1, 1), datetime.datetime(2037, 12, 31)]},
        ],
    )
    def test_display_download_link(self, authenticated_client, bookings, query_args):
        venue_id = [bookings[0].venueId]
        kwargs = {**query_args, "venue_id": venue_id}
        response = authenticated_client.get(url_for(self.endpoint, **kwargs))
        assert b"pc-clipboard" in response.data

    def test_list_bookings_by_offer_name(self, authenticated_client, bookings):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="Routard Sainte-Hélène"))
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
        # -1 query because no need to check incident ff when no result
        with assert_num_queries(self.expected_num_queries - 1):
            response = authenticated_client.get(url_for(self.endpoint, q="IENA06"))
            assert response.status_code == 200

        assert html_parser.count_table_rows(response.data) == 0

    def test_list_bookings_by_offer_id(self, authenticated_client, bookings):
        searched_id = str(bookings[2].stock.offer.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=searched_id))
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
        search_query = str(bookings[1].user.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=search_query))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        # Warning: test may return more than 1 row when an offer id is the same as expected user id
        assert len(rows) >= 1
        assert bookings[1].token in set(row["Contremarque"] for row in rows)

    @pytest.mark.parametrize("search_query", ["napo@leon.com", "Napo@Leon.com"])
    def test_list_bookings_by_user(self, authenticated_client, bookings, search_query):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=search_query))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(row["Contremarque"] for row in rows) == {"WTRL00", "ELBEIT"}

    def test_list_bookings_by_category(self, authenticated_client, bookings):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, category=categories.SPECTACLE.id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(row["Contremarque"] for row in rows) == {"CNCL02", "REIMB3"}

    def test_list_bookings_by_cashflow_batch(self, authenticated_client):
        cashflows = finance_factories.CashflowFactory.create_batch(
            3,
            bankAccount=finance_factories.BankAccountFactory(),
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

        searched_cashflow_batches = [cashflows[0].batch.id, cashflows[2].batch.id]
        # one more query because of cashflow_batches validation
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, cashflow_batches=searched_cashflow_batches))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID résa"]) for row in rows) == {
            reimbursed_pricing1.bookingId,
            reimbursed_pricing3.bookingId,
        }

    @pytest.mark.parametrize(
        "status, expected_tokens",
        [
            ([forms.BookingStatus.CONFIRMED.name], {"ELBEIT"}),
            ([forms.BookingStatus.USED.name], {"WTRL00"}),
            ([forms.BookingStatus.CANCELLED.name], {"CNCL02"}),
            ([forms.BookingStatus.REIMBURSED.name], {"REIMB3"}),
            ([forms.BookingStatus.BOOKED.name], {"ADFTH9"}),
            (
                [forms.BookingStatus.CONFIRMED.name, forms.BookingStatus.USED.name],
                {"ELBEIT", "WTRL00"},
            ),
        ],
    )
    def test_list_bookings_by_status(self, authenticated_client, bookings, status, expected_tokens):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, status=status))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(row["Contremarque"] for row in rows) == expected_tokens

    def test_list_bookings_by_cancellation_reason(self, authenticated_client):
        bookings_factories.CancelledBookingFactory.create_batch(
            size=3,
            token=factory.Iterator(["CNCL01", "CNCL02", "CNCL03"]),
            cancellationReason=factory.Iterator(
                [
                    bookings_models.BookingCancellationReasons.OFFERER.value,
                    bookings_models.BookingCancellationReasons.BENEFICIARY.value,
                    bookings_models.BookingCancellationReasons.FRAUD.value,
                ]
            ),
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, cancellation_reason=["OFFERER", "FRAUD"]))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)

        assert {row["Contremarque"] for row in rows} == {"CNCL01", "CNCL03"}

    def test_list_bookings_by_date(self, authenticated_client, bookings):
        date_from = datetime.date.today() - datetime.timedelta(days=3)
        date_to = datetime.date.today() - datetime.timedelta(days=2)
        separator = " - "
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    from_to_date=f"{date_from.strftime('%d/%m/%Y')}{separator}{date_to.strftime('%d/%m/%Y')}",
                )
            )
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(row["Contremarque"] for row in rows) == {"CNCL02", "ELBEIT"}

    @pytest.mark.parametrize(
        "from_date, to_date, expected_tokens",
        [
            ((datetime.date.today() + datetime.timedelta(days=12)).isoformat(), None, {"REIMB3"}),
            (None, (datetime.date.today() + datetime.timedelta(days=12)).isoformat(), {"CNCL02", "REIMB3"}),
            (
                (datetime.date.today() + datetime.timedelta(days=12)).isoformat(),
                (datetime.date.today() + datetime.timedelta(days=12)).isoformat(),
                {"REIMB3"},
            ),
        ],
    )
    def test_list_bookings_by_event_date(self, authenticated_client, bookings, from_date, to_date, expected_tokens):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    event_from_date=from_date,
                    event_to_date=to_date,
                )
            )
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(row["Contremarque"] for row in rows) == expected_tokens

    def test_list_bookings_by_offerer(self, authenticated_client, bookings):
        offerer_id = bookings[1].offererId
        # one more query because of offerer validation
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, offerer=offerer_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert rows[0]["Contremarque"] == bookings[1].token

    def test_list_bookings_by_venue(self, authenticated_client, bookings):
        venue_ids = [bookings[0].venueId, bookings[2].venueId]
        # one more query because of venue validation
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, venue=venue_ids))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(row["Contremarque"] for row in rows) == {bookings[0].token, bookings[2].token}

    @pytest.mark.parametrize(
        "deposit_filter_value, result_token",
        [
            ("expired", "EXPIRD"),
            ("active", "ACTIVE"),
        ],
    )
    def test_list_bookings_by_deposit_expiration_status(self, authenticated_client, deposit_filter_value, result_token):
        old_user = users_factories.BeneficiaryGrant18Factory()
        expired_deposit_booking = bookings_factories.UsedBookingFactory(
            user=old_user,
            token="EXPIRD",
        )
        users_factories.DepositGrantFactory(
            bookings=[expired_deposit_booking],
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=5),
            expirationDate=datetime.datetime.utcnow() - datetime.timedelta(days=1),
        )

        new_user = users_factories.BeneficiaryGrant18Factory()
        bookings_factories.UsedBookingFactory(
            user=new_user,
            token="ACTIVE",
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, deposit=deposit_filter_value))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(row["Contremarque"] for row in rows) == {result_token}

    def test_list_bookings_more_than_max(self, authenticated_client):
        bookings_factories.BookingFactory.create_batch(
            25,
            stock__offer__subcategoryId=subcategories_v2.CINE_PLEIN_AIR.id,
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, category=categories.CINEMA.id, limit=20))
            assert response.status_code == 200

        assert html_parser.count_table_rows(response.data) == 2 * 20  # extra data in second row for each booking
        assert "Il y a plus de 20 résultats dans la base de données" in html_parser.extract_alert(response.data)

    def test_additional_data_when_reimbursed(self, authenticated_client, bookings):
        reimbursed = bookings[3]
        pricing_venue = offerers_factories.VenueFactory()
        bank_account = finance_factories.BankAccountFactory()
        offerers_factories.VenueBankAccountLinkFactory(venue=pricing_venue, bankAccount=bank_account)
        pricing = finance_factories.PricingFactory(
            booking=reimbursed,
            status=finance_models.PricingStatus.INVOICED,
            venue=pricing_venue,
        )
        cashflow = finance_factories.CashflowFactory(bankAccount=bank_account, pricings=[pricing])

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, status=bookings_models.BookingStatus.REIMBURSED.name)
            )
            assert response.status_code == 200

        reimbursement_data = html_parser.extract(response.data, tag="tr", class_="collapse accordion-collapse")[0]
        assert "Total payé par l'utilisateur : 10,10 €" in reimbursement_data
        assert f"Date de remboursement : {reimbursed.reimbursementDate.strftime('%d/%m/%Y à ')}" in reimbursement_data
        assert "Montant remboursé : 10,10 €" in reimbursement_data
        assert f"N° de virement : {cashflow.batch.label}" in reimbursement_data
        assert "Taux de remboursement : 100,0 %" in reimbursement_data

    def test_sort_bookings_by_date(self, authenticated_client, bookings):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, status=[s.name for s in forms.BookingStatus]))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        # booked J not used, booked J-2 not used, event J+12, event J+11, used J
        assert [row["Contremarque"] for row in rows] == ["ADFTH9", "ELBEIT", "REIMB3", "CNCL02", "WTRL00"]


class MarkBookingAsUsedTest(PostEndpointHelper):
    endpoint = "backoffice_web.individual_bookings.mark_booking_as_used"
    endpoint_kwargs = {"booking_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_BOOKINGS

    def test_uncancel_and_mark_as_used(self, authenticated_client, bookings):
        cancelled = bookings[1]

        response = self.post_to_endpoint(authenticated_client, booking_id=cancelled.id)

        assert response.status_code == 303

        db.session.refresh(cancelled)
        assert cancelled.status is bookings_models.BookingStatus.USED
        assert cancelled.validationAuthorType == bookings_models.BookingValidationAuthorType.BACKOFFICE

        redirected_response = authenticated_client.get(response.headers["location"])
        assert html_parser.extract_alert(redirected_response.data) == f"La réservation {cancelled.token} a été validée"

    def test_uncancel_non_cancelled_booking(self, authenticated_client, bookings):
        non_cancelled = bookings[2]
        old_status = non_cancelled.status

        response = self.post_to_endpoint(authenticated_client, booking_id=non_cancelled.id)

        assert response.status_code == 303

        db.session.refresh(non_cancelled)
        assert non_cancelled.status == old_status

        redirected_response = authenticated_client.get(response.headers["location"])
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Impossible de valider une réservation qui n'est pas annulée"
        )

    def test_uncancel_booking_insufficient_funds(self, authenticated_client, bookings):
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        booking_id = bookings_factories.CancelledBookingFactory(user=beneficiary, stock__price="250").id
        bookings_factories.ReimbursedBookingFactory(user=beneficiary, stock__price="100")

        response = self.post_to_endpoint(authenticated_client, booking_id=booking_id)

        assert response.status_code == 303

        booking = bookings_models.Booking.query.filter_by(id=booking_id).one()
        assert booking.status == bookings_models.BookingStatus.CANCELLED

        redirected_response = authenticated_client.get(response.headers["location"])
        assert "The user does not have enough credit to book" in html_parser.extract_alert(redirected_response.data)

    def test_uncancel_booking_no_stock(self, authenticated_client, bookings):
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        booking_id = bookings_factories.CancelledBookingFactory(user=beneficiary, quantity=2, stock__quantity=1).id

        response = self.post_to_endpoint(authenticated_client, booking_id=booking_id)

        assert response.status_code == 303

        booking = bookings_models.Booking.query.filter_by(id=booking_id).one()
        assert booking.status == bookings_models.BookingStatus.CANCELLED

        redirected_response = authenticated_client.get(response.headers["location"])
        assert 'Number of bookings cannot exceed "stock.quantity"' in html_parser.extract_alert(
            redirected_response.data
        )


class CancelBookingTest(PostEndpointHelper):
    endpoint = "backoffice_web.individual_bookings.mark_booking_as_cancelled"
    endpoint_kwargs = {"booking_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_BOOKINGS

    def test_cancel_booking(self, authenticated_client, bookings):
        confirmed = bookings[2]

        response = self.post_to_endpoint(
            authenticated_client,
            booking_id=confirmed.id,
            form={"reason": bookings_models.BookingCancellationReasons.BACKOFFICE.value},
        )

        assert response.status_code == 303

        db.session.refresh(confirmed)
        assert confirmed.status is bookings_models.BookingStatus.CANCELLED
        assert confirmed.cancellationReason == bookings_models.BookingCancellationReasons.BACKOFFICE

        redirected_response = authenticated_client.get(response.headers["location"])
        assert html_parser.extract_alert(redirected_response.data) == f"La réservation {confirmed.token} a été annulée"

    def test_cancel_booking_decreases_stock_quantity(self, authenticated_client, bookings):
        stock = offers_factories.StockFactory(quantity=3)

        booking = bookings_factories.BookingFactory(stock=stock)
        booking_to_cancel = bookings_factories.BookingFactory(stock=stock)
        offers_factories.ActivationCodeFactory(booking=booking, stock=stock)
        offers_factories.ActivationCodeFactory(booking=booking_to_cancel, stock=stock)

        response = self.post_to_endpoint(
            authenticated_client,
            booking_id=booking_to_cancel.id,
            form={"reason": bookings_models.BookingCancellationReasons.BENEFICIARY.value},
        )

        assert response.status_code == 303
        db.session.refresh(booking_to_cancel)
        assert booking_to_cancel.status == bookings_models.BookingStatus.CANCELLED
        assert booking_to_cancel.cancellationReason == bookings_models.BookingCancellationReasons.BENEFICIARY
        assert stock.quantity == 2
        assert stock.dnBookedQuantity == 1

    def test_cant_cancel_booking_with_pricing_processed(self, authenticated_client, bookings):
        pricing = finance_factories.PricingFactory(status=finance_models.PricingStatus.PROCESSED)

        response = self.post_to_endpoint(
            authenticated_client,
            booking_id=pricing.bookingId,
            form={"reason": bookings_models.BookingCancellationReasons.BACKOFFICE.value},
        )

        assert response.status_code == 303

        db.session.refresh(pricing)
        assert pricing.booking.status == bookings_models.BookingStatus.USED

        redirected_response = authenticated_client.get(response.headers["location"])
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Cette réservation est en train d’être remboursée, il est impossible de l’invalider"
        )

    def test_cant_cancel_reimbursed_booking(self, authenticated_client, bookings):
        reimbursed = bookings[3]
        old_status = reimbursed.status

        response = self.post_to_endpoint(
            authenticated_client,
            booking_id=reimbursed.id,
            form={"reason": bookings_models.BookingCancellationReasons.BACKOFFICE.value},
        )

        assert response.status_code == 303

        db.session.refresh(reimbursed)
        assert reimbursed.status == old_status

        redirected_response = authenticated_client.get(response.headers["location"])
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Cette réservation est en train d’être remboursée, il est impossible de l’invalider"
        )

    def test_cant_cancel_cancelled_booking(self, authenticated_client, bookings):
        cancelled = bookings[1]
        old_status = cancelled.status

        response = self.post_to_endpoint(
            authenticated_client,
            booking_id=cancelled.id,
            form={"reason": bookings_models.BookingCancellationReasons.BACKOFFICE.value},
        )

        assert response.status_code == 303

        db.session.refresh(cancelled)
        assert cancelled.status == old_status

        redirected_response = authenticated_client.get(response.headers["location"])
        assert (
            html_parser.extract_alert(redirected_response.data) == "Impossible d'annuler une réservation déjà annulée"
        )

    def test_cant_cancel_booking_without_reason(self, authenticated_client, bookings):
        confirmed = bookings[2]

        response = self.post_to_endpoint(authenticated_client, booking_id=confirmed.id)

        assert response.status_code == 303

        db.session.refresh(confirmed)
        assert confirmed.status == bookings_models.BookingStatus.CONFIRMED
        assert confirmed.cancellationReason is None

        redirected_response = authenticated_client.get(response.headers["location"])

        assert (
            "Les données envoyées comportent des erreurs. Raison : Information obligatoire"
            in html_parser.extract_alert(redirected_response.data)
        )

    @override_features(ENABLE_EMS_INTEGRATION=True)
    @override_settings(EMS_SUPPORT_EMAIL_ADDRESS="ems.support@example.com")
    def test_ems_cancel_external_booking_from_backoffice(self, authenticated_client, requests_mock):
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        ems_provider = get_provider_by_local_class("EMSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=ems_provider)
        providers_factories.CinemaProviderPivotFactory(venue=venue_provider.venue)
        offer = offers_factories.EventOfferFactory(
            name="Film",
            venue=venue_provider.venue,
            subcategoryId=subcategories_v2.SEANCE_CINE.id,
            lastProviderId=ems_provider.id,
        )
        stock = offers_factories.EventStockFactory(
            offer=offer,
            idAtProviders="1111%2222%EMS#3333",
            beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=2),
        )
        booking = bookings_factories.BookingFactory(stock=stock, user=beneficiary)
        external_bookings_factories.ExternalBookingFactory(
            booking=booking,
            barcode="123456789",
            additional_information={
                "num_cine": "9997",
                "num_caisse": "255",
                "num_trans": 1257,
                "num_ope": 147149,
            },
        )
        requests_mock.post(
            url=re.compile(r"https://fake_url.com/ANNULATION/*"),
            json={"code_erreur": 5, "message_erreur": "Erreur lors de l'appel au cinéma", "statut": 0},
        )

        assert booking.status is bookings_models.BookingStatus.CONFIRMED
        assert len(booking.externalBookings) == 1
        assert booking.externalBookings[0].barcode
        assert booking.externalBookings[0].seat
        assert booking.externalBookings[0].additional_information == {
            "num_cine": "9997",
            "num_caisse": "255",
            "num_trans": 1257,
            "num_ope": 147149,
        }

        old_quantity = stock.dnBookedQuantity

        response = self.post_to_endpoint(
            authenticated_client,
            booking_id=booking.id,
            form={"reason": bookings_models.BookingCancellationReasons.BACKOFFICE.value},
        )

        assert response.status_code == 303
        redirected_response = authenticated_client.get(response.headers["location"])
        assert html_parser.extract_alert(redirected_response.data) == f"La réservation {booking.token} a été annulée"

        db.session.refresh(booking)
        assert booking.status == bookings_models.BookingStatus.CANCELLED
        assert stock.dnBookedQuantity == old_quantity - 1
        assert booking.cancellationReason == bookings_models.BookingCancellationReasons.BACKOFFICE

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == "ems.support@example.com"
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.EXTERNAL_BOOKING_SUPPORT_CANCELLATION.value
        )
        assert mails_testing.outbox[0]["params"] == {
            "EXTERNAL_BOOKING_INFORMATION": "barcode: 123456789, additional_information: {'num_ope': 147149, 'num_cine': '9997', 'num_trans': 1257, 'num_caisse': '255'}"
        }

    def test_cancel_cgr_external_booking_unilaterally(self, authenticated_client, requests_mock):
        requests_mock.get(
            "https://cgr-cinema-0.example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION
        )
        requests_mock.post(
            "https://cgr-cinema-0.example.com/web_service",
            text=cgr_fixtures.cgr_annulation_response_template(
                success=False,
                message_error="L'annulation n'a pas pu être prise en compte : Code barre non reconnu / annulation impossible",
            ),
        )
        cgr_provider = get_provider_by_local_class("CGRStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cgr_provider)
        cinema_provider_pivot = providers_factories.CGRCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        providers_factories.CGRCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cgr-cinema-0.example.com/web_service"
        )

        offer = offers_factories.OfferFactory(
            lastProvider=cgr_provider,
            idAtProvider="123%12354114%CGR",
            subcategoryId=subcategories_v2.SEANCE_CINE.id,
            venue=venue_provider.venue,
        )
        stock = offers_factories.StockFactory(
            lastProvider=cgr_provider,
            idAtProviders="123%12354114%CGR#111",
            beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=2),
            offer=offer,
        )
        booking_to_cancel = bookings_factories.BookingFactory(stock=stock)
        external_bookings_factories.ExternalBookingFactory(booking=booking_to_cancel)

        response = self.post_to_endpoint(
            authenticated_client,
            booking_id=booking_to_cancel.id,
            form={"reason": bookings_models.BookingCancellationReasons.BACKOFFICE.value},
        )

        assert response.status_code == 303

        db.session.refresh(booking_to_cancel)
        assert booking_to_cancel.status == bookings_models.BookingStatus.CANCELLED
        assert booking_to_cancel.cancellationReason == bookings_models.BookingCancellationReasons.BACKOFFICE

        redirected_response = authenticated_client.get(response.headers["location"])

        assert (
            html_parser.extract_alert(redirected_response.data)
            == f"La réservation {booking_to_cancel.token} a été annulée"
        )


class GetBatchMarkAsUsedIndividualBookingsFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.individual_bookings.get_batch_validate_individual_bookings_form"
    needed_permission = perm_models.Permissions.MANAGE_BOOKINGS

    def test_get_batch_mark_as_used_booking_form(self, legit_user, authenticated_client):
        bookings_factories.BookingFactory()
        with assert_num_queries(2):  # session + tested_query
            response = authenticated_client.get(url_for(self.endpoint))
            # Rendering is not checked, but at least the fetched frame does not crash
            assert response.status_code == 200


class BatchMarkBookingAsUsedTest(PostEndpointHelper):
    endpoint = "backoffice_web.individual_bookings.batch_validate_individual_bookings"
    needed_permission = perm_models.Permissions.MANAGE_BOOKINGS

    def test_batch_mark_as_used_bookings(self, legit_user, authenticated_client):
        bookings = bookings_factories.BookingFactory.create_batch(3)
        parameter_ids = ",".join(str(booking.id) for booking in bookings)
        response = self.post_to_endpoint(authenticated_client, form={"object_ids": parameter_ids})

        assert response.status_code == 303
        for booking in bookings:
            db.session.refresh(booking)
            assert booking.status is bookings_models.BookingStatus.USED
            assert booking.validationAuthorType == bookings_models.BookingValidationAuthorType.BACKOFFICE

    def test_batch_mark_as_used_cancelled_bookings(self, legit_user, authenticated_client):
        bookings = bookings_factories.BookingFactory.create_batch(3, status=bookings_models.BookingStatus.CANCELLED)
        parameter_ids = ",".join(str(booking.id) for booking in bookings)
        response = self.post_to_endpoint(authenticated_client, form={"object_ids": parameter_ids})

        assert response.status_code == 303
        for booking in bookings:
            db.session.refresh(booking)
            assert booking.status is bookings_models.BookingStatus.USED
            assert booking.validationAuthorType == bookings_models.BookingValidationAuthorType.BACKOFFICE

    def test_batch_mark_as_used_bookings_with_expired_deposit(self, legit_user, authenticated_client):
        booking1 = bookings_factories.BookingFactory(
            status=bookings_models.BookingStatus.CANCELLED,
            deposit=users_factories.DepositGrantFactory(
                expirationDate=datetime.datetime.utcnow() - datetime.timedelta(days=1)
            ),
        )
        booking2 = bookings_factories.BookingFactory()
        parameter_ids = str(booking1.id) + "," + str(booking2.id)

        response = self.post_to_endpoint(authenticated_client, form={"object_ids": parameter_ids})

        redirected_response = authenticated_client.get(response.headers["location"])
        assert (
            f"La réservation {booking1.token} ne peut être validée, car le crédit associé est expiré."
            in html_parser.extract_alert(redirected_response.data)
        )


class GetBatchCancelIndividualBookingsFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.individual_bookings.get_batch_cancel_individual_bookings_form"
    needed_permission = perm_models.Permissions.MANAGE_BOOKINGS

    def test_get_batch_cancel_booking_form(self, legit_user, authenticated_client):
        bookings_factories.BookingFactory()
        with assert_num_queries(2):  # session + tested_query
            url = url_for(self.endpoint)
            response = authenticated_client.get(url)
            # Rendering is not checked, but at least the fetched frame does not crash
            assert response.status_code == 200


class BatchOfferCancelTest(PostEndpointHelper):
    endpoint = "backoffice_web.individual_bookings.batch_cancel_individual_bookings"
    needed_permission = perm_models.Permissions.MANAGE_BOOKINGS

    def test_batch_cancel_bookings(self, legit_user, authenticated_client):
        bookings = bookings_factories.BookingFactory.create_batch(3)
        parameter_ids = ",".join(str(booking.id) for booking in bookings)
        response = self.post_to_endpoint(
            authenticated_client,
            form={"object_ids": parameter_ids, "reason": bookings_models.BookingCancellationReasons.BACKOFFICE.value},
        )

        assert response.status_code == 303
        for booking in bookings:
            db.session.refresh(booking)
            assert booking.status is bookings_models.BookingStatus.CANCELLED
            assert booking.cancellationReason == bookings_models.BookingCancellationReasons.BACKOFFICE


class GetIndividualBookingCSVDownloadTest(GetEndpointHelper):
    endpoint = "backoffice_web.individual_bookings.get_individual_booking_csv_download"
    needed_permission = perm_models.Permissions.READ_BOOKINGS

    # session + current user + bookings
    expected_num_queries = 3

    def test_csv_length(self, authenticated_client, bookings):
        venue_id = bookings[0].venueId

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue=venue_id))
            assert response.status_code == 200

        assert len(response.data.split(b"\n")) == 4


class GetIndividualBookingXLSXDownloadTest(GetEndpointHelper):
    endpoint = "backoffice_web.individual_bookings.get_individual_booking_xlsx_download"
    needed_permission = perm_models.Permissions.READ_BOOKINGS

    # session + current user + bookings
    expected_num_queries = 3

    def reader_from_response(self, response):
        wb = openpyxl.load_workbook(BytesIO(response.data))
        return wb.active

    def test_csv_length(self, authenticated_client, bookings):
        venue_id = bookings[0].venueId

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue=venue_id))
            assert response.status_code == 200

        sheet = self.reader_from_response(response)
        assert sheet.cell(row=1, column=1).value == "Lieu"
        assert sheet.cell(row=2, column=1).value == bookings[0].venue.name
        assert sheet.cell(row=3, column=1).value == bookings[0].venue.name
        assert sheet.cell(row=4, column=1).value == None
