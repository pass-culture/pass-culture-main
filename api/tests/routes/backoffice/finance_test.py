import datetime
import decimal
from secrets import compare_digest
from unittest.mock import patch

import pytest
import sqlalchemy as sa
from dateutil.relativedelta import relativedelta
from flask import url_for

from pcapi.core import testing
from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import factories as educational_factories
from pcapi.core.finance import api
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import utils as finance_utils
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers import exceptions as providers_exceptions
from pcapi.core.providers.clients import cgr_client
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.routes.backoffice.filters import format_booking_status
from pcapi.routes.backoffice.filters import format_date_time
from pcapi.routes.backoffice.finance import forms as finance_forms
from pcapi.utils import date as date_utils

from .helpers import flash
from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class ListIncidentsTest(GetEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.list_incidents"
    needed_permission = perm_models.Permissions.READ_INCIDENTS

    # Fetch Session + user
    # Fetch Finance Incidents
    expected_num_queries = 2

    def test_list_incidents_without_filter(self, authenticated_client):
        partial_booking_incident = finance_factories.IndividualBookingFinanceIncidentFactory(
            newTotalAmount=8.10,
            incident__zendeskId=1,
        )
        total_booking_incident = finance_factories.IndividualBookingFinanceIncidentFactory(
            newTotalAmount=0,
            incident__venue=offerers_factories.CaledonianVenueFactory(),
            incident__zendeskId=2,
        )

        url = url_for(self.endpoint)

        with testing.assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert rows[0]["ID"] == str(total_booking_incident.incident.id)
        assert rows[0]["Statut de l'incident"] == "Créé"
        assert rows[0]["Type d'incident"] == "Trop Perçu"
        assert rows[0]["Nature"] == "Total"
        assert rows[0]["Montant total"] == "10,10 € (1205 CFP)"
        assert rows[0]["Ticket Zendesk"] == "2"
        assert rows[1]["ID"] == str(partial_booking_incident.incident.id)
        assert rows[1]["Statut de l'incident"] == "Créé"
        assert rows[1]["Type d'incident"] == "Trop Perçu"
        assert rows[1]["Nature"] == "Partiel"
        assert rows[1]["Montant total"] == "10,02 €"
        assert rows[1]["Ticket Zendesk"] == "1"

    def test_list_incident_by_incident_id(self, authenticated_client):
        booking = bookings_factories.BookingFactory()
        incident = finance_factories.IndividualBookingFinanceIncidentFactory(booking=booking).incident
        # Ensure that incident.id != other_booking.id or other_offer.id
        max_id = max([incident.id, booking.id, booking.stock.offerId])
        finance_factories.CollectiveBookingFinanceIncidentFactory(
            incident__id=max_id + 1,
            collectiveBooking__id=max_id + 1,
            collectiveBooking__collectiveStock__collectiveOffer__id=max_id + 1,
        )
        finance_factories.IndividualBookingFinanceIncidentFactory(
            incident__id=max_id + 2,
            booking__id=max_id + 2,
            booking__stock__offer__id=max_id + 2,
        )
        incident_id = str(incident.id)

        with testing.assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=incident_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == incident_id
        assert rows[0]["Statut de l'incident"] == "Créé"
        assert rows[0]["Type d'incident"] == "Trop Perçu"
        assert rows[0]["Nature"] == "Total"
        assert rows[0]["Type de résa"] == "Individuelle"
        assert rows[0]["Nb. Réservation(s)"] == str(len(incident.booking_finance_incidents))
        assert rows[0]["Montant total"] == "11,00 €"
        assert rows[0]["Entité juridique"] == incident.venue.managingOfferer.name
        assert rows[0]["Partenaire culturel"] == incident.venue.name
        assert rows[0]["Origine de la demande"] == incident.origin.value

    def test_list_incident_by_booking_id(self, authenticated_client):
        booking = bookings_factories.BookingFactory()
        incident = finance_factories.IndividualBookingFinanceIncidentFactory(booking=booking).incident
        # Ensure that incident.id != other_booking.id or other_offer.id
        max_id = max([incident.id, booking.id, booking.stock.offerId])
        finance_factories.CollectiveBookingFinanceIncidentFactory(
            incident__id=max_id + 1,
            collectiveBooking__id=max_id + 1,
            collectiveBooking__collectiveStock__collectiveOffer__id=max_id + 1,
        )
        booking_id = str(booking.id)

        with testing.assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=booking_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(incident.id)
        assert rows[0]["Statut de l'incident"] == "Créé"
        assert rows[0]["Type d'incident"] == "Trop Perçu"
        assert rows[0]["Nature"] == "Total"
        assert rows[0]["Type de résa"] == "Individuelle"
        assert rows[0]["Nb. Réservation(s)"] == str(len(incident.booking_finance_incidents))
        assert rows[0]["Montant total"] == "11,00 €"
        assert rows[0]["Entité juridique"] == incident.venue.managingOfferer.name
        assert rows[0]["Partenaire culturel"] == incident.venue.name
        assert rows[0]["Origine de la demande"] == incident.origin.value

    def test_list_incident_by_offer_id(self, authenticated_client):
        booking = bookings_factories.BookingFactory()
        incident = finance_factories.IndividualBookingFinanceIncidentFactory(booking=booking).incident
        # Ensure that incident.id != other_booking.id or other_offer.id
        max_id = max([incident.id, booking.id, booking.stock.offerId])

        finance_factories.IndividualBookingFinanceIncidentFactory(
            incident__id=max_id + 1,
            booking__id=max_id + 1,
            booking__stock__offer__id=max_id + 1,
        )
        offer_id = str(booking.stock.offerId)

        with testing.assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=offer_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert incident.id != booking.id
        assert incident.id != booking.stock.offerId
        assert len(rows) == 1
        assert rows[0]["ID"] == str(incident.id)

    def test_list_incident_by_collective_booking_id(self, authenticated_client):
        collective_booking = educational_factories.CollectiveBookingFactory()
        incident = finance_factories.CollectiveBookingFinanceIncidentFactory(
            incident__status=finance_models.IncidentStatus.INVOICED,
            collectiveBooking=collective_booking,
        ).incident
        # Ensure that incident.id != other_booking.id or other_offer.id
        max_id = max([incident.id, collective_booking.id, collective_booking.collectiveStock.collectiveOfferId])
        finance_factories.CollectiveBookingFinanceIncidentFactory(
            incident__id=max_id + 1,
            collectiveBooking__id=max_id + 1,
            collectiveBooking__collectiveStock__collectiveOffer__id=max_id + 1,
        )
        collective_booking_id = str(collective_booking.id)

        with testing.assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=collective_booking_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(incident.id)
        assert rows[0]["Statut de l'incident"] == "Terminé"
        assert rows[0]["Type d'incident"] == "Trop Perçu"
        assert rows[0]["Nature"] == "Total"
        assert rows[0]["Type de résa"] == "Collective"
        assert rows[0]["Nb. Réservation(s)"] == str(len(incident.booking_finance_incidents))
        assert rows[0]["Montant total"] == "100,00 €"
        assert rows[0]["Entité juridique"] == incident.venue.managingOfferer.name
        assert rows[0]["Partenaire culturel"] == incident.venue.name
        assert rows[0]["Origine de la demande"] == incident.origin.value

    def test_list_incident_by_collective_offer_id(self, authenticated_client):
        collective_booking = educational_factories.CollectiveBookingFactory()
        incident = finance_factories.CollectiveBookingFinanceIncidentFactory(
            collectiveBooking=collective_booking
        ).incident
        # Ensure that incident.id != other_booking.id or other_offer.id
        max_id = max([incident.id, collective_booking.id, collective_booking.collectiveStock.collectiveOfferId])
        finance_factories.CollectiveBookingFinanceIncidentFactory(
            incident__id=max_id + 1,
            collectiveBooking__id=max_id + 1,
            collectiveBooking__collectiveStock__collectiveOffer__id=max_id + 1,
        )
        collective_offer_id = str(collective_booking.collectiveStock.collectiveOfferId)

        with testing.assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=collective_offer_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(incident.id)

    def test_list_incident_by_token(self, authenticated_client):
        booking = bookings_factories.BookingFactory()

        incident = finance_factories.IndividualBookingFinanceIncidentFactory(booking=booking).incident
        # Ensure that incident.id != other_booking.id or other_offer.id
        max_id = max([incident.id, booking.id, booking.stock.offerId])

        finance_factories.IndividualBookingFinanceIncidentFactory(
            incident__id=max_id + 1,
            booking__id=max_id + 1,
            booking__stock__offer__id=max_id + 1,
        )
        booking_token = booking.token

        with testing.assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=booking_token))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(incident.id)
        assert rows[0]["Statut de l'incident"] == "Créé"
        assert rows[0]["Type d'incident"] == "Trop Perçu"
        assert rows[0]["Nature"] == "Total"
        assert rows[0]["Type de résa"] == "Individuelle"
        assert rows[0]["Nb. Réservation(s)"] == str(len(incident.booking_finance_incidents))
        assert rows[0]["Montant total"] == "11,00 €"
        assert rows[0]["Entité juridique"] == incident.venue.managingOfferer.name
        assert rows[0]["Partenaire culturel"] == incident.venue.name
        assert rows[0]["Origine de la demande"] == incident.origin.value

    def test_list_incident_by_status(self, authenticated_client):
        finance_factories.IndividualBookingFinanceIncidentFactory(
            incident__status=finance_models.IncidentStatus.CREATED,
        )
        finance_factories.IndividualBookingFinanceIncidentFactory(
            incident__status=finance_models.IncidentStatus.CANCELLED,
        )
        finance_factories.IndividualBookingFinanceIncidentFactory(
            incident__status=finance_models.IncidentStatus.INVOICED,
        )
        incident = finance_factories.IndividualBookingFinanceIncidentFactory(
            incident__status=finance_models.IncidentStatus.VALIDATED,
        ).incident

        with testing.assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, status=[finance_models.IncidentStatus.VALIDATED.name])
            )
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(incident.id)

    def test_list_incident_by_incident_kind_commercial_gesture(self, authenticated_client):
        incident = finance_factories.IndividualBookingFinanceCommercialGestureFactory().incident
        finance_factories.IndividualBookingFinanceIncidentFactory()
        with testing.assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, incident_type="COMMERCIAL_GESTURE"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(incident.id)

    def test_list_incident_by_incident_kind_overpayment(self, authenticated_client):
        incident = finance_factories.IndividualBookingFinanceIncidentFactory().incident
        finance_factories.IndividualBookingFinanceCommercialGestureFactory()
        with testing.assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, incident_type="OVERPAYMENT"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(incident.id)

    def test_list_incident_by_booking_type_true(self, authenticated_client):
        incident = finance_factories.CollectiveBookingFinanceIncidentFactory().incident
        finance_factories.IndividualBookingFinanceIncidentFactory()

        with testing.assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, is_collective="true"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(incident.id)

    def test_list_incident_by_booking_type_false(self, authenticated_client):
        finance_factories.CollectiveBookingFinanceIncidentFactory()
        incident = finance_factories.IndividualBookingFinanceIncidentFactory().incident

        with testing.assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, is_collective="false"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(incident.id)

    def test_list_incident_by_zendesk_id(self, authenticated_client):
        booking = bookings_factories.BookingFactory()
        incident = finance_factories.IndividualBookingFinanceIncidentFactory(
            incident__zendeskId=1,
            booking=booking,
        ).incident
        # Ensure that incident.id != other_booking.id or other_offer.id
        max_id = max([incident.id, booking.id, booking.stock.offerId])

        finance_factories.IndividualBookingFinanceIncidentFactory(
            incident__zendeskId=2,
            incident__id=max_id + 1,
            booking__id=max_id + 1,
            booking__stock__offer__id=max_id + 1,
        )

        with testing.assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="1"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(incident.id)

    def test_list_incident_by_origin(self, authenticated_client):
        incident1 = finance_factories.IndividualBookingFinanceIncidentFactory(
            incident__origin=finance_models.FinanceIncidentRequestOrigin.SUPPORT_JEUNE,
        ).incident
        incident2 = finance_factories.IndividualBookingFinanceIncidentFactory(
            incident__origin=finance_models.FinanceIncidentRequestOrigin.SUPPORT_PRO,
        ).incident
        finance_factories.IndividualBookingFinanceIncidentFactory(
            incident__origin=finance_models.FinanceIncidentRequestOrigin.FRAUDE,
        )

        with testing.assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    origin=[
                        finance_models.FinanceIncidentRequestOrigin.SUPPORT_JEUNE.name,
                        finance_models.FinanceIncidentRequestOrigin.SUPPORT_PRO.name,
                    ],
                )
            )
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert {row["ID"] for row in rows} == {str(incident1.id), str(incident2.id)}

    def test_list_incident_by_offerer(self, authenticated_client):
        incident = finance_factories.IndividualBookingFinanceIncidentFactory().incident
        finance_factories.IndividualBookingFinanceIncidentFactory().incident
        offerer_id = str(incident.venue.managingOffererId)

        with testing.assert_num_queries(self.expected_num_queries + 1):  # +1 to prefill offerer selection in form
            response = authenticated_client.get(url_for(self.endpoint, offerer=offerer_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(incident.id)
        assert rows[0]["Statut de l'incident"] == "Créé"
        assert rows[0]["Type d'incident"] == "Trop Perçu"
        assert rows[0]["Nature"] == "Total"
        assert rows[0]["Type de résa"] == "Individuelle"
        assert rows[0]["Nb. Réservation(s)"] == str(len(incident.booking_finance_incidents))
        assert rows[0]["Montant total"] == "11,00 €"
        assert rows[0]["Entité juridique"] == incident.venue.managingOfferer.name
        assert rows[0]["Partenaire culturel"] == incident.venue.name
        assert rows[0]["Origine de la demande"] == incident.origin.value

    def test_list_incident_by_venue(self, authenticated_client):
        incident = finance_factories.IndividualBookingFinanceIncidentFactory().incident
        finance_factories.IndividualBookingFinanceIncidentFactory().incident
        venue_id = str(incident.venueId)

        with testing.assert_num_queries(self.expected_num_queries + 1):  # +1 to prefill venue selection in form
            response = authenticated_client.get(url_for(self.endpoint, venue=venue_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(incident.id)

    def test_list_incident_by_dates(self, authenticated_client):
        incident = finance_factories.IndividualBookingFinanceIncidentFactory().incident
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.FINANCE_INCIDENT_CREATED,
            financeIncident=incident,
            actionDate=(datetime.date.today() - datetime.timedelta(days=1)).isoformat(),
        )
        finance_factories.IndividualBookingFinanceIncidentFactory()

        with testing.assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    from_date=(datetime.date.today() - datetime.timedelta(days=3)).isoformat(),
                    to_date=(datetime.date.today() - datetime.timedelta(days=1)).isoformat(),
                )
            )
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(incident.id)


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

    expected_num_queries = 1
    expected_num_queries += 1  # get incident info

    def test_get_incident_validation_form(self, authenticated_client):
        booking_incident = finance_factories.IndividualBookingFinanceIncidentFactory()
        url = url_for(self.endpoint, finance_incident_id=booking_incident.incident.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        text_content = html_parser.content_as_text(response.data)
        assert (
            "Vous allez valider un incident de 11,00 € sur le compte bancaire du partenaire culturel." in text_content
        )

    def test_no_script_injection_in_venue_name(self, authenticated_client):
        bank_account = finance_factories.BankAccountFactory()
        venue = offerers_factories.VenueFactory(name="<script>alert('coucou')</script>", bank_account=bank_account)
        booking_incident = finance_factories.IndividualBookingFinanceIncidentFactory(incident__venue=venue)
        url = url_for(self.endpoint, finance_incident_id=booking_incident.incident.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        text_content = html_parser.content_as_text(response.data)
        assert f"Vous allez valider un incident de 11,00 € sur le compte bancaire {bank_account.label}." in text_content


class CancelIncidentTest(PostEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.cancel_finance_incident"
    endpoint_kwargs = {"finance_incident_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_INCIDENTS

    def test_cancel_incident(self, legit_user, authenticated_client):
        incident = finance_factories.FinanceIncidentFactory()
        self.form_data = {"comment": "L'incident n'est pas conforme"}

        response = self.post_to_endpoint(
            authenticated_client, finance_incident_id=incident.id, form=self.form_data, follow_redirects=True
        )

        assert response.status_code == 200

        assert (
            db.session.query(finance_models.FinanceIncident)
            .filter(finance_models.FinanceIncident.status == finance_models.IncidentStatus.CREATED)
            .count()
            == 0
        )

        badges = html_parser.extract(response.data, tag="span", class_="badge")
        assert "Annulé" in badges

        action_history = db.session.query(history_models.ActionHistory).one()
        assert action_history.actionType == history_models.ActionType.FINANCE_INCIDENT_CANCELLED
        assert action_history.authorUser == legit_user
        assert action_history.comment == self.form_data["comment"]

    @pytest.mark.parametrize(
        "status, wording",
        [
            (finance_models.IncidentStatus.CANCELLED, "annulé"),
            (finance_models.IncidentStatus.VALIDATED, "validé"),
            (finance_models.IncidentStatus.INVOICED, "remboursé"),
        ],
    )
    def test_cancel_wrong_status_incident(self, authenticated_client, status, wording):
        incident = finance_factories.FinanceIncidentFactory(status=status)
        self.form_data = {"comment": "L'incident n'est pas conforme"}

        response = self.post_to_endpoint(
            authenticated_client, finance_incident_id=incident.id, form=self.form_data, follow_redirects=True
        )

        assert response.status_code == 200

        assert f"Impossible d'annuler un incident déjà {wording}" in html_parser.extract_alert(response.data)
        assert db.session.query(history_models.ActionHistory).count() == 0


class ValidateFinanceOverpaymentIncidentTest(PostEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.validate_finance_overpayment_incident"
    endpoint_kwargs = {"finance_incident_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_INCIDENTS

    @pytest.mark.parametrize("force_debit_note", [True, False])
    def test_validate_incident(self, authenticated_client, force_debit_note):
        venue = offerers_factories.VenueBankAccountLinkFactory().venue
        booking_incident = finance_factories.IndividualBookingFinanceIncidentFactory(
            booking__amount=10.10,
            booking__stock__offer__venue=venue,
            incident__venue=venue,
            newTotalAmount=0,
        )
        finance_factories.PricingFactory(
            booking=booking_incident.booking,
            status=finance_models.PricingStatus.INVOICED,
            amount=-1000,
        )
        used_finance_event = db.session.query(finance_models.FinanceEvent).one()

        assert booking_incident.incident.venue.current_bank_account_link

        response = self.post_to_endpoint(
            authenticated_client,
            finance_incident_id=booking_incident.incident.id,
            form={
                "compensation_mode": (
                    finance_forms.IncidentCompensationModes.FORCE_DEBIT_NOTE.name
                    if force_debit_note
                    else finance_forms.IncidentCompensationModes.COMPENSATE_ON_BOOKINGS.name
                )
            },
            follow_redirects=True,
        )

        assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert "L'incident a été validé." in content

        updated_incident = (
            db.session.query(finance_models.FinanceIncident).filter_by(id=booking_incident.incidentId).one()
        )
        assert updated_incident.status == finance_models.IncidentStatus.VALIDATED
        assert updated_incident.forceDebitNote == force_debit_note

        beneficiary_action = (
            db.session.query(history_models.ActionHistory)
            .filter(history_models.ActionHistory.user == booking_incident.beneficiary)
            .first()
        )
        validation_action = (
            db.session.query(history_models.ActionHistory)
            .filter(history_models.ActionHistory.financeIncident == updated_incident)
            .first()
        )

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

        last_finance_event = (
            db.session.query(finance_models.FinanceEvent)
            .filter(finance_models.FinanceEvent.id != used_finance_event.id)
            .one()
        )
        assert last_finance_event.motive == finance_models.FinanceEventMotive.INCIDENT_REVERSAL_OF_ORIGINAL_EVENT

        assert len(mails_testing.outbox) == 2
        assert mails_testing.outbox[0]["To"] == venue.bookingEmail
        if force_debit_note:
            assert (
                mails_testing.outbox[0]["template"]
                == TransactionalEmail.RETRIEVE_DEBIT_NOTE_ON_INDIVIDUAL_BOOKINGS.value.__dict__
            )
        else:
            assert (
                mails_testing.outbox[0]["template"]
                == TransactionalEmail.RETRIEVE_INCIDENT_AMOUNT_ON_INDIVIDUAL_BOOKINGS.value.__dict__
            )
        assert mails_testing.outbox[0]["params"] == {
            "OFFER_NAME": booking_incident.booking.stock.offer.name,
            "VENUE_NAME": venue.publicName,
            "TOKEN_LIST": booking_incident.booking.token,
        }

        assert mails_testing.outbox[-1]["To"] == booking_incident.booking.user.email
        assert (
            mails_testing.outbox[-1]["template"]
            == TransactionalEmail.BOOKING_CANCELLATION_BY_PRO_TO_BENEFICIARY.value.__dict__
        )
        assert mails_testing.outbox[-1]["params"]["OFFER_NAME"] == booking_incident.booking.stock.offer.name
        assert mails_testing.outbox[-1]["params"]["VENUE_NAME"] == venue.publicName

    @pytest.mark.parametrize("force_debit_note", [True, False])
    def test_incident_validation_with_several_bookings(self, authenticated_client, force_debit_note):
        deposit = users_factories.DepositGrantFactory(
            amount=300, expirationDate=date_utils.get_naive_utc_now() + relativedelta(years=2)
        )
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

        total_booking_incident = finance_factories.IndividualBookingFinanceIncidentFactory(
            booking=booking_reimbursed,
            incident=incident,
            newTotalAmount=finance_utils.to_cents(booking_reimbursed.pricings[0].amount),
        )  # total incident

        partial_booking_incident = finance_factories.IndividualBookingFinanceIncidentFactory(
            booking=booking_reimbursed_2, incident=incident, newTotalAmount=3000
        )  # partiel incident : instead of 40, 10 go back to the deposit

        response = self.post_to_endpoint(
            authenticated_client,
            finance_incident_id=incident.id,
            form={
                "compensation_mode": (
                    finance_forms.IncidentCompensationModes.FORCE_DEBIT_NOTE.name
                    if force_debit_note
                    else finance_forms.IncidentCompensationModes.COMPENSATE_ON_BOOKINGS.name
                )
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert "L'incident a été validé" in html_parser.content_as_text(response.data)
        assert incident.status == finance_models.IncidentStatus.VALIDATED
        assert incident.forceDebitNote == force_debit_note

        validation_action = (
            db.session.query(history_models.ActionHistory)
            .filter(history_models.ActionHistory.financeIncident == incident)
            .first()
        )

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

        # total finance incident
        total_incident_events = (
            db.session.query(finance_models.FinanceEvent)
            .filter(finance_models.FinanceEvent.bookingFinanceIncidentId == total_booking_incident.id)
            .all()
        )
        assert len(total_incident_events) == 1
        assert total_incident_events[0].motive == finance_models.FinanceEventMotive.INCIDENT_REVERSAL_OF_ORIGINAL_EVENT

        # partial finaance incident
        partial_incident_events = (
            db.session.query(finance_models.FinanceEvent)
            .filter(finance_models.FinanceEvent.bookingFinanceIncidentId == partial_booking_incident.id)
            .all()
        )
        assert len(partial_incident_events) == 2
        assert (
            partial_incident_events[0].motive == finance_models.FinanceEventMotive.INCIDENT_REVERSAL_OF_ORIGINAL_EVENT
        )
        assert partial_incident_events[1].motive == finance_models.FinanceEventMotive.INCIDENT_NEW_PRICE

    @pytest.mark.parametrize(
        "initial_status",
        [
            finance_models.IncidentStatus.CANCELLED,
            finance_models.IncidentStatus.VALIDATED,
            finance_models.IncidentStatus.INVOICED,
        ],
    )
    def test_not_validate_incident(self, authenticated_client, initial_status):
        finance_incident = finance_factories.FinanceIncidentFactory(status=initial_status)

        response = self.post_to_endpoint(
            authenticated_client,
            finance_incident_id=finance_incident.id,
            form={"compensation_mode": finance_forms.IncidentCompensationModes.COMPENSATE_ON_BOOKINGS.name},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert (
            html_parser.extract_alert(response.data) == "L'incident ne peut être validé que s'il est au statut 'créé'."
        )
        finance_incident = db.session.query(finance_models.FinanceIncident).filter_by(id=finance_incident.id).one()
        assert finance_incident.status == initial_status
        assert db.session.query(finance_models.FinanceEvent).count() == 0
        assert len(mails_testing.outbox) == 0

    @pytest.mark.parametrize(
        "exception_type,expected_error_msg",
        [
            (cgr_client.CGRAPIException, "Une erreur s'est produite : Test"),
            (providers_exceptions.ProviderException, "Une erreur s'est produite : ProviderException"),
        ],
    )
    def test_validate_incident_external_provider_api_failed(
        self, authenticated_client, exception_type, expected_error_msg
    ):
        finance_incident = finance_factories.FinanceIncidentFactory(status=finance_models.IncidentStatus.CREATED)

        with patch(
            "pcapi.core.finance.api.validate_finance_overpayment_incident",
            side_effect=exception_type("Test"),
        ):
            response = self.post_to_endpoint(
                authenticated_client,
                finance_incident_id=finance_incident.id,
                form={"compensation_mode": finance_forms.IncidentCompensationModes.COMPENSATE_ON_BOOKINGS.name},
                follow_redirects=True,
            )

        assert response.status_code == 200
        assert html_parser.extract_alert(response.data) == expected_error_msg

        db.session.refresh(finance_incident)
        assert finance_incident.status == finance_models.IncidentStatus.CREATED
        assert db.session.query(finance_models.FinanceEvent).count() == 0
        assert len(mails_testing.outbox) == 0


class GetBatchFinanceIncidentValidationFormTest(PostEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.get_batch_finance_incidents_validation_form"
    needed_permission = perm_models.Permissions.MANAGE_INCIDENTS

    @pytest.mark.parametrize(
        "kind,expected_result",
        [
            (finance_models.IncidentType.OVERPAYMENT, "trop perçus"),
            (finance_models.IncidentType.COMMERCIAL_GESTURE, "gestes commerciaux"),
        ],
    )
    def test_validate_finance_incidents_form(self, authenticated_client, kind, expected_result):
        finance_factories.CollectiveBookingFinanceIncidentFactory(
            incident__id=39,
            incident__status=finance_models.IncidentStatus.CREATED,
            incident__kind=kind,
        )
        finance_factories.CollectiveBookingFinanceIncidentFactory(
            incident__id=40,
            incident__status=finance_models.IncidentStatus.CREATED,
            incident__kind=kind,
        )

        response = self.post_to_endpoint(
            authenticated_client,
            form={"object_ids": "39,40"},
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        response_text = html_parser.content_as_text(response.data)
        assert f"Voulez-vous valider les {expected_result} sélectionnés ?" in response_text
        assert "Vous allez valider 2 incident(s). Voulez vous continuer ?" in response_text
        if kind == finance_models.IncidentType.OVERPAYMENT:
            assert "Générer une note de débit à la prochaine échéance" in response_text
            assert "Récupérer l'argent sur les prochaines réservations Mode de compensation" in response_text

    def test_validate_finance_incidents_with_other_status_then_created(self, authenticated_client):
        incident1 = finance_factories.IndividualBookingFinanceIncidentFactory(
            incident__status=finance_models.IncidentStatus.CREATED,
        ).incident
        incident2 = finance_factories.CollectiveBookingFinanceIncidentFactory(
            incident__status=finance_models.IncidentStatus.VALIDATED,
        ).incident
        incident3 = finance_factories.IndividualBookingFinanceIncidentFactory(
            incident__status=finance_models.IncidentStatus.CANCELLED,
        ).incident
        incident4 = finance_factories.IndividualBookingFinanceIncidentFactory(
            incident__status=finance_models.IncidentStatus.INVOICED,
        ).incident

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "object_ids": f"{incident1.id},{incident2.id},{incident3.id},{incident4.id}",
            },
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        assert (
            """Seuls les incidents au statut "créé" peuvent faire l'objet d'une validation"""
            in html_parser.content_as_text(response.data)
        )

    def test_validate_finance_incidents_with_different_type(self, authenticated_client):
        incident1 = finance_factories.IndividualBookingFinanceIncidentFactory(
            incident__status=finance_models.IncidentStatus.CREATED,
        ).incident
        incident2 = finance_factories.IndividualBookingFinanceCommercialGestureFactory(
            incident__status=finance_models.IncidentStatus.CREATED
        ).incident

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "object_ids": f"{incident1.id},{incident2.id}",
            },
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        assert (
            "Impossible de valider des trop perçus et des gestes commerciaux dans la même action"
            in html_parser.content_as_text(response.data)
        )


class GetBatchFinanceIncidentCancellationFormTest(PostEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.get_batch_finance_incidents_cancellation_form"
    needed_permission = perm_models.Permissions.MANAGE_INCIDENTS

    @pytest.mark.parametrize(
        "kind,expected_result",
        [
            (finance_models.IncidentType.OVERPAYMENT, "trop perçus"),
            (finance_models.IncidentType.COMMERCIAL_GESTURE, "gestes commerciaux"),
        ],
    )
    def test_cancel_finance_incidents_form(self, authenticated_client, kind, expected_result):
        incident1 = finance_factories.CollectiveBookingFinanceIncidentFactory(
            incident__status=finance_models.IncidentStatus.CREATED,
            incident__kind=kind,
        ).incident
        incident2 = finance_factories.CollectiveBookingFinanceIncidentFactory(
            incident__status=finance_models.IncidentStatus.CREATED,
            incident__kind=kind,
        ).incident

        response = self.post_to_endpoint(
            authenticated_client,
            form={"object_ids": f"{incident1.id},{incident2.id}"},
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        response_text = html_parser.content_as_text(response.data)
        assert f"Voulez-vous annuler les {expected_result} sélectionnés ?" in response_text
        assert "Vous allez annuler 2 incident(s). Voulez vous continuer ?" in response_text

    def test_cancel_finance_incidents_with_other_status_then_created(self, authenticated_client):
        incident1 = finance_factories.IndividualBookingFinanceIncidentFactory(
            incident__status=finance_models.IncidentStatus.CREATED,
        ).incident
        incident2 = finance_factories.CollectiveBookingFinanceIncidentFactory(
            incident__status=finance_models.IncidentStatus.VALIDATED,
        ).incident
        incident3 = finance_factories.IndividualBookingFinanceIncidentFactory(
            incident__status=finance_models.IncidentStatus.CANCELLED,
        ).incident
        incident4 = finance_factories.IndividualBookingFinanceIncidentFactory(
            incident__status=finance_models.IncidentStatus.INVOICED,
        ).incident

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "object_ids": f"{incident1.id},{incident2.id},{incident3.id},{incident4.id}",
            },
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        assert (
            """Seuls les incidents au statut "créé" peuvent faire l'objet d'une annulation"""
            in html_parser.content_as_text(response.data)
        )

    def test_cancel_finance_incidents_with_different_type(self, authenticated_client):
        incident1 = finance_factories.IndividualBookingFinanceIncidentFactory(
            incident__status=finance_models.IncidentStatus.CREATED,
        ).incident
        incident2 = finance_factories.IndividualBookingFinanceCommercialGestureFactory(
            incident__status=finance_models.IncidentStatus.CREATED
        ).incident

        response = self.post_to_endpoint(
            authenticated_client,
            form={"object_ids": f"{incident1.id},{incident2.id}"},
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        assert (
            "Impossible de rejeter des trop perçus et des gestes commerciaux dans la même action"
            in html_parser.content_as_text(response.data)
        )


class ValidateFinanceCommercialGestureTest(PostEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.validate_finance_commercial_gesture"
    endpoint_kwargs = {"finance_incident_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_COMMERCIAL_GESTURE

    def test_validate_commercial_gesture(self, authenticated_client):
        venue = offerers_factories.VenueBankAccountLinkFactory().venue

        used_booking_finance_event = finance_factories.UsedBookingFinanceEventFactory(
            booking__stock__price=decimal.Decimal("10.10")
        )
        booking = used_booking_finance_event.booking

        bookings_api._cancel_booking(booking, bookings_models.BookingCancellationReasons.OFFERER)

        booking_incident = finance_factories.IndividualBookingFinanceCommercialGestureFactory(
            incident__venue=venue,
            booking=booking,
            newTotalAmount=5_00,
        )
        used_finance_event = db.session.query(finance_models.FinanceEvent).one()

        assert booking_incident.incident.venue.current_bank_account_link

        response = self.post_to_endpoint(
            authenticated_client,
            finance_incident_id=booking_incident.incident.id,
            form={
                "compensation_mode": finance_forms.IncidentCompensationModes.COMPENSATE_ON_BOOKINGS.name,
            },
            follow_redirects=True,
        )

        assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert "Le geste commercial a été validé." in content

        updated_incident = (
            db.session.query(finance_models.FinanceIncident).filter_by(id=booking_incident.incidentId).one()
        )
        assert updated_incident.status == finance_models.IncidentStatus.VALIDATED
        assert updated_incident.forceDebitNote is False

        beneficiary_action = (
            db.session.query(history_models.ActionHistory)
            .filter(history_models.ActionHistory.user == booking_incident.beneficiary)
            .first()
        )
        validation_action = (
            db.session.query(history_models.ActionHistory)
            .filter(history_models.ActionHistory.financeIncident == updated_incident)
            .first()
        )

        assert validation_action
        assert validation_action.actionType == history_models.ActionType.FINANCE_INCIDENT_VALIDATED
        assert validation_action.comment == "Récupération sur les prochaines réservations."

        assert (
            beneficiary_action
            and beneficiary_action.actionType == history_models.ActionType.FINANCE_INCIDENT_USER_RECREDIT
        )

        last_finance_event = (
            db.session.query(finance_models.FinanceEvent)
            .filter(finance_models.FinanceEvent.id != used_finance_event.id)
            .one()
        )
        assert last_finance_event.motive == finance_models.FinanceEventMotive.INCIDENT_COMMERCIAL_GESTURE

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == venue.bookingEmail
        assert mails_testing.outbox[0]["template"] == TransactionalEmail.COMMERCIAL_GESTURE_REIMBURSEMENT.value.__dict__
        assert mails_testing.outbox[0]["params"] == {
            "OFFER_NAME": booking_incident.booking.stock.offer.name,
            "VENUE_NAME": venue.publicName,
            "MONTANT_REMBOURSEMENT": decimal.Decimal("5.10"),
            "FORMATTED_MONTANT_REMBOURSEMENT": "5,10 €",
            "TOKEN_LIST": booking_incident.booking.token,
        }

    def test_commercial_gesture_validation_with_several_bookings(self, authenticated_client):
        deposit = users_factories.DepositGrantFactory(
            amount=300, expirationDate=date_utils.get_naive_utc_now() + relativedelta(years=2)
        )
        incident = finance_factories.FinanceCommercialGestureFactory()
        # make the participant poor because commercial gesture is not meant to be taken from the user's balance
        bookings_factories.UsedBookingFactory(stock__price=decimal.Decimal("299.9"), user=deposit.user)

        assert incident.status == finance_models.IncidentStatus.CREATED

        cancelled_booking1 = bookings_factories.CancelledBookingFactory(
            deposit=deposit,
            amount=30,
            user=deposit.user,
            pricings=[
                finance_factories.PricingFactory(status=finance_models.PricingStatus.CANCELLED, amount=-3000),
            ],
        )
        cancelled_booking2 = bookings_factories.CancelledBookingFactory(
            deposit=deposit,
            amount=40,
            user=deposit.user,
            pricings=[finance_factories.PricingFactory(status=finance_models.PricingStatus.CANCELLED, amount=-4000)],
        )

        total_booking_commercial_gesture = finance_factories.IndividualBookingFinanceCommercialGestureFactory(
            booking=cancelled_booking1,
            incident=incident,
            newTotalAmount=finance_utils.to_cents(cancelled_booking1.pricings[0].amount),
        )  # total commercial gesture

        partial_booking_commercial_gesture = finance_factories.IndividualBookingFinanceCommercialGestureFactory(
            booking=cancelled_booking2, incident=incident, newTotalAmount=3000
        )  # partial commercial gesture : instead of 40, 10 go back to the deposit

        response = self.post_to_endpoint(
            authenticated_client,
            finance_incident_id=incident.id,
            form={
                "compensation_mode": finance_forms.IncidentCompensationModes.COMPENSATE_ON_BOOKINGS.name,
            },
            follow_redirects=True,
        )

        assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert "Le geste commercial a été validé." in content

        assert incident.status == finance_models.IncidentStatus.VALIDATED
        assert incident.forceDebitNote is False

        validation_action = (
            db.session.query(history_models.ActionHistory)
            .filter(history_models.ActionHistory.financeIncident == incident)
            .first()
        )

        assert validation_action
        assert validation_action.actionType == history_models.ActionType.FINANCE_INCIDENT_VALIDATED
        assert validation_action.comment == "Récupération sur les prochaines réservations."
        assert db.session.query(sa.func.get_deposit_balance(deposit.id, False)).first()[0] == decimal.Decimal("0.10")
        assert db.session.query(sa.func.get_deposit_balance(deposit.id, True)).first()[0] == decimal.Decimal("0.10")

        assert cancelled_booking1.status == bookings_models.BookingStatus.CANCELLED
        assert cancelled_booking2.status == bookings_models.BookingStatus.CANCELLED

        # total finance incident
        total_incident_events = (
            db.session.query(finance_models.FinanceEvent)
            .filter(finance_models.FinanceEvent.bookingFinanceIncidentId == total_booking_commercial_gesture.id)
            .all()
        )
        assert len(total_incident_events) == 1
        assert total_incident_events[0].motive == finance_models.FinanceEventMotive.INCIDENT_COMMERCIAL_GESTURE

        # partial finaance incident
        partial_incident_events = (
            db.session.query(finance_models.FinanceEvent)
            .filter(finance_models.FinanceEvent.bookingFinanceIncidentId == partial_booking_commercial_gesture.id)
            .all()
        )
        assert len(partial_incident_events) == 1
        assert partial_incident_events[0].motive == finance_models.FinanceEventMotive.INCIDENT_COMMERCIAL_GESTURE

    def test_validate_commercial_gesture_incident(self, client, codir_admin):
        venue = offerers_factories.VenueBankAccountLinkFactory().venue
        offer_1 = offers_factories.OfferFactory(venue=venue)
        stock_1 = offers_factories.StockFactory(offer=offer_1)
        offer_2 = offers_factories.OfferFactory(venue=venue)
        stock_2 = offers_factories.StockFactory(offer=offer_2)
        deposit = users_factories.DepositGrantFactory()
        incident = finance_factories.FinanceCommercialGestureFactory(venue=venue)

        assert incident.status == finance_models.IncidentStatus.CREATED

        cancelled_booking1 = bookings_factories.CancelledBookingFactory(
            deposit=deposit,
            amount=decimal.Decimal("30.0"),
            user=deposit.user,
            stock=stock_1,
            pricings=[finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED, amount=-3000)],
        )
        cancelled_booking2 = bookings_factories.CancelledBookingFactory(
            deposit=deposit,
            amount=decimal.Decimal("40.0"),
            user=deposit.user,
            stock=stock_2,
            pricings=[finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED, amount=-4000)],
        )

        commercial_gesture_incident1 = finance_factories.IndividualBookingFinanceCommercialGestureFactory(
            booking=cancelled_booking1,
            incident=incident,
            newTotalAmount=20_00,
        )

        commercial_gesture_incident2 = finance_factories.IndividualBookingFinanceCommercialGestureFactory(
            booking=cancelled_booking2,
            incident=incident,
            newTotalAmount=10_00,
        )

        response = self.post_to_endpoint(
            client.with_bo_session_auth(codir_admin),
            finance_incident_id=incident.id,
            form={"compensation_mode": finance_forms.IncidentCompensationModes.COMPENSATE_ON_BOOKINGS.name},
            follow_redirects=True,
        )

        assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert "Le geste commercial a été validé" in content

        assert incident.status == finance_models.IncidentStatus.VALIDATED

        commercial_gesture1_events = (
            db.session.query(finance_models.FinanceEvent)
            .filter(finance_models.FinanceEvent.bookingFinanceIncidentId == commercial_gesture_incident1.id)
            .all()
        )
        assert len(commercial_gesture1_events) == 1

        commercial_gesture2_events = (
            db.session.query(finance_models.FinanceEvent)
            .filter(finance_models.FinanceEvent.bookingFinanceIncidentId == commercial_gesture_incident2.id)
            .all()
        )
        assert len(commercial_gesture2_events) == 1

        assert len(mails_testing.outbox) == 2
        assert mails_testing.outbox[0]["To"] == venue.bookingEmail
        assert mails_testing.outbox[0]["template"] == TransactionalEmail.COMMERCIAL_GESTURE_REIMBURSEMENT.value.__dict__
        params_1 = mails_testing.outbox[0]["params"]
        assert params_1["OFFER_NAME"] == offer_1.name
        assert params_1["VENUE_NAME"] == venue.publicName
        assert params_1["MONTANT_REMBOURSEMENT"] == decimal.Decimal("10")
        assert params_1["FORMATTED_MONTANT_REMBOURSEMENT"] == "10 €"
        assert compare_digest(params_1["TOKEN_LIST"], cancelled_booking1.token)
        params_2 = mails_testing.outbox[1]["params"]
        assert params_2["OFFER_NAME"] == offer_2.name
        assert params_2["VENUE_NAME"] == venue.publicName
        assert params_2["MONTANT_REMBOURSEMENT"] == decimal.Decimal("30")
        assert params_2["FORMATTED_MONTANT_REMBOURSEMENT"] == "30 €"
        assert compare_digest(params_2["TOKEN_LIST"], cancelled_booking2.token)

    @pytest.mark.parametrize(
        "initial_status",
        [
            finance_models.IncidentStatus.CANCELLED,
            finance_models.IncidentStatus.VALIDATED,
            finance_models.IncidentStatus.INVOICED,
        ],
    )
    def test_validate_invalid_commercial_gesture_status(self, authenticated_client, initial_status):
        finance_incident = finance_factories.FinanceCommercialGestureFactory(status=initial_status)

        response = self.post_to_endpoint(
            authenticated_client,
            finance_incident_id=finance_incident.id,
            form={"compensation_mode": finance_forms.IncidentCompensationModes.COMPENSATE_ON_BOOKINGS.name},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert (
            html_parser.extract_alert(response.data)
            == "Le geste commercial ne peut être validé que s'il est au statut 'créé'."
        )
        finance_incident = db.session.query(finance_models.FinanceIncident).filter_by(id=finance_incident.id).one()
        assert finance_incident.status == initial_status
        assert db.session.query(finance_models.FinanceEvent).count() == 0
        assert len(mails_testing.outbox) == 0


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
        validation_date = date_utils.get_naive_utc_now()
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

        validation_date = date_utils.get_naive_utc_now()
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

        validation_date = date_utils.get_naive_utc_now()
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
        booking_incident = finance_factories.IndividualBookingFinanceCommercialGestureFactory(
            booking__pricings=[
                finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED, amount=-1000)
            ],
            newTotalAmount=800,
        )
        validation_date = date_utils.get_naive_utc_now()

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
    expected_num_queries += 1  # Fetch Session + User
    expected_num_queries += 1  # Fetch Incident infos

    def test_get_overpayment_incident(self, authenticated_client):
        overpayment_incident = finance_factories.FinanceIncidentFactory(kind=finance_models.IncidentType.OVERPAYMENT)
        bank_account = finance_factories.BankAccountFactory(offerer=overpayment_incident.venue.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(venue=overpayment_incident.venue, bankAccount=bank_account)
        url = url_for(self.endpoint, finance_incident_id=overpayment_incident.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 303

        assert response.location.endswith(
            url_for(
                "backoffice_web.finance_incidents.get_incident_overpayment", finance_incident_id=overpayment_incident.id
            )
        )

    def test_get_commercial_gesture(self, authenticated_client):
        commercial_gesture = finance_factories.FinanceIncidentFactory(
            kind=finance_models.IncidentType.COMMERCIAL_GESTURE
        )
        bank_account = finance_factories.BankAccountFactory(offerer=commercial_gesture.venue.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(venue=commercial_gesture.venue, bankAccount=bank_account)
        url = url_for(self.endpoint, finance_incident_id=commercial_gesture.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 303

        assert response.location.endswith(
            url_for(
                "backoffice_web.finance_incidents.get_commercial_gesture", finance_incident_id=commercial_gesture.id
            )
        )

    def test_get_unhandled_incident_kind(self, authenticated_client):
        incident = finance_factories.FinanceIncidentFactory(kind=finance_models.IncidentType.OFFER_PRICE_REGULATION)
        bank_account = finance_factories.BankAccountFactory(offerer=incident.venue.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(venue=incident.venue, bankAccount=bank_account)
        url = url_for(self.endpoint, finance_incident_id=incident.id)

        with assert_num_queries(self.expected_num_queries + 1):  # rollback
            response = authenticated_client.get(url)
            assert response.status_code == 404


class GetOverpaymentIncidentTest(GetEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.get_incident_overpayment"
    endpoint_kwargs = {"finance_incident_id": 1}
    needed_permission = perm_models.Permissions.READ_INCIDENTS
    expected_num_queries = 0
    expected_num_queries += 1  # Fetch Session + User
    expected_num_queries += 1  # Fetch Incidents infos

    @pytest.mark.parametrize(
        "venue_factory,expected_xpf_text",
        [(offerers_factories.VenueFactory, ""), (offerers_factories.CaledonianVenueFactory, "(1205 CFP)")],
    )
    @pytest.mark.parametrize("zendesk_id", [None, "1"])
    def test_get_incident(self, authenticated_client, venue_factory, expected_xpf_text, zendesk_id):
        finance_incident = finance_factories.FinanceIncidentFactory(venue=venue_factory(), zendeskId=zendesk_id)
        finance_factories.IndividualBookingFinanceIncidentFactory(newTotalAmount=0, incident=finance_incident)
        bank_account = finance_factories.BankAccountFactory(offerer=finance_incident.venue.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(venue=finance_incident.venue, bankAccount=bank_account)
        url = url_for(self.endpoint, finance_incident_id=finance_incident.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        header = html_parser.get_tag(response.data, class_="incident-header")
        badges = html_parser.extract_badges(header)
        assert badges == ["Créé", "Total"]

        content = html_parser.content_as_text(response.data)
        assert f"ID : {finance_incident.id}" in content
        assert f"Partenaire culturel porteur de l'offre : {finance_incident.venue.name}" in content
        assert f"Compte bancaire : {bank_account.label}" in content
        if zendesk_id:
            assert f"Ticket Zendesk : {zendesk_id}" in content
        else:
            assert "Ticket Zendesk" not in content
        assert f"Montant trop perçu par l'acteur culturel à récupérer : 10,10 € {expected_xpf_text}" in content
        assert "Batch :" not in content
        assert "Justificatif de remboursement :" not in content

    @pytest.mark.parametrize("zendesk_id", [None, "1"])
    def test_get_collective_booking_incident(self, authenticated_client, zendesk_id):
        finance_incident = finance_factories.FinanceIncidentFactory(
            booking_finance_incidents=[finance_factories.CollectiveBookingFinanceIncidentFactory()],
            zendeskId=zendesk_id,
        )
        finance_factories.CollectiveBookingFinanceIncidentFactory(incident=finance_incident)
        url = url_for(self.endpoint, finance_incident_id=finance_incident.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert f"ID : {finance_incident.id}" in content
        assert f"Partenaire culturel porteur de l'offre : {finance_incident.venue.name}" in content
        if zendesk_id:
            assert f"Ticket Zendesk : {zendesk_id}" in content
        else:
            assert "Ticket Zendesk" not in content
        assert f"Incident créé par : {finance_incident.details['author']}" in content
        assert "Batch :" not in content
        assert "Justificatif de remboursement :" not in content

    def test_get_incident_batch_info(self, authenticated_client):
        bank_account = finance_factories.BankAccountFactory()
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerers_factories.UserOffererFactory().offerer, bank_account=bank_account
        )
        invoice = finance_factories.InvoiceFactory()
        cashflow = finance_factories.CashflowFactory(
            status=finance_models.CashflowStatus.ACCEPTED,
            bankAccount=bank_account,
            batch__label="VIR1",
            invoices=[invoice],
        )
        pricing = finance_factories.PricingFactory(
            status=finance_models.PricingStatus.INVOICED,
            cashflows=[cashflow],
        )
        finance_incident = finance_factories.FinanceIncidentFactory()
        booking_finance_incident = finance_factories.IndividualBookingFinanceIncidentFactory(
            incident=finance_incident,
        )
        finance_factories.FinanceEventFactory(
            venue=venue,
            bookingFinanceIncident=booking_finance_incident,
            booking=None,
            valueDate=date_utils.get_naive_utc_now(),
            status=finance_models.FinanceEventStatus.PRICED,
            pricings=[pricing],
            pricingPoint=venue,
            pricingOrderingDate=date_utils.get_naive_utc_now(),
        )

        url = url_for(self.endpoint, finance_incident_id=finance_incident.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)

        assert f"ID : {finance_incident.id}" in content
        assert f"Partenaire culturel porteur de l'offre : {finance_incident.venue.name}" in content
        assert f"Incident créé par : {finance_incident.details['author']}" in content
        assert "Batch : VIR1" in content
        assert "Justificatif de remboursement : PDF" in content
        assert (
            invoice.url
            in html_parser.get_tag(html_content=response.data, class_="link-primary", tag="a", download=True).decode()
        )


class GetCommercialGestureTest(GetEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.get_commercial_gesture"
    endpoint_kwargs = {"finance_incident_id": 1}
    needed_permission = perm_models.Permissions.READ_INCIDENTS
    expected_num_queries = 0
    expected_num_queries += 1  # Fetch Session User
    expected_num_queries += 1  # Fetch Incidents infos

    @pytest.mark.parametrize(
        "venue_factory,expected_xpf_text",
        [
            (offerers_factories.VenueFactory, ""),
            (offerers_factories.CaledonianVenueFactory, "(1205 CFP)"),
        ],
    )
    @pytest.mark.parametrize("zendesk_id", [None, "1"])
    def test_get_incident(self, authenticated_client, venue_factory, expected_xpf_text, zendesk_id):
        finance_incident = finance_factories.FinanceIncidentFactory(
            kind=finance_models.IncidentType.COMMERCIAL_GESTURE, venue=venue_factory(), zendeskId=zendesk_id
        )
        bank_account = finance_factories.BankAccountFactory(offerer=finance_incident.venue.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(venue=finance_incident.venue, bankAccount=bank_account)
        finance_factories.IndividualBookingFinanceCommercialGestureFactory(
            incident=finance_incident,
            newTotalAmount=0,
            booking__user__deposit__type=finance_models.DepositType.GRANT_18,
        )
        url = url_for(self.endpoint, finance_incident_id=finance_incident.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        badges = html_parser.extract_badges(response.data)
        assert badges == ["Créé", "Total", "Annulée", "Ancien Pass 18"]  # incident badges + booking badges

        content = html_parser.content_as_text(response.data)
        assert f"ID : {finance_incident.id}" in content
        assert f"Partenaire culturel porteur de l'offre : {finance_incident.venue.name}" in content
        assert f"Compte bancaire : {bank_account.label}" in content
        if zendesk_id:
            assert f"Ticket Zendesk : {zendesk_id}" in content
        else:
            assert "Ticket Zendesk" not in content
        assert f"Montant d'origine de la réservation : 10,10 € {expected_xpf_text}" in content
        assert f"Montant du geste commercial à verser à l'acteur : 10,10 € {expected_xpf_text}" in content
        assert f"Geste commercial créé par : {finance_incident.details['author']}" in content
        assert "Batch :" not in content
        assert "Justificatif de remboursement :" not in content

    @pytest.mark.parametrize("zendesk_id", [None, "1"])
    def test_get_collective_booking_incident(self, authenticated_client, zendesk_id):
        finance_incident = finance_factories.FinanceIncidentFactory(
            kind=finance_models.IncidentType.COMMERCIAL_GESTURE,
            booking_finance_incidents=[finance_factories.CollectiveBookingFinanceIncidentFactory()],
            zendeskId=zendesk_id,
        )
        finance_factories.CollectiveBookingFinanceIncidentFactory(incident=finance_incident)
        url = url_for(self.endpoint, finance_incident_id=finance_incident.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)

        assert f"ID : {finance_incident.id}" in content
        assert f"Partenaire culturel porteur de l'offre : {finance_incident.venue.name}" in content
        if zendesk_id:
            assert f"Ticket Zendesk : {zendesk_id}" in content
        else:
            assert "Ticket Zendesk" not in content
        assert f"Geste commercial créé par : {finance_incident.details['author']}" in content
        assert "Batch :" not in content
        assert "Justificatif de remboursement :" not in content

    def test_get_batch_info(self, authenticated_client):
        bank_account = finance_factories.BankAccountFactory()
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerers_factories.UserOffererFactory().offerer, bank_account=bank_account
        )
        invoice = finance_factories.InvoiceFactory()
        cashflow = finance_factories.CashflowFactory(
            status=finance_models.CashflowStatus.ACCEPTED,
            bankAccount=bank_account,
            batch__label="VIR1",
            invoices=[invoice],
        )
        pricing = finance_factories.PricingFactory(
            status=finance_models.PricingStatus.INVOICED,
            cashflows=[cashflow],
        )
        finance_incident = finance_factories.FinanceIncidentFactory(kind=finance_models.IncidentType.COMMERCIAL_GESTURE)
        booking_finance_incident = finance_factories.IndividualBookingFinanceIncidentFactory(
            incident=finance_incident,
        )
        finance_factories.FinanceEventFactory(
            venue=venue,
            bookingFinanceIncident=booking_finance_incident,
            booking=None,
            valueDate=date_utils.get_naive_utc_now(),
            status=finance_models.FinanceEventStatus.PRICED,
            pricings=[pricing],
            pricingPoint=venue,
            pricingOrderingDate=date_utils.get_naive_utc_now(),
        )

        url = url_for(self.endpoint, finance_incident_id=finance_incident.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)

        assert f"ID : {finance_incident.id}" in content
        assert f"Partenaire culturel porteur de l'offre : {finance_incident.venue.name}" in content
        assert f"Geste commercial créé par : {finance_incident.details['author']}" in content
        assert "Batch : VIR1" in content
        assert "Justificatif de remboursement : PDF" in content
        assert (
            invoice.url
            in html_parser.get_tag(html_content=response.data, class_="link-primary", tag="a", download=True).decode()
        )


class GetOverpaymentCreationFormTest(PostEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.get_individual_bookings_overpayment_creation_form"
    needed_permission = perm_models.Permissions.CREATE_INCIDENTS
    error_message_template = "Erreur %s Annuler"

    expected_num_queries = 5

    @pytest.mark.parametrize(
        "venue_factory,show_xfp_amount",
        [
            (offerers_factories.VenueFactory, False),
            (offerers_factories.CaledonianVenueFactory, True),
        ],
    )
    def test_get_overpayment_creation_for_one_booking_form(self, authenticated_client, venue_factory, show_xfp_amount):
        venue = venue_factory()
        offer = offers_factories.OfferFactory(venue=venue)
        stock = offers_factories.StockFactory(offer=offer)
        booking = bookings_factories.ReimbursedBookingFactory(
            stock=stock,
            pricings=[finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED, amount=-1000)],
        )
        object_ids = str(booking.id)

        with assert_num_queries(self.expected_num_queries):
            response = self.post_to_endpoint(
                authenticated_client,
                form={"object_ids": object_ids},
                headers={"hx-request": "true"},
            )
            assert response.status_code == 200

        additional_data_text = html_parser.extract_cards_text(response.data)[0]
        assert f"Partenaire culturel : {venue.name}" in additional_data_text
        assert f"ID de la réservation : {booking.id}" in additional_data_text
        assert f"Statut de la réservation : {format_booking_status(booking)}" in additional_data_text
        assert f"Contremarque : {booking.token}" in additional_data_text
        assert f"Nom de l'offre : {offer.name}" in additional_data_text
        assert f"Bénéficiaire : {booking.user.full_name}" in additional_data_text
        if show_xfp_amount:
            assert "Montant de la réservation : 10,10 € (1205 CFP)" in additional_data_text
            assert "Montant remboursé à l'acteur : 10,00 € (1195 CFP)" in additional_data_text
        else:
            assert "Montant de la réservation : 10,10 €" in additional_data_text
            assert "Montant remboursé à l'acteur : 10,00 €" in additional_data_text
            assert "CFP" not in additional_data_text

        default_amount = html_parser.extract_input_value(response.data, "total_amount")
        assert default_amount == str(booking.total_amount)

    def test_get_overpayment_creation_for_multiple_bookings_form(self, authenticated_client):
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
            response = self.post_to_endpoint(
                authenticated_client,
                form={"object_ids": object_ids},
                headers={"hx-request": "true"},
            )
            assert response.status_code == 200

        additional_data_text = html_parser.extract_cards_text(response.data)[0]
        assert f"Partenaire culturel : {venue.name}" in additional_data_text
        assert f"Nombre de réservations : {len(selected_bookings)}" in additional_data_text
        assert "Montant des réservations : 20,20 €" in additional_data_text
        assert "Montant remboursé à l'acteur : 20,20 €" in additional_data_text

    def test_display_error_if_booking_not_reimbursed(self, authenticated_client):
        booking = bookings_factories.UsedBookingFactory()
        object_ids = str(booking.id)

        # don't query the number of BookingFinanceIncident with FinanceIncident's status in
        # (CREATED, VALIDATED)
        # but adds 1 query for the rollback
        with assert_num_queries(self.expected_num_queries):
            response = self.post_to_endpoint(
                authenticated_client,
                form={"object_ids": object_ids},
                headers={"hx-request": "true"},
            )

        assert (
            html_parser.content_as_text(response.data)
            == self.error_message_template
            % """Seules les réservations ayant le statut "remboursée" peuvent faire l'objet d'un trop perçu."""
        )

    def test_display_error_if_bookings_from_different_venues_selected(self, authenticated_client):
        selected_bookings = bookings_factories.ReimbursedBookingFactory.create_batch(2)
        object_ids = ",".join(str(booking.id) for booking in selected_bookings)

        # don't query the number of BookingFinanceIncident with FinanceIncident's status in
        # (CREATED, VALIDATED)
        # but adds 1 query for rollback
        with assert_num_queries(self.expected_num_queries):
            response = self.post_to_endpoint(
                authenticated_client,
                form={"object_ids": object_ids},
                headers={"hx-request": "true"},
            )

        assert (
            html_parser.content_as_text(response.data)
            == self.error_message_template
            % "Un incident ne peut être créé qu'à partir de réservations venant du même partenaire culturel."
        )


class GetCollectiveBookingOverpaymentFormTest(PostEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.get_collective_booking_overpayment_creation_form"
    endpoint_kwargs = {"collective_booking_id": 1}
    needed_permission = perm_models.Permissions.CREATE_INCIDENTS

    expected_num_queries = 8

    def test_get_form(self, authenticated_client):
        collective_booking = educational_factories.ReimbursedCollectiveBookingFactory(
            pricings=[finance_factories.CollectivePricingFactory(status=finance_models.PricingStatus.INVOICED)]
        )

        with assert_num_queries(self.expected_num_queries):
            response = self.post_to_endpoint(
                authenticated_client,
                collective_booking_id=collective_booking.id,
                headers={"hx-request": "true"},
            )
            assert response.status_code == 200

        additional_data_text = html_parser.extract_cards_text(response.data)[0]

        assert f"ID de la réservation : {collective_booking.id}" in additional_data_text
        assert "Statut de la réservation : Remboursée" in additional_data_text
        assert f"Nom de l'offre : {collective_booking.collectiveStock.collectiveOffer.name}" in additional_data_text
        assert (
            f"Date de l'offre : {format_date_time(collective_booking.collectiveStock.startDatetime)}"
            in additional_data_text
        )
        assert f"Établissement : {collective_booking.educationalInstitution.name}" in additional_data_text
        assert f"Nombre d'élèves : {collective_booking.collectiveStock.numberOfTickets}" in additional_data_text
        assert "Montant de la réservation : 100,00 €" in additional_data_text
        assert "Montant remboursé à l'acteur : 100,00 €" in additional_data_text


class CreateOverpaymentTest(PostEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.create_individual_booking_overpayment"
    needed_permission = perm_models.Permissions.CREATE_INCIDENTS

    @pytest.mark.parametrize("zendesk_id", [None, 1])
    @pytest.mark.parametrize("comment", [None, "Commentaire facultatif"])
    def test_create_incident_from_one_booking(self, legit_user, authenticated_client, zendesk_id, comment):
        booking = bookings_factories.ReimbursedBookingFactory(
            pricings=[finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED, amount=-1000)],
        )

        object_ids = str(booking.id)

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "total_amount": booking.amount,
                "origin": finance_models.FinanceIncidentRequestOrigin.SUPPORT_JEUNE.name,
                "comment": comment,
                "zendesk_id": zendesk_id,
                "kind": finance_models.IncidentType.OVERPAYMENT.name,
                "object_ids": object_ids,
            },
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"booking-row-{booking.id}")
        assert cells[2] == str(booking.id)

        incidents = db.session.query(finance_models.FinanceIncident).all()
        assert len(incidents) == 1
        assert db.session.query(finance_models.BookingFinanceIncident).count() == 1
        booking_finance_incident = db.session.query(finance_models.BookingFinanceIncident).first()
        assert booking_finance_incident.newTotalAmount == 0
        assert booking_finance_incident.incident.origin == finance_models.FinanceIncidentRequestOrigin.SUPPORT_JEUNE
        assert booking_finance_incident.incident.comment == comment
        assert booking_finance_incident.incident.zendeskId == zendesk_id

        action_history = db.session.query(history_models.ActionHistory).one()
        assert action_history.actionType == history_models.ActionType.FINANCE_INCIDENT_CREATED
        assert action_history.authorUser == legit_user
        assert action_history.comment == comment

        alerts = flash.get_htmx_flash_messages(authenticated_client)
        assert "Un nouvel incident a été créé pour 1 réservation." in alerts["success"]

    def test_not_creating_incident_if_already_exists(self, authenticated_client):
        booking = bookings_factories.ReimbursedBookingFactory()
        finance_factories.IndividualBookingFinanceIncidentFactory(booking=booking)
        object_ids = str(booking.id)

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "total_amount": booking.amount,
                "origin": finance_models.FinanceIncidentRequestOrigin.SUPPORT_JEUNE.name,
                "comment": "Commentaire facultatif",
                "kind": finance_models.IncidentType.OVERPAYMENT.name,
                "object_ids": object_ids,
            },
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"booking-row-{booking.id}")
        assert cells[2] == str(booking.id)

        alerts = flash.get_htmx_flash_messages(authenticated_client)
        assert (
            "Au moins une des réservations fait déjà l'objet d'un incident ou geste commercial non annulé."
            in alerts["warning"]
        )

        assert db.session.query(finance_models.FinanceIncident).count() == 1  # didn't create new incident
        assert db.session.query(history_models.ActionHistory).count() == 0

    @pytest.mark.parametrize(
        "zendesk_id, comment, percent, expected_cents_1, expected_cents_2",
        [(None, None, 100, 0, 0), (1, "Commentaire facultatif", 40, 1218, 1950)],
    )
    def test_create_incident_from_multiple_bookings(
        self, legit_user, authenticated_client, zendesk_id, comment, percent, expected_cents_1, expected_cents_2
    ):
        venue = offerers_factories.VenueFactory()
        offer = offers_factories.OfferFactory(venue=venue)
        stock_1 = offers_factories.StockFactory(offer=offer, price=decimal.Decimal("20.3"))
        stock_2 = offers_factories.StockFactory(offer=offer, price=decimal.Decimal("32.5"))
        selected_bookings = [
            bookings_factories.ReimbursedBookingFactory(
                stock=stock_1, pricings=[finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED)]
            ),
            bookings_factories.ReimbursedBookingFactory(
                stock=stock_2, pricings=[finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED)]
            ),
        ]
        object_ids = ",".join([str(booking.id) for booking in selected_bookings])

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "percent": percent,
                "origin": finance_models.FinanceIncidentRequestOrigin.SUPPORT_JEUNE.name,
                "comment": comment,
                "zendesk_id": zendesk_id,
                "kind": finance_models.IncidentType.OVERPAYMENT.name,
                "object_ids": object_ids,
            },
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        for booking in selected_bookings:
            cells = html_parser.extract_plain_row(response.data, id=f"booking-row-{booking.id}")
            assert cells[2] == str(booking.id)

        assert db.session.query(finance_models.FinanceIncident).count() == 1
        finance_incident = db.session.query(finance_models.FinanceIncident).first()
        assert finance_incident.comment == comment
        assert finance_incident.zendeskId == zendesk_id
        assert finance_incident.origin == finance_models.FinanceIncidentRequestOrigin.SUPPORT_JEUNE

        assert db.session.query(finance_models.BookingFinanceIncident).count() == 2
        assert (
            db.session.query(finance_models.BookingFinanceIncident)
            .filter_by(bookingId=selected_bookings[0].id)
            .one()
            .newTotalAmount
            == expected_cents_1
        )
        assert (
            db.session.query(finance_models.BookingFinanceIncident)
            .filter_by(bookingId=selected_bookings[1].id)
            .one()
            .newTotalAmount
            == expected_cents_2
        )

        action_history = db.session.query(history_models.ActionHistory).one()
        assert action_history.actionType == history_models.ActionType.FINANCE_INCIDENT_CREATED
        assert action_history.authorUser == legit_user
        assert action_history.comment == comment

    def test_not_create_overpayment_incident_from_used_booking(self, authenticated_client):
        booking = bookings_factories.UsedBookingFactory()

        object_ids = str(booking.id)

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "total_amount": booking.amount,
                "origin": finance_models.FinanceIncidentRequestOrigin.SUPPORT_JEUNE.name,
                "comment": "Commentaire facultatif",
                "kind": finance_models.IncidentType.OVERPAYMENT.name,
                "object_ids": object_ids,
            },
        )

        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"booking-row-{booking.id}")
        assert cells[2] == str(booking.id)

        alerts = flash.get_htmx_flash_messages(authenticated_client)
        assert (
            'Au moins une des réservations sélectionnées est dans un état différent de "remboursé".'
            in alerts["warning"]
        )

        assert db.session.query(finance_models.FinanceIncident).count() == 0  # didn't create new incident
        assert db.session.query(history_models.ActionHistory).count() == 0

    @pytest.mark.parametrize(
        "percent, expected_alert",
        [
            ("0", "Impossible de créer un incident de 0 %%."),
            (
                "101",
                "Les données envoyées comportent des erreurs. Pourcentage du montant des réservations à récupérer : Le pourcentage doit être compris entre 0 % et 100 %. ;",
            ),
            (
                "-1",
                "Les données envoyées comportent des erreurs. Pourcentage du montant des réservations à récupérer : Le pourcentage doit être compris entre 0 % et 100 %. ;",
            ),
        ],
    )
    def test_can_not_create_incident_from_multiple_bookings_with_invalid_percent(
        self, authenticated_client, percent, expected_alert
    ):
        offer = offers_factories.OfferFactory()
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

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "percent": percent,
                "origin": finance_models.FinanceIncidentRequestOrigin.SUPPORT_JEUNE.name,
                "comment": "test",
                "zendesk_id": "",
                "kind": finance_models.IncidentType.OVERPAYMENT.name,
                "object_ids": object_ids,
            },
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200

        alerts = flash.get_htmx_flash_messages(authenticated_client)
        assert expected_alert in alerts["warning"]

        assert db.session.query(finance_models.FinanceIncident).count() == 0
        assert db.session.query(finance_models.BookingFinanceIncident).count() == 0
        assert db.session.query(history_models.ActionHistory).count() == 0


class GetCommercialGestureCreationFormTest(PostEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.get_individual_bookings_commercial_gesture_creation_form"
    needed_permission = perm_models.Permissions.CREATE_INCIDENTS
    error_message_template = "Erreur %s Annuler"

    expected_num_queries = 5

    @pytest.mark.parametrize(
        "venue_factory,show_xfp_amount",
        [
            (offerers_factories.VenueFactory, False),
            (offerers_factories.CaledonianVenueFactory, True),
        ],
    )
    def test_get_commercial_gesture_creation_for_one_booking_form(
        self, authenticated_client, venue_factory, show_xfp_amount
    ):
        venue = venue_factory(name="Etablissement")
        offer = offers_factories.OfferFactory(venue=venue, name="Offre ++")
        stock = offers_factories.StockFactory(offer=offer)
        invoiced_pricing = finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED, amount=-10_00)
        booking = bookings_factories.CancelledBookingFactory(
            stock=stock,
            pricings=[invoiced_pricing],
            quantity=4,
            amount=decimal.Decimal(50),
            token="TOK3N",
            user__firstName="John",
            user__lastName="Doe",
        )
        object_ids = str(booking.id)

        with assert_num_queries(self.expected_num_queries):
            response = self.post_to_endpoint(authenticated_client, form={"object_ids": object_ids})
            assert response.status_code == 200

        additional_data_text = html_parser.extract_cards_text(response.data)[0]
        assert "Partenaire culturel : Etablissement" in additional_data_text
        assert f"ID de la réservation : {booking.id}" in additional_data_text
        assert "Statut de la réservation : Annulée" in additional_data_text
        assert "Contremarque : TOK3N" in additional_data_text
        assert "Nom de l'offre : Offre ++" in additional_data_text
        assert "Bénéficiaire : John Doe" in additional_data_text
        if show_xfp_amount:
            assert "Montant de la réservation : 200,00 € (23865 CFP)" in additional_data_text
            assert "Montant remboursé à l'acteur : 10,00 € (1195 CFP)" in additional_data_text
        else:
            assert "Montant de la réservation : 200,00 €" in additional_data_text
            assert "Montant remboursé à l'acteur : 10,00 €" in additional_data_text
            assert "CFP" not in additional_data_text

        default_amount = html_parser.extract_input_value(response.data, "total_amount")
        assert default_amount == str(booking.total_amount)

    def test_get_commercial_gesture_creation_for_multiple_bookings_form(self, authenticated_client):
        venue = offerers_factories.VenueFactory(name="Etablissement")
        offer = offers_factories.OfferFactory(venue=venue)
        stock = offers_factories.StockFactory(offer=offer)
        booking1 = bookings_factories.CancelledBookingFactory(
            stock=stock,
            pricings=[finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED, amount=-3_00)],
            quantity=4,
            amount=decimal.Decimal(3),
        )
        booking2 = bookings_factories.CancelledBookingFactory(
            stock=stock,
            pricings=[finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED, amount=-4_00)],
            quantity=9,
            amount=decimal.Decimal(6),
        )
        object_ids = f"{booking1.id},{booking2.id}"

        with assert_num_queries(self.expected_num_queries):
            response = self.post_to_endpoint(authenticated_client, form={"object_ids": object_ids})
            assert response.status_code == 200

        additional_data_text = html_parser.extract_cards_text(response.data)[0]
        assert "Partenaire culturel : Etablissement" in additional_data_text
        assert "Nombre de réservations : 2" in additional_data_text
        assert "Montant des réservations : 66,00 €" in additional_data_text
        assert "Montant remboursé à l'acteur : 7,00 €" in additional_data_text

    def test_display_error_if_booking_not_cancelled(self, authenticated_client):
        booking = bookings_factories.UsedBookingFactory()
        object_ids = str(booking.id)

        # don't query the number of BookingFinanceIncident with FinanceIncident's status in
        # (CREATED, VALIDATED)
        # but adds 1 query for rollback
        with assert_num_queries(self.expected_num_queries):
            response = self.post_to_endpoint(authenticated_client, form={"object_ids": object_ids})

        assert (
            html_parser.content_as_text(response.data)
            == self.error_message_template
            % """Seules les réservations ayant le statut "annulée" peuvent faire l'objet d'un geste comercial."""
        )

    def test_display_error_if_bookings_from_different_venues_selected(self, authenticated_client):
        booking1, booking2 = bookings_factories.CancelledBookingFactory.create_batch(2)
        object_ids = f"{booking1.id},{booking2.id}"

        # add 1 query for rollback
        with assert_num_queries(self.expected_num_queries + 1):
            response = self.post_to_endpoint(authenticated_client, form={"object_ids": object_ids})

        assert (
            html_parser.content_as_text(response.data)
            == self.error_message_template
            % "Un geste commercial ne peut concerner que des réservations faites sur un même stock."
        )


class CreateCommercialGestureTest(PostEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.create_individual_booking_commercial_gesture"
    needed_permission = perm_models.Permissions.CREATE_INCIDENTS

    @pytest.mark.parametrize("zendesk_id", [None, 1])
    @pytest.mark.parametrize("comment", [None, "Commentaire facultatif"])
    def test_create_commercial_gesture_incident_from_one_booking_without_deposit_balance(
        self, legit_user, authenticated_client, zendesk_id, comment
    ):
        booking = bookings_factories.CancelledBookingFactory(
            quantity=1,
            amount=11,
            user__deposit__amount=decimal.Decimal(2.0),
        )

        object_ids = str(booking.id)
        total_amount = 11
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "total_amount": total_amount,
                "origin": finance_models.FinanceIncidentRequestOrigin.SUPPORT_JEUNE.name,
                "comment": comment,
                "zendesk_id": zendesk_id,
                "kind": finance_models.IncidentType.COMMERCIAL_GESTURE.name,
                "object_ids": object_ids,
            },
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"booking-row-{booking.id}")
        assert cells[2] == str(booking.id)

        assert db.session.query(finance_models.FinanceIncident).count() == 1
        assert db.session.query(finance_models.BookingFinanceIncident).count() == 1
        booking_finance_incident = db.session.query(finance_models.BookingFinanceIncident).first()
        assert booking_finance_incident.newTotalAmount == 0
        assert booking_finance_incident.incident.origin == finance_models.FinanceIncidentRequestOrigin.SUPPORT_JEUNE
        assert booking_finance_incident.incident.comment == comment
        assert booking_finance_incident.incident.zendeskId == zendesk_id

        action_history = db.session.query(history_models.ActionHistory).one()
        assert action_history.actionType == history_models.ActionType.FINANCE_INCIDENT_CREATED
        assert action_history.authorUser == legit_user
        assert action_history.comment == comment

    def test_create_commercial_gesture_incident_from_one_booking_with_deposit_balance(
        self, legit_user, authenticated_client
    ):
        booking = bookings_factories.CancelledBookingFactory()

        object_ids = str(booking.id)
        total_amount = 11
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "total_amount": total_amount,
                "origin": finance_models.FinanceIncidentRequestOrigin.SUPPORT_JEUNE.name,
                "comment": "Commentaire facultatif",
                "kind": finance_models.IncidentType.COMMERCIAL_GESTURE.name,
                "object_ids": object_ids,
            },
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"booking-row-{booking.id}")
        assert cells[2] == str(booking.id)

        assert db.session.query(finance_models.FinanceIncident).count() == 0
        assert db.session.query(finance_models.BookingFinanceIncident).count() == 0

        alerts = flash.get_htmx_flash_messages(authenticated_client)
        assert (
            "Au moins un des jeunes ayant fait une réservation a encore du crédit pour payer la réservation."
            in alerts["warning"]
        )

    def test_create_commercial_gesture_incident_from_used_booking(self, legit_user, authenticated_client):
        booking = bookings_factories.UsedBookingFactory()

        object_ids = str(booking.id)
        total_amount = 11
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "total_amount": total_amount,
                "origin": finance_models.FinanceIncidentRequestOrigin.SUPPORT_JEUNE.name,
                "comment": "Commentaire facultatif",
                "kind": finance_models.IncidentType.COMMERCIAL_GESTURE.name,
                "object_ids": object_ids,
            },
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"booking-row-{booking.id}")
        assert cells[2] == str(booking.id)

        assert db.session.query(finance_models.FinanceIncident).count() == 0
        assert db.session.query(finance_models.BookingFinanceIncident).count() == 0

        alerts = flash.get_htmx_flash_messages(authenticated_client)
        assert (
            'Au moins une des réservations sélectionnées est dans un état différent de "annulée".' in alerts["warning"]
        )

    def test_not_create_commercial_gesture_incident_too_expensive(self, authenticated_client):
        booking = bookings_factories.UsedBookingFactory()

        object_ids = str(booking.id)

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "total_amount": booking.amount * decimal.Decimal(1.21),
                "origin": finance_models.FinanceIncidentRequestOrigin.SUPPORT_JEUNE.name,
                "comment": "Commentaire facultatif",
                "kind": finance_models.IncidentType.COMMERCIAL_GESTURE.name,
                "object_ids": object_ids,
            },
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"booking-row-{booking.id}")
        assert cells[2] == str(booking.id)

        assert db.session.query(finance_models.FinanceIncident).count() == 0  # didn't create new incident
        assert db.session.query(history_models.ActionHistory).count() == 0

        alerts = flash.get_htmx_flash_messages(authenticated_client)
        assert (
            'Au moins une des réservations sélectionnées est dans un état différent de "annulée".' in alerts["warning"]
        )

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
                "origin": finance_models.FinanceIncidentRequestOrigin.SUPPORT_JEUNE.name,
                "comment": "Commentaire facultatif",
                "kind": finance_models.IncidentType.COMMERCIAL_GESTURE.name,
                "object_ids": object_ids,
            },
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        for booking in selected_bookings:
            cells = html_parser.extract_plain_row(response.data, id=f"booking-row-{booking.id}")
            assert cells[2] == str(booking.id)

        alerts = flash.get_htmx_flash_messages(authenticated_client)
        assert (
            'Au moins une des réservations sélectionnées est dans un état différent de "annulée".' in alerts["warning"]
        )

        assert db.session.query(finance_models.FinanceIncident).count() == 0  # didn't create new incident
        assert db.session.query(history_models.ActionHistory).count() == 0


class CreateCollectiveBookingOverpaymentTest(PostEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.create_collective_booking_overpayment"
    endpoint_kwargs = {"collective_booking_id": 1}
    needed_permission = perm_models.Permissions.CREATE_INCIDENTS

    @pytest.mark.parametrize("zendesk_id", [None, 1])
    @pytest.mark.parametrize("comment", [None, "Commentaire facultatif"])
    def test_create_incident(self, authenticated_client, zendesk_id, comment):
        collective_booking = educational_factories.ReimbursedCollectiveBookingFactory(
            pricings=[finance_factories.CollectivePricingFactory(status=finance_models.PricingStatus.INVOICED)],
        )

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "origin": finance_models.FinanceIncidentRequestOrigin.SUPPORT_JEUNE.name,
                "comment": comment,
                "kind": finance_models.IncidentType.OVERPAYMENT.name,
                "zendesk_id": zendesk_id,
            },
            collective_booking_id=collective_booking.id,
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"booking-row-{collective_booking.id}")
        assert cells[1] == str(collective_booking.id)

        finance_incidents = db.session.query(finance_models.FinanceIncident).all()
        assert len(finance_incidents) == 1
        assert finance_incidents[0].origin == finance_models.FinanceIncidentRequestOrigin.SUPPORT_JEUNE
        assert finance_incidents[0].comment == comment
        assert finance_incidents[0].zendeskId == zendesk_id
        assert finance_incidents[0].kind == finance_models.IncidentType.OVERPAYMENT

        booking_incidents = finance_incidents[0].booking_finance_incidents
        assert len(booking_incidents) == 1
        assert booking_incidents[0].collectiveBookingId == collective_booking.id
        assert booking_incidents[0].newTotalAmount == 0

        alerts = flash.get_htmx_flash_messages(authenticated_client)
        assert "Un nouvel incident a été créé." in alerts["success"]

    @pytest.mark.parametrize(
        "incident_status,expected_incident_count",
        [
            (finance_models.IncidentStatus.CREATED, 1),
            (finance_models.IncidentStatus.VALIDATED, 1),
        ],
    )
    def test_incident_already_exists(self, authenticated_client, incident_status, expected_incident_count):
        collective_booking = educational_factories.ReimbursedCollectiveBookingFactory(
            pricings=[finance_factories.CollectivePricingFactory(status=finance_models.PricingStatus.INVOICED)],
        )
        finance_factories.CollectiveBookingFinanceIncidentFactory(
            collectiveBooking=collective_booking, incident__status=incident_status
        )

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "origin": finance_models.FinanceIncidentRequestOrigin.SUPPORT_JEUNE.name,
                "comment": "Demande E-mail",
                "kind": finance_models.IncidentType.OVERPAYMENT.name,
            },
            collective_booking_id=collective_booking.id,
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"booking-row-{collective_booking.id}")
        assert cells[1] == str(collective_booking.id)

        assert db.session.query(finance_models.FinanceIncident).count() == expected_incident_count

        alerts = flash.get_htmx_flash_messages(authenticated_client)
        assert (
            """Cette réservation fait déjà l'objet d'un incident au statut "créé" ou "validé".""" in alerts["warning"]
        )

    def test_incident_already_exists_cancelled(self, authenticated_client):
        collective_booking = educational_factories.ReimbursedCollectiveBookingFactory(
            pricings=[finance_factories.CollectivePricingFactory(status=finance_models.PricingStatus.INVOICED)],
        )
        finance_factories.CollectiveBookingFinanceIncidentFactory(
            collectiveBooking=collective_booking, incident__status=finance_models.IncidentStatus.CANCELLED
        )

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "origin": finance_models.FinanceIncidentRequestOrigin.SUPPORT_JEUNE.name,
                "comment": "Demande E-mail",
                "kind": finance_models.IncidentType.OVERPAYMENT.name,
            },
            collective_booking_id=collective_booking.id,
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"booking-row-{collective_booking.id}")
        assert cells[1] == str(collective_booking.id)

        assert db.session.query(finance_models.FinanceIncident).count() == 2
        alerts = flash.get_htmx_flash_messages(authenticated_client)
        assert "Un nouvel incident a été créé." in alerts["success"]


class GetIncidentHistoryTest(GetEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.get_history"
    endpoint_kwargs = {"finance_incident_id": 1}
    needed_permission = perm_models.Permissions.READ_INCIDENTS

    # session + incident data
    expected_num_queries = 2

    def test_get_incident_history(self, legit_user, authenticated_client):
        finance_incident = finance_factories.FinanceIncidentFactory()
        action = history_factories.ActionHistoryFactory(
            financeIncident=finance_incident,
            actionType=history_models.ActionType.FINANCE_INCIDENT_CREATED,
            actionDate=date_utils.get_naive_utc_now() + datetime.timedelta(days=-1),
        )
        author = users_factories.UserFactory()
        api.cancel_finance_incident(finance_incident, comment="Je décide d'annuler l'incident", author=author)

        finance_incident_id = finance_incident.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, finance_incident_id=finance_incident_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        iterator_actions = iter(rows)
        cancel_action = next(iterator_actions)
        creation_action = next(iterator_actions)
        assert cancel_action["Type"] == "Annulation de l'incident"
        assert creation_action["Type"] == "Création de l'incident"
        assert creation_action["Date/Heure"].startswith(action.actionDate.strftime("%d/%m/%Y à "))
        assert creation_action["Commentaire"] == action.comment
        assert creation_action["Auteur"] == action.authorUser.full_name


class ForceDebitNoteTest(PostEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.force_debit_note"
    endpoint_kwargs = {"finance_incident_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_INCIDENTS

    def test_force_debit_note(self, authenticated_client):
        venue = offerers_factories.VenueFactory(pricing_point="self")
        booking = bookings_factories.ReimbursedBookingFactory(stock__offer__venue=venue)
        original_event = finance_factories.UsedBookingFinanceEventFactory(booking=booking)
        original_pricing = api.price_event(original_event)
        original_pricing.status = finance_models.PricingStatus.INVOICED

        now = date_utils.get_naive_utc_now()
        finance_incident = finance_factories.IndividualBookingFinanceIncidentFactory(
            booking=booking, incident__status=finance_models.IncidentStatus.VALIDATED, incident__forceDebitNote=False
        ).incident
        api._create_finance_events_from_incident(
            finance_incident.booking_finance_incidents[0], incident_validation_date=now
        )

        response = self.post_to_endpoint(
            authenticated_client,
            finance_incident_id=finance_incident.id,
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert "Une note de débit sera générée à la prochaine échéance." in html_parser.extract_alert(response.data)
        updated_finance_incident = (
            db.session.query(finance_models.FinanceIncident).filter_by(id=finance_incident.id).one()
        )
        assert updated_finance_incident.forceDebitNote is True

    @pytest.mark.parametrize(
        "incident_status",
        [
            finance_models.IncidentStatus.CANCELLED,
            finance_models.IncidentStatus.CREATED,
            finance_models.IncidentStatus.INVOICED,
        ],
    )
    def test_not_force_debit_note(self, authenticated_client, incident_status):
        original_finance_incident = finance_factories.FinanceIncidentFactory(status=incident_status)

        response = self.post_to_endpoint(
            authenticated_client,
            finance_incident_id=original_finance_incident.id,
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert (
            "Cette action ne peut être effectuée que sur un incident validé non terminé."
            == html_parser.extract_alert(response.data)
        )
        finance_incident = (
            db.session.query(finance_models.FinanceIncident).filter_by(id=original_finance_incident.id).one()
        )
        assert finance_incident.forceDebitNote is False

    def test_force_debit_note_on_finished_incident(self, authenticated_client):
        venue = offerers_factories.VenueFactory(pricing_point="self")
        bank_account = finance_factories.BankAccountFactory(offerer=venue.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=bank_account)
        booking = bookings_factories.ReimbursedBookingFactory(stock__offer__venue=venue)
        original_event = finance_factories.UsedBookingFinanceEventFactory(booking=booking)
        original_pricing = api.price_event(original_event)
        original_pricing.status = finance_models.PricingStatus.INVOICED

        original_finance_incident = finance_factories.IndividualBookingFinanceIncidentFactory(
            booking=booking, incident__status=finance_models.IncidentStatus.INVOICED, incident__venue=venue
        ).incident
        events_to_price = []
        events_to_price.extend(
            api._create_finance_events_from_incident(
                original_finance_incident.booking_finance_incidents[0],
                incident_validation_date=date_utils.get_naive_utc_now(),
            )
        )
        booking = bookings_factories.UsedBookingFactory(stock__offer__venue=venue, amount=20)
        events_to_price.append(
            finance_factories.FinanceEventFactory(
                venue=venue, booking=booking, status=finance_models.FinanceEventStatus.READY
            )
        )

        for event in events_to_price:
            api.price_event(event)

        cashflow_batch = api.generate_cashflows_and_payment_files(date_utils.get_naive_utc_now())
        generated_cashflow = cashflow_batch.cashflows[0]
        generated_cashflow.status = finance_models.CashflowStatus.ACCEPTED

        response = self.post_to_endpoint(
            authenticated_client,
            finance_incident_id=original_finance_incident.id,
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert (
            "Cette action ne peut être effectuée que sur un incident validé non terminé."
            == html_parser.extract_alert(response.data)
        )
        finance_incident = (
            db.session.query(finance_models.FinanceIncident).filter_by(id=original_finance_incident.id).one()
        )
        assert finance_incident.forceDebitNote is False


class CancelDebitNoteTest(PostEndpointHelper):
    endpoint = "backoffice_web.finance_incidents.cancel_debit_note"
    endpoint_kwargs = {"finance_incident_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_INCIDENTS

    def test_cancel_debit_note(self, authenticated_client):
        venue = offerers_factories.VenueBankAccountLinkFactory().venue
        offerers_factories.VenuePricingPointLinkFactory(
            venue=venue,
            pricingPoint=venue,
        )
        booking = bookings_factories.ReimbursedBookingFactory(stock__offer__venue=venue)
        original_event = finance_factories.UsedBookingFinanceEventFactory(booking=booking, pricingPointId=venue.id)
        original_pricing = api.price_event(original_event)
        original_pricing.status = finance_models.PricingStatus.INVOICED

        now = date_utils.get_naive_utc_now()
        finance_incident = finance_factories.IndividualBookingFinanceIncidentFactory(
            booking=booking,
            incident__status=finance_models.IncidentStatus.VALIDATED,
            incident__forceDebitNote=True,
            incident__venue=venue,
        ).incident
        api._create_finance_events_from_incident(
            finance_incident.booking_finance_incidents[0], incident_validation_date=now
        )

        response = self.post_to_endpoint(
            authenticated_client,
            finance_incident_id=finance_incident.id,
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert (
            "Vous avez fait le choix de récupérer l'argent sur les prochaines réservations de l'acteur."
            in html_parser.content_as_text(response.data)
        )

        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0]["template"]
            == TransactionalEmail.RETRIEVE_INCIDENT_AMOUNT_ON_INDIVIDUAL_BOOKINGS.value.__dict__
        )
        assert mails_testing.outbox[0]["To"] == venue.bookingEmail
        assert mails_testing.outbox[0]["params"] == {
            "VENUE_NAME": venue.publicName,
            "OFFER_NAME": booking.stock.offer.name,
            "TOKEN_LIST": booking.token,
        }
        updated_finance_incident = (
            db.session.query(finance_models.FinanceIncident).filter_by(id=finance_incident.id).one()
        )
        assert updated_finance_incident.forceDebitNote is False

    @pytest.mark.parametrize(
        "incident_status",
        [
            finance_models.IncidentStatus.CANCELLED,
            finance_models.IncidentStatus.CREATED,
            finance_models.IncidentStatus.INVOICED,
        ],
    )
    def test_not_cancel_debit_note(self, authenticated_client, incident_status):
        original_finance_incident = finance_factories.FinanceIncidentFactory(
            status=incident_status, forceDebitNote=True
        )

        response = self.post_to_endpoint(
            authenticated_client,
            finance_incident_id=original_finance_incident.id,
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert (
            "Cette action ne peut être effectuée que sur un incident validé non terminé."
            == html_parser.extract_alert(response.data)
        )
        finance_incident = (
            db.session.query(finance_models.FinanceIncident).filter_by(id=original_finance_incident.id).one()
        )
        assert finance_incident.forceDebitNote == original_finance_incident.forceDebitNote

    def test_cancel_debit_note_on_finished_incident(self, authenticated_client):
        venue = offerers_factories.VenueFactory(pricing_point="self")
        bank_account = finance_factories.BankAccountFactory(offerer=venue.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=bank_account)
        booking = bookings_factories.ReimbursedBookingFactory(stock__offer__venue=venue)
        original_event = finance_factories.UsedBookingFinanceEventFactory(booking=booking)
        original_pricing = api.price_event(original_event)
        original_pricing.status = finance_models.PricingStatus.INVOICED

        original_finance_incident = finance_factories.IndividualBookingFinanceIncidentFactory(
            booking=booking,
            incident__status=finance_models.IncidentStatus.INVOICED,
            incident__venue=venue,
            incident__forceDebitNote=True,
        ).incident
        events_to_price = []
        events_to_price.extend(
            api._create_finance_events_from_incident(
                original_finance_incident.booking_finance_incidents[0],
                incident_validation_date=date_utils.get_naive_utc_now(),
            )
        )
        booking = bookings_factories.UsedBookingFactory(stock__offer__venue=venue, amount=20)
        events_to_price.append(
            finance_factories.FinanceEventFactory(
                venue=venue, booking=booking, status=finance_models.FinanceEventStatus.READY
            )
        )

        for event in events_to_price:
            api.price_event(event)

        cashflow_batch = api.generate_cashflows_and_payment_files(date_utils.get_naive_utc_now())
        generated_cashflow = cashflow_batch.cashflows[0]
        generated_cashflow.status = finance_models.CashflowStatus.ACCEPTED

        response = self.post_to_endpoint(
            authenticated_client,
            finance_incident_id=original_finance_incident.id,
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert (
            "Cette action ne peut être effectuée que sur un incident validé non terminé."
            == html_parser.extract_alert(response.data)
        )
        finance_incident = (
            db.session.query(finance_models.FinanceIncident).filter_by(id=original_finance_incident.id).one()
        )
        assert finance_incident.forceDebitNote == original_finance_incident.forceDebitNote
