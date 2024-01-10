import datetime
import decimal
from unittest import mock

from flask import url_for
import pytest
import sqlalchemy as sa

from pcapi.core import testing
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import factories as educational_factories
from pcapi.core.finance import api
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import utils as finance_utils
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice.filters import format_booking_status
from pcapi.routes.backoffice.filters import format_date_time
from pcapi.routes.backoffice.finance import forms as finance_forms

from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


@pytest.fixture(scope="function", name="invoiced_pricing")
def invoiced_pricing_fixture() -> list:
    return finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED, amount=-1000)


@pytest.fixture(scope="function", name="invoiced_collective_pricing")
def invoiced_collective_pricing_fixture() -> list:
    return finance_factories.CollectivePricingFactory(status=finance_models.PricingStatus.INVOICED)


class ListIncidentsTest(GetEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.list_incidents"
    needed_permission = perm_models.Permissions.READ_INCIDENTS

    expected_num_queries = 0
    expected_num_queries += 1  # Fetch Session
    expected_num_queries += 1  # Fetch User
    expected_num_queries += 1  # Fetch Finance Incidents

    def test_list_incidents_without_filter(self, authenticated_client):
        incidents = finance_factories.FinanceIncidentFactory.create_batch(10)

        url = url_for(self.endpoint)

        with testing.assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == len(incidents)
        last_created_incident = incidents[-1]
        assert rows[0]["ID"] == str(last_created_incident.id)
        assert rows[0]["Statut de l'incident"] == "Créé"
        assert rows[0]["Type d'incident"] == "Trop Perçu"


class GetIncidentCancellationFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.get_finance_incident_cancellation_form"
    endpoint_kwargs = {"finance_incident_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_INCIDENTS

    def test_get_incident_cancellation_form(self, legit_user, authenticated_client):
        incident = finance_factories.FinanceIncidentFactory()
        url = url_for(self.endpoint, finance_incident_id=incident.id)
        response = authenticated_client.get(url)

        assert response.status_code == 200


class GetIncidentValidationFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.get_finance_incident_validation_form"
    endpoint_kwargs = {"finance_incident_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_INCIDENTS

    expected_num_queries = 2
    expected_num_queries += 1  # get incident info

    def test_get_incident_validation_form(self, authenticated_client):
        booking_incident = finance_factories.IndividualBookingFinanceIncidentFactory()
        url = url_for(self.endpoint, finance_incident_id=booking_incident.incident.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        text_content = html_parser.content_as_text(response.data)
        assert (
            f"Vous allez valider un incident de {filters.format_amount(finance_utils.to_euros(booking_incident.incident.due_amount_by_offerer))} "
            f"sur le point de remboursement {booking_incident.incident.venue.name}." in text_content
        )

    def test_no_script_injection_in_venue_name(self, authenticated_client):
        venue = offerers_factories.VenueFactory(name="<script>alert('coucou')</script>")
        booking_incident = finance_factories.IndividualBookingFinanceIncidentFactory(incident__venue=venue)
        url = url_for(self.endpoint, finance_incident_id=booking_incident.incident.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        text_content = html_parser.content_as_text(response.data)
        assert (
            f"Vous allez valider un incident de {filters.format_amount(finance_utils.to_euros(booking_incident.incident.due_amount_by_offerer))} "
            f"sur le point de remboursement {venue.name}." in text_content
        )


class CancelIncidentTest(PostEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.cancel_finance_incident"
    endpoint_kwargs = {"finance_incident_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_INCIDENTS

    def test_cancel_incident(self, legit_user, authenticated_client):
        incident = finance_factories.FinanceIncidentFactory()
        self.form_data = {"comment": "L'incident n'est pas conforme"}

        response = self.post_to_endpoint(authenticated_client, finance_incident_id=incident.id, form=self.form_data)

        assert response.status_code == 200

        assert (
            finance_models.FinanceIncident.query.filter(
                finance_models.FinanceIncident.status == finance_models.IncidentStatus.CREATED
            ).count()
            == 0
        )

        badges = html_parser.extract(response.data, tag="span", class_="badge")
        assert "Annulé" in badges

        action_history = history_models.ActionHistory.query.one()
        assert action_history.actionType == history_models.ActionType.FINANCE_INCIDENT_CANCELLED
        assert action_history.authorUser == legit_user
        assert action_history.comment == self.form_data["comment"]

    def test_cancel_already_cancelled_incident(self, authenticated_client):
        incident = finance_factories.FinanceIncidentFactory(status=finance_models.IncidentStatus.CANCELLED)
        self.form_data = {"comment": "L'incident n'est pas conforme"}

        response = self.post_to_endpoint(authenticated_client, finance_incident_id=incident.id, form=self.form_data)

        assert response.status_code == 200

        assert "L'incident a déjà été annulé" in html_parser.extract_alert(response.data)
        assert history_models.ActionHistory.query.count() == 0

    def test_cancel_already_validated_incident(self, authenticated_client):
        incident = finance_factories.FinanceIncidentFactory(status=finance_models.IncidentStatus.VALIDATED)
        self.form_data = {"comment": "L'incident n'est pas conforme"}

        response = self.post_to_endpoint(authenticated_client, finance_incident_id=incident.id, form=self.form_data)

        assert response.status_code == 200

        assert "Impossible d'annuler un incident déjà validé" in html_parser.extract_alert(response.data)
        assert history_models.ActionHistory.query.count() == 0


class ValidateIncidentTest(PostEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.validate_finance_incident"
    endpoint_kwargs = {"finance_incident_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_INCIDENTS

    @pytest.mark.parametrize("force_debit_note", [True, False])
    def test_validate_incident(self, authenticated_client, force_debit_note):
        booking_incident = finance_factories.IndividualBookingFinanceIncidentFactory(
            booking__pricings=[
                finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED, amount=-1000)
            ],
            booking__amount=10.10,
            newTotalAmount=0,
        )

        response = self.post_to_endpoint(
            authenticated_client,
            finance_incident_id=booking_incident.incident.id,
            form={
                "compensation_mode": finance_forms.IncidentCompensationModes.FORCE_DEBIT_NOTE.name
                if force_debit_note
                else finance_forms.IncidentCompensationModes.COMPENSATE_ON_BOOKINGS.name
            },
        )

        assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert "L'incident a été validé avec succès." in content

        updated_incident = finance_models.FinanceIncident.query.get(booking_incident.incidentId)
        assert updated_incident.status == finance_models.IncidentStatus.VALIDATED
        assert updated_incident.forceDebitNote == force_debit_note

        beneficiary_action = history_models.ActionHistory.query.filter(
            history_models.ActionHistory.user == booking_incident.beneficiary
        ).first()
        validation_action = history_models.ActionHistory.query.filter(
            history_models.ActionHistory.financeIncident == updated_incident
        ).first()

        assert validation_action
        assert validation_action.actionType == history_models.ActionType.FINANCE_INCIDENT_VALIDATED
        assert (
            validation_action.comment == "Génération d'une note de débit à la prochaine échéance."
            if force_debit_note
            else "Récupération sur les prochaines réservations."
        )

        assert (
            beneficiary_action
            and beneficiary_action.actionType == history_models.ActionType.FINANCE_INCIDENT_USER_RECREDIT
        )

        finance_events = finance_models.FinanceEvent.query.all()
        assert len(finance_events) == 1
        assert finance_events[0].motive == finance_models.FinanceEventMotive.INCIDENT_REVERSAL_OF_ORIGINAL_EVENT

    @pytest.mark.parametrize("force_debit_note", [True, False])
    def test_incident_validation_with_several_bookings(self, authenticated_client, force_debit_note):
        deposit = users_factories.DepositGrantFactory()
        incident = finance_factories.FinanceIncidentFactory()

        assert incident.status == finance_models.IncidentStatus.CREATED

        booking_reimbursed = bookings_factories.ReimbursedBookingFactory(
            deposit=deposit,
            amount=30,
            user=deposit.user,
            pricings=[finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED, amount=-3000)],
        )
        booking_reimbursed_2 = bookings_factories.ReimbursedBookingFactory(
            deposit=deposit,
            amount=40,
            user=deposit.user,
            pricings=[finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED, amount=-4000)],
        )
        bookings_factories.BookingFactory(deposit=deposit, amount=20, user=deposit.user)

        finance_factories.IndividualBookingFinanceIncidentFactory(
            booking=booking_reimbursed,
            incident=incident,
            newTotalAmount=finance_utils.to_eurocents(booking_reimbursed.pricings[0].amount),
        )  # total incident

        finance_factories.IndividualBookingFinanceIncidentFactory(
            booking=booking_reimbursed_2, incident=incident, newTotalAmount=3000
        )  # partiel incident : instead of 40, 10 go back to the deposit

        response = self.post_to_endpoint(
            authenticated_client,
            finance_incident_id=incident.id,
            form={
                "compensation_mode": finance_forms.IncidentCompensationModes.FORCE_DEBIT_NOTE.name
                if force_debit_note
                else finance_forms.IncidentCompensationModes.COMPENSATE_ON_BOOKINGS.name
            },
        )

        assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert "L'incident a été validé avec succès." in content

        assert incident.status == finance_models.IncidentStatus.VALIDATED
        assert incident.forceDebitNote == force_debit_note

        validation_action = history_models.ActionHistory.query.filter(
            history_models.ActionHistory.financeIncident == incident
        ).first()

        assert validation_action
        assert validation_action.actionType == history_models.ActionType.FINANCE_INCIDENT_VALIDATED
        assert (
            validation_action.comment == "Génération d'une note de débit à la prochaine échéance."
            if force_debit_note
            else "Récupération sur les prochaines réservations."
        )
        assert db.session.query(sa.func.get_deposit_balance(deposit.id, False)).first()[0] == 250
        assert db.session.query(sa.func.get_deposit_balance(deposit.id, True)).first()[0] == 270

        assert booking_reimbursed.status == bookings_models.BookingStatus.CANCELLED
        assert booking_reimbursed_2.status == bookings_models.BookingStatus.REIMBURSED

        finance_events = finance_models.FinanceEvent.query.all()
        assert len(finance_events) == 3

        # total finance incident
        assert finance_events[0].motive == finance_models.FinanceEventMotive.INCIDENT_REVERSAL_OF_ORIGINAL_EVENT

        # partial finaance incident
        assert finance_events[1].motive == finance_models.FinanceEventMotive.INCIDENT_REVERSAL_OF_ORIGINAL_EVENT
        assert finance_events[2].motive == finance_models.FinanceEventMotive.INCIDENT_NEW_PRICE

    @pytest.mark.parametrize(
        "initial_status", [finance_models.IncidentStatus.CANCELLED, finance_models.IncidentStatus.VALIDATED]
    )
    def test_not_validate_incident(self, authenticated_client, initial_status):
        finance_incident = finance_factories.FinanceIncidentFactory(status=initial_status)

        response = self.post_to_endpoint(
            authenticated_client,
            finance_incident_id=finance_incident.id,
            form={"compensation_mode": finance_forms.IncidentCompensationModes.COMPENSATE_ON_BOOKINGS.name},
        )

        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "L'incident ne peut être validé que s'il est au statut 'créé'."
        )
        finance_incident = finance_models.FinanceIncident.query.get(finance_incident.id)
        assert finance_incident.status == initial_status
        assert finance_models.FinanceEvent.query.count() == 0


class CreateIncidentFinanceEventTest:
    @pytest.mark.parametrize(
        "incident_type",
        [
            finance_models.IncidentType.OVERPAYMENT,
            finance_models.IncidentType.OFFER_PRICE_REGULATION,
            finance_models.IncidentType.FRAUD,
        ],
    )
    def test_create_event_on_total_booking_incident(self, incident_type):
        total_booking_incident = finance_factories.IndividualBookingFinanceIncidentFactory(
            booking__pricings=[
                finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED, amount=-1000)
            ],
            booking__amount=10.10,
            incident__kind=incident_type,
            newTotalAmount=0,
        )
        validation_date = datetime.datetime.utcnow()
        finance_events = api._create_finance_events_from_incident(total_booking_incident, validation_date)

        assert len(finance_events) == 1
        assert finance_events[0].bookingFinanceIncidentId == total_booking_incident.id
        assert finance_events[0].status == finance_models.FinanceEventStatus.PENDING
        assert finance_events[0].venue and finance_events[0].venue == total_booking_incident.booking.venue
        assert finance_events[0].motive == finance_models.FinanceEventMotive.INCIDENT_REVERSAL_OF_ORIGINAL_EVENT
        assert finance_events[0].valueDate == validation_date

    @pytest.mark.parametrize(
        "incident_type",
        [
            finance_models.IncidentType.OVERPAYMENT,
            finance_models.IncidentType.OFFER_PRICE_REGULATION,
            finance_models.IncidentType.FRAUD,
        ],
    )
    def test_create_event_on_total_collective_booking_incident(self, incident_type):
        total_booking_incident = finance_factories.CollectiveBookingFinanceIncidentFactory(
            collectiveBooking__pricings=[
                finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED, amount=-10000)
            ],
            incident__kind=incident_type,
        )

        validation_date = datetime.datetime.utcnow()
        finance_events = api._create_finance_events_from_incident(total_booking_incident, validation_date)

        assert len(finance_events) == 1

        assert finance_events[0].bookingFinanceIncidentId == total_booking_incident.id
        assert finance_events[0].status == finance_models.FinanceEventStatus.PENDING
        assert finance_events[0].venue and finance_events[0].venue == total_booking_incident.collectiveBooking.venue
        assert finance_events[0].motive == finance_models.FinanceEventMotive.INCIDENT_REVERSAL_OF_ORIGINAL_EVENT
        assert finance_events[0].valueDate == validation_date

    @pytest.mark.parametrize(
        "incident_type",
        [
            finance_models.IncidentType.OVERPAYMENT,
            finance_models.IncidentType.OFFER_PRICE_REGULATION,
            finance_models.IncidentType.FRAUD,
        ],
    )
    def test_create_event_on_partial_booking_incident(self, incident_type):
        partial_booking_incident = finance_factories.IndividualBookingFinanceIncidentFactory(
            booking__pricings=[
                finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED, amount=-1000)
            ],
            incident__kind=incident_type,
            newTotalAmount=600,
        )

        validation_date = datetime.datetime.utcnow()
        finance_events = api._create_finance_events_from_incident(partial_booking_incident, validation_date)

        assert len(finance_events) == 2

        assert finance_events[0].bookingFinanceIncidentId == partial_booking_incident.id
        assert finance_events[0].status == finance_models.FinanceEventStatus.PENDING
        assert finance_events[0].venue and finance_events[0].venue == partial_booking_incident.booking.venue
        assert finance_events[0].motive == finance_models.FinanceEventMotive.INCIDENT_REVERSAL_OF_ORIGINAL_EVENT
        assert finance_events[0].valueDate == validation_date

        assert finance_events[1].bookingFinanceIncidentId == partial_booking_incident.id
        assert finance_events[1].status == finance_models.FinanceEventStatus.PENDING
        assert finance_events[1].venue and finance_events[0].venue == partial_booking_incident.booking.venue
        assert finance_events[1].motive == finance_models.FinanceEventMotive.INCIDENT_NEW_PRICE
        assert finance_events[1].valueDate == validation_date

    def test_create_commercial_gesture_event_on_booking(self):
        booking_incident = finance_factories.IndividualBookingFinanceIncidentFactory(
            booking__pricings=[
                finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED, amount=-1000)
            ],
            incident__kind=finance_models.IncidentType.COMMERCIAL_GESTURE,
            newTotalAmount=800,
        )
        validation_date = datetime.datetime.utcnow()

        finance_events = api._create_finance_events_from_incident(booking_incident, validation_date)

        assert len(finance_events) == 1

        assert finance_events[0].bookingFinanceIncidentId == booking_incident.id
        assert finance_events[0].status == finance_models.FinanceEventStatus.PENDING
        assert finance_events[0].venue and finance_events[0].venue == booking_incident.booking.venue
        assert finance_events[0].motive == finance_models.FinanceEventMotive.INCIDENT_COMMERCIAL_GESTURE
        assert finance_events[0].valueDate == validation_date


class GetIncidentTest(GetEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.get_incident"
    endpoint_kwargs = {"finance_incident_id": 1}
    needed_permission = perm_models.Permissions.READ_INCIDENTS
    expected_num_queries = 0
    expected_num_queries += 1  # Fetch Session
    expected_num_queries += 1  # Fetch User
    expected_num_queries += 1  # Fetch Incidents infos
    expected_num_queries += 1  # Fetch Reimbursement point infos

    def test_get_incident(self, authenticated_client, finance_incident):
        url = url_for(self.endpoint, finance_incident_id=finance_incident.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)

        assert f"ID : {finance_incident.id}" in content
        assert f"Lieu porteur de l'offre : {finance_incident.venue.name}" in content
        assert f"Incident créé par : {finance_incident.details['author']}" in content

    def test_get_collective_booking_incident(self, authenticated_client):
        finance_incident = finance_factories.FinanceIncidentFactory(
            booking_finance_incidents=[finance_factories.CollectiveBookingFinanceIncidentFactory()]
        )
        url = url_for(self.endpoint, finance_incident_id=finance_incident.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)

        assert f"ID : {finance_incident.id}" in content
        assert f"Lieu porteur de l'offre : {finance_incident.venue.name}" in content
        assert f"Incident créé par : {finance_incident.details['author']}" in content


class GetIncidentCreationFormTest(PostEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.get_incident_creation_form"
    needed_permission = perm_models.Permissions.MANAGE_INCIDENTS

    error_message = 'Seules les réservations ayant les statuts "remboursée" et "annulée" et correspondant au même lieu peuvent faire l\'objet d\'un incident'

    expected_num_queries = 6

    def test_get_incident_creation_for_one_booking_form(self, authenticated_client, invoiced_pricing):
        venue = offerers_factories.VenueFactory()
        offer = offers_factories.OfferFactory(venue=venue)
        stock = offers_factories.StockFactory(offer=offer)
        booking = bookings_factories.ReimbursedBookingFactory(stock=stock, pricings=[invoiced_pricing])
        object_ids = str(booking.id)

        with assert_num_queries(self.expected_num_queries):
            response = self.post_to_endpoint(authenticated_client, form={"object_ids": object_ids})
            assert response.status_code == 200

        additional_data_text = html_parser.extract_cards_text(response.data)[0]
        assert f"Lieu : {venue.name}" in additional_data_text
        assert f"ID de la réservation : {booking.id}" in additional_data_text
        assert f"Statut de la réservation : {format_booking_status(booking)}" in additional_data_text
        assert f"Contremarque : {booking.token}" in additional_data_text
        assert f"Nom de l'offre : {offer.name}" in additional_data_text
        assert f"Bénéficiaire : {booking.user.full_name}" in additional_data_text
        assert f"Montant de la réservation : {filters.format_amount(booking.total_amount)}" in additional_data_text
        assert (
            f"Montant remboursé à l'acteur : {filters.format_amount(finance_utils.to_euros(-invoiced_pricing.amount))}"
            in additional_data_text
        )

        default_amount = html_parser.extract_input_value(response.data, "total_amount")
        assert default_amount == str(booking.total_amount)

    def test_get_incident_creation_for_multiple_bookings_form(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        offer = offers_factories.OfferFactory(venue=venue)
        stock = offers_factories.StockFactory(offer=offer)
        selected_bookings = [
            bookings_factories.ReimbursedBookingFactory(
                stock=stock, pricings=[finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED)]
            ),
            bookings_factories.ReimbursedBookingFactory(
                stock=stock, pricings=[finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED)]
            ),
        ]
        object_ids = ",".join([str(booking.id) for booking in selected_bookings])

        with assert_num_queries(self.expected_num_queries):
            response = self.post_to_endpoint(authenticated_client, form={"object_ids": object_ids})
            assert response.status_code == 200

        additional_data_text = html_parser.extract_cards_text(response.data)[0]
        assert f"Lieu : {venue.name}" in additional_data_text
        assert f"Nombre de réservations : {len(selected_bookings)}" in additional_data_text
        assert (
            f"Montant des réservations : {filters.format_amount(sum(booking.total_amount for booking in selected_bookings))}"
            in additional_data_text
        )
        assert (
            f"Montant remboursé à l'acteur : {filters.format_amount(finance_utils.to_euros(-sum(booking.reimbursement_pricing.amount for booking in selected_bookings)))}"
            in additional_data_text
        )

    def test_display_error_if_booking_not_reimbursed(self, authenticated_client):
        booking = bookings_factories.UsedBookingFactory()
        object_ids = str(booking.id)

        with assert_num_queries(self.expected_num_queries):
            response = self.post_to_endpoint(authenticated_client, form={"object_ids": object_ids})

        assert self.error_message in html_parser.content_as_text(response.data)

    def test_display_error_if_bookings_from_different_venues_selected(self, authenticated_client):
        selected_bookings = [
            bookings_factories.ReimbursedBookingFactory(),
            bookings_factories.ReimbursedBookingFactory(),
        ]
        object_ids = ",".join(str(booking.id) for booking in selected_bookings)

        with assert_num_queries(self.expected_num_queries):
            response = self.post_to_endpoint(authenticated_client, form={"object_ids": object_ids})

        assert self.error_message in html_parser.content_as_text(response.data)


class GetCollectiveBookingIncidentFormTest(PostEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.get_collective_booking_incident_creation_form"
    endpoint_kwargs = {"collective_booking_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_INCIDENTS

    expected_num_queries = 10

    def test_get_form(self, authenticated_client, invoiced_collective_pricing):
        collective_booking = educational_factories.ReimbursedCollectiveBookingFactory(
            pricings=[invoiced_collective_pricing]
        )

        with assert_num_queries(self.expected_num_queries):
            response = self.post_to_endpoint(authenticated_client, collective_booking_id=collective_booking.id)
            assert response.status_code == 200

        additional_data_text = html_parser.extract_cards_text(response.data)[0]

        assert f"ID de la réservation : {collective_booking.id}" in additional_data_text
        assert "Statut de la réservation : Remboursée" in additional_data_text
        assert f"Nom de l'offre : {collective_booking.collectiveStock.collectiveOffer.name}" in additional_data_text
        assert (
            f"Date de l'offre : {format_date_time(collective_booking.collectiveStock.beginningDatetime)}"
            in additional_data_text
        )
        assert f"Établissement : {collective_booking.educationalInstitution.name}" in additional_data_text
        assert f"Nombre d'élèves : {collective_booking.collectiveStock.numberOfTickets}" in additional_data_text
        assert (
            f"Montant de la réservation : {filters.format_amount(collective_booking.total_amount)}"
            in additional_data_text
        )
        assert (
            f"Montant remboursé à l'acteur : {filters.format_amount(finance_utils.to_euros(-collective_booking.reimbursement_pricing.amount))}"
            in additional_data_text
        )


class CreateIncidentTest(PostEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.create_individual_booking_incident"
    needed_permission = perm_models.Permissions.MANAGE_INCIDENTS

    def test_create_incident_from_one_booking(self, legit_user, authenticated_client, invoiced_pricing):
        booking = bookings_factories.ReimbursedBookingFactory(pricings=[invoiced_pricing])

        object_ids = str(booking.id)

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "total_amount": booking.amount,
                "origin": "Origine de la demande",
                "kind": finance_models.IncidentType.OVERPAYMENT.name,
                "object_ids": object_ids,
            },
        )

        assert response.status_code == 303
        assert finance_models.FinanceIncident.query.count() == 1
        assert finance_models.BookingFinanceIncident.query.count() == 1
        booking_finance_incident = finance_models.BookingFinanceIncident.query.first()
        assert booking_finance_incident.newTotalAmount == 0

        action_history = history_models.ActionHistory.query.one()
        assert action_history.actionType == history_models.ActionType.FINANCE_INCIDENT_CREATED
        assert action_history.authorUser == legit_user
        assert action_history.comment == "Origine de la demande"

    def test_not_creating_incident_if_already_exists(self, authenticated_client):
        booking = bookings_factories.ReimbursedBookingFactory()
        finance_factories.IndividualBookingFinanceIncidentFactory(booking=booking)
        object_ids = str(booking.id)

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "total_amount": booking.amount,
                "origin": "Origine de la demande",
                "kind": finance_models.IncidentType.OVERPAYMENT.name,
                "object_ids": object_ids,
            },
        )

        assert response.status_code == 303
        assert finance_models.FinanceIncident.query.count() == 1  # didn't create new incident

        assert history_models.ActionHistory.query.count() == 0

    def test_create_incident_from_multiple_booking(self, legit_user, authenticated_client, invoiced_pricing):
        venue = offerers_factories.VenueFactory()
        offer = offers_factories.OfferFactory(venue=venue)
        stock = offers_factories.StockFactory(offer=offer)
        selected_bookings = [
            bookings_factories.ReimbursedBookingFactory(
                stock=stock, pricings=[finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED)]
            ),
            bookings_factories.ReimbursedBookingFactory(
                stock=stock, pricings=[finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED)]
            ),
        ]
        object_ids = ",".join([str(booking.id) for booking in selected_bookings])
        total_booking_amount = sum(booking.amount for booking in selected_bookings)

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "total_amount": total_booking_amount,
                "origin": "Origine de la demande",
                "kind": finance_models.IncidentType.OVERPAYMENT.name,
                "object_ids": object_ids,
            },
        )

        assert response.status_code == 303
        assert finance_models.FinanceIncident.query.count() == 1
        finance_incident = finance_models.FinanceIncident.query.first()
        assert finance_incident.details["origin"] == "Origine de la demande"
        assert finance_models.BookingFinanceIncident.query.count() == 2

        action_history = history_models.ActionHistory.query.one()
        assert action_history.actionType == history_models.ActionType.FINANCE_INCIDENT_CREATED
        assert action_history.authorUser == legit_user
        assert action_history.comment == "Origine de la demande"

    def test_not_create_overpayment_incident_from_used_booking(self, authenticated_client):
        booking = bookings_factories.UsedBookingFactory()

        object_ids = str(booking.id)

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "total_amount": booking.amount,
                "origin": "Origine de la demande",
                "kind": finance_models.IncidentType.OVERPAYMENT.name,
                "object_ids": object_ids,
            },
        )

        assert response.status_code == 303
        assert finance_models.FinanceIncident.query.count() == 0  # didn't create new incident
        assert history_models.ActionHistory.query.count() == 0

    def test_create_comercial_gesture_incident_from_one_booking_without_deposit_balance(
        self, legit_user, authenticated_client
    ):
        booking = bookings_factories.CancelledBookingFactory(user__deposit__amount=decimal.Decimal(2.0))

        object_ids = str(booking.id)
        total_amount = 11
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "total_amount": total_amount,
                "origin": "Origine de la demande",
                "kind": finance_models.IncidentType.COMMERCIAL_GESTURE.name,
                "object_ids": object_ids,
            },
        )

        assert response.status_code == 303
        assert finance_models.FinanceIncident.query.count() == 1
        assert finance_models.BookingFinanceIncident.query.count() == 1
        booking_finance_incident = finance_models.BookingFinanceIncident.query.first()
        assert booking_finance_incident.newTotalAmount == (total_amount) * 100

        action_history = history_models.ActionHistory.query.one()
        assert action_history.actionType == history_models.ActionType.FINANCE_INCIDENT_CREATED
        assert action_history.authorUser == legit_user
        assert action_history.comment == "Origine de la demande"

    def test_create_comercial_gesture_incident_from_one_booking_with_deposit_balance(
        self, legit_user, authenticated_client
    ):
        booking = bookings_factories.CancelledBookingFactory()

        object_ids = str(booking.id)
        total_amount = 11
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "total_amount": total_amount,
                "origin": "Origine de la demande",
                "kind": finance_models.IncidentType.COMMERCIAL_GESTURE.name,
                "object_ids": object_ids,
            },
        )

        assert response.status_code == 303
        assert finance_models.FinanceIncident.query.count() == 0
        assert finance_models.BookingFinanceIncident.query.count() == 0

        redirected_response = authenticated_client.get(response.location)
        assert (
            "Au moins un des jeunes ayant fait une réservation a encore du crédit pour payer la réservation"
            in html_parser.extract_alert(redirected_response.data)
        )

    def test_create_comercial_gesture_incident_from_used_booking(self, legit_user, authenticated_client):
        booking = bookings_factories.UsedBookingFactory()

        object_ids = str(booking.id)
        total_amount = 11
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "total_amount": total_amount,
                "origin": "Origine de la demande",
                "kind": finance_models.IncidentType.COMMERCIAL_GESTURE.name,
                "object_ids": object_ids,
            },
        )

        assert response.status_code == 303
        assert finance_models.FinanceIncident.query.count() == 0
        assert finance_models.BookingFinanceIncident.query.count() == 0

        redirected_response = authenticated_client.get(response.location)
        assert (
            "Au moins une des réservations sélectionnées est dans un état non compatible avec ce type d'incident"
            in html_parser.extract_alert(redirected_response.data)
        )

    def test_not_create_comercial_gesture_incident_too_expensive(self, authenticated_client):
        booking = bookings_factories.UsedBookingFactory()

        object_ids = str(booking.id)

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "total_amount": booking.amount * decimal.Decimal(1.21),
                "origin": "Origine de la demande",
                "kind": finance_models.IncidentType.COMMERCIAL_GESTURE.name,
                "object_ids": object_ids,
            },
        )

        assert response.status_code == 303
        assert finance_models.FinanceIncident.query.count() == 0  # didn't create new incident
        assert history_models.ActionHistory.query.count() == 0

    def test_not_create_commercial_gesture_greater_than_300_per_booking(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        offer = offers_factories.OfferFactory(venue=venue)
        stock = offers_factories.StockFactory(offer=offer)
        selected_bookings = [
            bookings_factories.ReimbursedBookingFactory(
                stock=stock,
                pricings=[finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED)],
                amount=300.0,
            ),
            bookings_factories.ReimbursedBookingFactory(
                stock=stock,
                pricings=[finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED)],
                amount=300.0,
            ),
        ]
        object_ids = ",".join([str(booking.id) for booking in selected_bookings])
        total_booking_amount = 301.0 * len(selected_bookings)

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "total_amount": total_booking_amount,
                "origin": "Origine de la demande",
                "kind": finance_models.IncidentType.COMMERCIAL_GESTURE.name,
                "object_ids": object_ids,
            },
        )

        assert response.status_code == 303
        assert finance_models.FinanceIncident.query.count() == 0  # didn't create new incident
        assert history_models.ActionHistory.query.count() == 0


class CreateIncidentOnCollectiveBookingTest(PostEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.create_collective_booking_incident"
    endpoint_kwargs = {"collective_booking_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_INCIDENTS

    def test_create_incident(self, authenticated_client, invoiced_collective_pricing):
        collective_booking = educational_factories.ReimbursedCollectiveBookingFactory(
            pricings=[invoiced_collective_pricing]
        )

        response = self.post_to_endpoint(
            authenticated_client,
            form={"origin": "Demande E-mail", "kind": finance_models.IncidentType.OVERPAYMENT.name},
            collective_booking_id=collective_booking.id,
        )

        assert response.status_code == 303

        finance_incidents = finance_models.FinanceIncident.query.all()
        assert len(finance_incidents) == 1
        assert finance_incidents[0].details["origin"] == "Demande E-mail"
        assert finance_incidents[0].kind == finance_models.IncidentType.OVERPAYMENT

        booking_incidents = finance_incidents[0].booking_finance_incidents
        assert len(booking_incidents) == 1
        assert booking_incidents[0].collectiveBookingId == collective_booking.id
        assert booking_incidents[0].newTotalAmount == 0

    @pytest.mark.parametrize(
        "incident_status,expect_incident_creation",
        [
            (finance_models.IncidentStatus.CREATED, False),
            (finance_models.IncidentStatus.VALIDATED, False),
            (finance_models.IncidentStatus.CANCELLED, True),
        ],
    )
    def test_incident_already_exists(
        self, authenticated_client, incident_status, expect_incident_creation, invoiced_collective_pricing
    ):
        collective_booking = educational_factories.ReimbursedCollectiveBookingFactory(
            pricings=[invoiced_collective_pricing]
        )
        finance_factories.CollectiveBookingFinanceIncidentFactory(
            collectiveBooking=collective_booking, incident__status=incident_status
        )

        response = self.post_to_endpoint(
            authenticated_client,
            form={"origin": "Demande E-mail", "kind": finance_models.IncidentType.OVERPAYMENT.name},
            collective_booking_id=collective_booking.id,
        )

        assert response.status_code == 303
        incident_expected_count = 2 if expect_incident_creation else 1
        assert finance_models.FinanceIncident.query.count() == incident_expected_count


class GetIncidentHistoryTest(GetEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.get_history"
    endpoint_kwargs = {"finance_incident_id": 1}
    needed_permission = perm_models.Permissions.READ_INCIDENTS

    # session + current user + incident data
    expected_num_queries = 3

    def test_get_incident_history(self, legit_user, authenticated_client):
        finance_incident = finance_factories.FinanceIncidentFactory()
        action = history_factories.ActionHistoryFactory(
            financeIncident=finance_incident,
            actionType=history_models.ActionType.FINANCE_INCIDENT_CREATED,
            actionDate=datetime.datetime.utcnow() + datetime.timedelta(days=-1),
        )
        api.cancel_finance_incident(finance_incident, comment="Je décide d'annuler l'incident")

        finance_incident_id = finance_incident.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, finance_incident_id=finance_incident_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        iterator_actions = iter(rows)
        cancel_action = next(iterator_actions)
        creation_action = next(iterator_actions)
        assert cancel_action["Type"] == history_models.ActionType.FINANCE_INCIDENT_CANCELLED.value
        assert creation_action["Type"] == history_models.ActionType.FINANCE_INCIDENT_CREATED.value
        assert creation_action["Date/Heure"].startswith(action.actionDate.strftime("Le %d/%m/%Y à "))
        assert creation_action["Commentaire"] == action.comment
        assert creation_action["Auteur"] == action.authorUser.full_name


class GetInvoiceGenerationTest(GetEndpointHelper):
    endpoint = "backoffice_web.finance_invoices.get_finance_invoices"
    needed_permission = perm_models.Permissions.GENERATE_INVOICES
    # Fetch Session
    # Fetch User
    # Fetch CashflowBatches
    expected_num_queries = 3

    @pytest.mark.parametrize(
        "last_cashflow_status,is_queue_empty,expected_texts,unexpected_texts",
        [
            (
                finance_models.CashflowStatus.UNDER_REVIEW,
                True,
                [
                    "Derniers justificatifs créés",
                    "VIR1",
                    "entre le 01/01/2023 et le 15/01/2023",
                    "Prochains justificatifs générés",
                    "VIR2",
                    "entre le 16/01/2023 et le 31/01/2023 ",
                    "Générer les justificatifs",
                ],
                ["Il reste 11 justificatifs sur 40 à générer"],
            ),
            (
                finance_models.CashflowStatus.UNDER_REVIEW,
                False,
                [
                    "Derniers justificatifs créés",
                    "VIR1",
                    "entre le 01/01/2023 et le 15/01/2023",
                    "Justificatifs en cours de génération",
                    "VIR2",
                    "entre le 16/01/2023 et le 31/01/2023 ",
                    "Il reste 11 justificatifs sur 40 à générer",
                    "Une tâche est déjà en cours pour générer les justificatifs",
                ],
                [],
            ),
            (
                finance_models.CashflowStatus.ACCEPTED,
                True,
                [
                    "Derniers justificatifs créés",
                    "VIR2",
                    "entre le 16/01/2023 et le 31/01/2023",
                    "Il n'y a pas de justificatifs à générer pour le moment",
                ],
                ["VIR1", "entre le 01/01/2023 et le 15/01/2023", "Il reste 11 justificatifs sur 40 à générer"],
            ),
        ],
    )
    # with mock.patch("flask.current_app.redis_client", self.mock_redis_client):
    def test_get_invoices_generation(
        self, authenticated_client, last_cashflow_status, is_queue_empty, expected_texts, unexpected_texts
    ):
        user_offerer = offerers_factories.UserOffererFactory()
        pro_reimbursement_point1 = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, reimbursement_point="self"
        )
        finance_factories.BankInformationFactory(venue=pro_reimbursement_point1)
        finance_factories.CashflowFactory(
            status=finance_models.CashflowStatus.ACCEPTED,
            reimbursementPoint=pro_reimbursement_point1,
            bankInformation=pro_reimbursement_point1.bankInformation,
            amount=-2500,
            batch=finance_factories.CashflowBatchFactory(label="VIR1", cutoff=datetime.datetime(2023, 1, 15)),
        )

        user_offerer = offerers_factories.UserOffererFactory()
        pro_reimbursement_point1 = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, reimbursement_point="self"
        )
        finance_factories.BankInformationFactory(venue=pro_reimbursement_point1)
        finance_factories.CashflowFactory(
            status=last_cashflow_status,
            reimbursementPoint=pro_reimbursement_point1,
            bankInformation=pro_reimbursement_point1.bankInformation,
            amount=-1500,
            batch=finance_factories.CashflowBatchFactory(label="VIR2", cutoff=datetime.datetime(2023, 1, 31)),
        )

        with mock.patch("pcapi.tasks.finance_tasks.is_generate_invoices_queue_empty") as queue_empty_mock, mock.patch(
            "flask.current_app.redis_client.get"
        ) as redis_client_get_mock:
            queue_empty_mock.return_value = is_queue_empty
            redis_client_get_mock.side_effect = [40, 11] if not is_queue_empty else [None, None]

            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(url_for(self.endpoint))
                assert response.status_code == 200

        card_text = html_parser.extract_cards_text(response.data)[0]

        for text in expected_texts:
            assert text in card_text
        for text in unexpected_texts:
            assert text not in card_text


class GetIncidentGenerationFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.finance_invoices.get_finance_invoices_generation_form"
    needed_permission = perm_models.Permissions.GENERATE_INVOICES

    # Fetch Session
    # Fetch User
    # Fetch CashflowBatches
    expected_num_queries = 3

    def test_get_incident_validation_form(self, authenticated_client):
        finance_factories.CashflowBatchFactory()
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))

        assert response.status_code == 200


class GenerateInvoicesTest(PostEndpointHelper):
    endpoint = "backoffice_web.finance_invoices.generate_invoices"
    needed_permission = perm_models.Permissions.GENERATE_INVOICES

    def test_generate_invoices(self, authenticated_client):
        finance_factories.CashflowBatchFactory()
        should_be_called_batch = finance_factories.CashflowBatchFactory()
        with mock.patch("pcapi.tasks.finance_tasks.is_generate_invoices_queue_empty") as queue_empty_mock:
            queue_empty_mock.return_value = True

            with mock.patch(
                "pcapi.core.finance.api.async_generate_invoices"
            ) as generate_invoices_mock:  # so as not to generate all the necessary data
                generate_invoices_mock.return_value = None
                response = self.post_to_endpoint(authenticated_client)
                generate_invoices_mock.assert_called_with(should_be_called_batch)
                assert response.status_code == 303
                assert (
                    html_parser.extract_alert(authenticated_client.get(response.location).data)
                    == "La tâche de génération des justificatifs a été lancée"
                )

    def test_generate_invoices_when_task_already_running(self, authenticated_client):
        finance_factories.CashflowBatchFactory.create_batch(2)
        with mock.patch("pcapi.tasks.finance_tasks.is_generate_invoices_queue_empty") as queue_empty_mock:
            queue_empty_mock.return_value = False

            response = self.post_to_endpoint(authenticated_client)
            assert response.status_code == 303
            assert (
                html_parser.extract_alert(authenticated_client.get(response.location).data)
                == "La tâche de génération des justificatifs est déjà en cours"
            )
