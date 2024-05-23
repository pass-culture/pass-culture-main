import datetime
from unittest import mock

from flask import url_for
import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.utils.human_ids import humanize

from .helpers import button as button_helpers
from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class GetBankAccountTest(GetEndpointHelper):
    endpoint = "backoffice_web.bank_account.get"
    endpoint_kwargs = {"bank_account_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # get session (1 query)
    # get user with profile and permissions (1 query)
    # get bank_account (1 query)
    expected_num_queries = 3

    @mock.patch("pcapi.routes.backoffice.bank_account.blueprint.dms_api.get_dms_stats", lambda x: None)
    def test_get_bank_account(self, authenticated_client):
        bank_account = finance_factories.BankAccountFactory()

        url = url_for(self.endpoint, bank_account_id=bank_account.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert bank_account.label in response_text
        assert f"Bank Account ID : {bank_account.id} " in response_text
        assert f"Humanized ID : {humanize(bank_account.id)} " in response_text
        assert f"IBAN : {bank_account.iban} " in response_text
        assert f"BIC : {bank_account.bic} " in response_text
        assert "Statut dossier DMS ADAGE :" not in response_text
        assert "Pas de dossier DMS CB" in response_text
        assert "État du compte bancaire : Accepté" in response_text
        assert "ACCÉDER AU DOSSIER DMS CB" not in response_text

    def test_get_venue_dms_stats(self, authenticated_client):
        with mock.patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_bank_info_status") as bank_info_mock:
            bank_info_mock.return_value = {
                "dossier": {
                    "state": "en_construction",
                    "dateDepot": "2022-09-21T16:30:22+02:00",
                    "dateDerniereModification": "2022-09-23T16:30:22+02:00",
                    "datePassageEnConstruction": "2022-09-22T16:30:22+02:00",
                }
            }
            bank_account = finance_factories.BankAccountFactory()

            url = url_for(self.endpoint, bank_account_id=bank_account.id)

            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(url)
                assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert "Statut DMS CB : En construction" in response_text
        assert "Date de dépôt du dossier DMS CB : 21/09/2022" in response_text
        assert "Date de validation du dossier DMS CB" not in response_text
        assert "ACCÉDER AU DOSSIER DMS CB" in response_text

    def test_get_venue_dms_stats_for_accepted_file(self, authenticated_client):
        with mock.patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_bank_info_status") as bank_info_mock:
            bank_info_mock.return_value = {
                "dossier": {
                    "state": "accepte",
                    "dateDepot": "2022-09-21T16:30:22+02:00",
                    "dateDerniereModification": "2022-09-25T16:30:22+02:00",
                    "datePassageEnConstruction": "2022-09-22T16:30:22+02:00",
                    "datePassageEnInstruction": "2022-09-23T16:30:22+02:00",
                    "dateTraitement": "2022-09-24T16:30:22+02:00",
                }
            }
            bank_account = finance_factories.BankAccountFactory()

            url = url_for(self.endpoint, bank_account_id=bank_account.id)

            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(url)
                assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert "Statut DMS CB : Accepté" in response_text
        assert "Date de validation du dossier DMS CB : 24/09/2022" in response_text
        assert "Date de dépôt du dossier DMS CB" not in response_text
        assert "ACCÉDER AU DOSSIER DMS CB" in response_text


class GetBankAccountVenuesTest(GetEndpointHelper):
    endpoint = "backoffice_web.bank_account.get_linked_venues"
    endpoint_kwargs = {"bank_account_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # - session + authenticated user (2 queries)
    # - venues with joined data (1 query)
    expected_num_queries = 3

    def test_get_linked_venues(self, authenticated_client):
        bank_account = finance_factories.BankAccountFactory()

        offerer = offerers_factories.OffererFactory()
        venue_1 = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue_2 = offerers_factories.VenueFactory(managingOfferer=offerer)

        link_venue1_date = datetime.datetime(2022, 10, 3, 13, 1)
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue_1, bankAccount=bank_account, timespan=(link_venue1_date,)
        )
        link_venue2_date = datetime.datetime(2023, 8, 4, 14, 2)
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue_2, bankAccount=bank_account, timespan=(link_venue2_date,)
        )

        # Don't interfere
        other_offerer = offerers_factories.OffererFactory()
        offerers_factories.VenueFactory(managingOfferer=other_offerer)

        url = url_for(self.endpoint, bank_account_id=bank_account.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2

        # Sort before checking rows data to avoid flaky test
        rows = sorted(rows, key=lambda row: int(row["ID"]))

        assert rows[0]["ID"] == str(venue_1.id)
        assert rows[0]["Nom"] == venue_1.name
        assert rows[0]["Date de rattachement"].startswith(link_venue1_date.strftime("%d/%m/%Y à "))

        assert rows[1]["ID"] == str(venue_2.id)
        assert rows[1]["Nom"] == venue_2.name
        assert rows[1]["Date de rattachement"].startswith(link_venue2_date.strftime("%d/%m/%Y à "))


class GetBankAccountHistoryTest(GetEndpointHelper):
    endpoint = "backoffice_web.bank_account.get_history"
    endpoint_kwargs = {"bank_account_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # - session + authenticated user (2 queries)
    # - full history with joined data (1 query)
    expected_num_queries = 3

    def test_no_action(self, authenticated_client):
        bank_account = finance_factories.BankAccountFactory()

        url = url_for(self.endpoint, bank_account_id=bank_account.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert html_parser.count_table_rows(response.data) == 0

    def test_get_history(self, authenticated_client, legit_user):
        venue = offerers_factories.VenueFactory()
        bank_account = finance_factories.BankAccountFactory(offerer=venue.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue, bankAccount=bank_account, timespan=(datetime.datetime.utcnow(),)
        )

        action = history_factories.ActionHistoryFactory(
            bankAccount=bank_account,
            venue=venue,
            actionType=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
            authorUser=legit_user,
            user=legit_user,
        )

        url = url_for(self.endpoint, bank_account_id=bank_account.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["Type"] == history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED.value
        assert f"Lieu : {venue.common_name}" in rows[0]["Commentaire"]
        assert url_for("backoffice_web.venue.get", venue_id=venue.id) in str(response.data)
        assert rows[0]["Date/Heure"].startswith(action.actionDate.strftime("Le %d/%m/%Y à "))
        assert rows[0]["Auteur"] == action.authorUser.full_name

    def test_get_full_sorted_history(self, authenticated_client, legit_user):
        venue = offerers_factories.VenueFactory()
        bank_account = finance_factories.BankAccountFactory(offerer=venue.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue, bankAccount=bank_account, timespan=(datetime.datetime.utcnow(),)
        )

        link_action = history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 10, 3, 13, 1),
            venue=venue,
            actionType=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
            authorUser=legit_user,
            user=legit_user,
            bankAccount=bank_account,
        )
        unlink_action = history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 10, 4, 14, 2),
            venue=venue,
            actionType=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_DEPRECATED,
            authorUser=legit_user,
            user=legit_user,
            bankAccount=bank_account,
        )

        url = url_for(self.endpoint, bank_account_id=bank_account.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2

        assert rows[0]["Type"] == "Lieu dissocié d'un compte bancaire"
        assert f"Lieu : {venue.common_name}" in rows[0]["Commentaire"]
        assert url_for("backoffice_web.venue.get", venue_id=venue.id) in str(response.data)
        assert rows[0]["Date/Heure"].startswith(unlink_action.actionDate.strftime("Le %d/%m/%Y à "))
        assert rows[0]["Auteur"] == legit_user.full_name

        assert rows[1]["Type"] == "Lieu associé à un compte bancaire"
        assert f"Lieu : {venue.common_name}" in rows[0]["Commentaire"]
        assert url_for("backoffice_web.venue.get", venue_id=venue.id) in str(response.data)
        assert rows[1]["Date/Heure"].startswith(link_action.actionDate.strftime("Le %d/%m/%Y à "))
        assert rows[1]["Auteur"] == legit_user.full_name


class GetBankAccountInvoicesTest(GetEndpointHelper):
    endpoint = "backoffice_web.bank_account.get_invoices"
    endpoint_kwargs = {"bank_account_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # get session (1 query)
    # get user with profile and permissions (1 query)
    # get invoices (1 query)
    expected_num_queries = 3

    def test_bank_account_has_no_invoices_point(self, authenticated_client):
        bank_account = finance_factories.BankAccountFactory()
        bank_account_id = bank_account.id
        finance_factories.InvoiceFactory(bankAccount=finance_factories.BankAccountFactory())

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, bank_account_id=bank_account_id))
            assert response.status_code == 200

        assert "Aucun remboursement à ce jour" in html_parser.content_as_text(response.data)

    def test_bank_account_has_invoices(self, authenticated_client):
        bank_account = finance_factories.BankAccountFactory()
        bank_account_id = bank_account.id
        invoice1 = finance_factories.InvoiceFactory(
            bankAccount=bank_account, date=datetime.datetime(2023, 4, 1), amount=-1000
        )
        invoice2 = finance_factories.InvoiceFactory(
            bankAccount=bank_account, date=datetime.datetime(2023, 5, 1), amount=-1250
        )
        finance_factories.CashflowFactory(
            invoices=[invoice1, invoice2],
            amount=-2250,
            batch=finance_factories.CashflowBatchFactory(label="TEST123"),
            bankAccount=bank_account,
        )
        finance_factories.InvoiceFactory(bankAccount=finance_factories.BankAccountFactory())

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, bank_account_id=bank_account_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2

        assert rows[0]["Date du justificatif"] == "01/05/2023"
        assert rows[0]["N° du justificatif"] == invoice2.reference
        assert rows[0]["N° de virement"] == "TEST123"
        assert rows[0]["Montant remboursé"] == "12,50 €"

        assert rows[1]["Date du justificatif"] == "01/04/2023"
        assert rows[1]["N° du justificatif"] == invoice1.reference
        assert rows[1]["N° de virement"] == "TEST123"
        assert rows[1]["Montant remboursé"] == "10,00 €"


class DownloadReimbursementDetailsTest(PostEndpointHelper):
    endpoint = "backoffice_web.bank_account.download_reimbursement_details"
    endpoint_kwargs = {"bank_account_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    def test_download_reimbursement_details(self, authenticated_client):
        venue = offerers_factories.VenueFactory(pricing_point="self")
        booking = bookings_factories.UsedBookingFactory(stock__offer__venue=venue)
        bank_account = finance_factories.BankAccountFactory(offerer=venue.managingOfferer)

        # Create partial overpayment on booking
        booking_finance_incident = finance_factories.IndividualBookingFinanceIncidentFactory(
            booking__stock__offer__venue=venue,
            booking__amount=3,
            newTotalAmount=200,
        )
        finance_factories.PricingFactory(
            status=finance_models.PricingStatus.INVOICED, booking=booking_finance_incident.booking
        )
        incident_events = finance_api._create_finance_events_from_incident(
            booking_finance_incident, datetime.datetime.utcnow()
        )
        incident_pricings = []
        for event in incident_events:
            pricing = finance_api.price_event(event)
            pricing.status = finance_models.PricingStatus.INVOICED
            incident_pricings.append(pricing)

        # Create total overpayment on collective booking
        collective_booking_finance_incident = finance_factories.CollectiveBookingFinanceIncidentFactory(
            collectiveBooking__collectiveStock__beginningDatetime=datetime.datetime.utcnow()
            - datetime.timedelta(days=5),
            collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
            collectiveBooking__collectiveStock__price=7,
            newTotalAmount=0,
        )
        finance_factories.CollectivePricingFactory(
            status=finance_models.PricingStatus.INVOICED,
            collectiveBooking=collective_booking_finance_incident.collectiveBooking,
        )
        collective_incident_events = finance_api._create_finance_events_from_incident(
            collective_booking_finance_incident, datetime.datetime.utcnow()
        )
        for event in collective_incident_events:
            pricing = finance_api.price_event(event)
            pricing.status = finance_models.PricingStatus.INVOICED
            incident_pricings.append(pricing)

        pricing = finance_factories.PricingFactory(
            booking=booking,
            status=finance_models.PricingStatus.INVOICED,
        )
        cashflow = finance_factories.CashflowFactory(
            bankAccount=bank_account, pricings=[pricing, *incident_pricings], amount=-210
        )
        invoice = finance_factories.InvoiceFactory(cashflows=[cashflow], bankAccount=bank_account)

        second_booking = bookings_factories.UsedBookingFactory(stock__offer__venue=venue)
        second_pricing = finance_factories.PricingFactory(
            booking=second_booking,
            status=finance_models.PricingStatus.INVOICED,
        )
        second_cashflow = finance_factories.CashflowFactory(
            bankAccount=bank_account, pricings=[second_pricing], amount=-1010
        )
        second_invoice = finance_factories.InvoiceFactory(cashflows=[second_cashflow], bankAccount=bank_account)

        response = self.post_to_endpoint(
            authenticated_client,
            bank_account_id=bank_account.id,
            form={"object_ids": f"{invoice.id}, {second_invoice.id}"},
        )
        assert response.status_code == 200

        expected_length = 1  # headers
        expected_length += 1  # first invoice booking
        expected_length += 1  # first invoice booking price reversal (incident)
        expected_length += 1  # first invoice booking new price (incident)
        expected_length += 1  # first invoice collective booking reversal (incident)
        expected_length += 1  # second_invoice
        expected_length += 1  # empty line

        assert len(response.data.split(b"\n")) == expected_length
        assert str(response.data).count("Incident") == 3


@mock.patch("pcapi.routes.backoffice.bank_account.blueprint.dms_api.get_dms_stats", lambda x: None)
class EditBankAccountButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY
    button_label = "Modifier les informations"

    @property
    def path(self):
        bank_account = finance_factories.BankAccountFactory()
        return url_for("backoffice_web.bank_account.update_bank_account", bank_account_id=bank_account.id)


class UpdateBankAccountTest(PostEndpointHelper):
    endpoint = "backoffice_web.bank_account.update_bank_account"
    endpoint_kwargs = {"bank_account_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_update_bank_account(self, legit_user, authenticated_client):
        bank_account = finance_factories.BankAccountFactory()

        old_label = bank_account.label
        new_label = "Mon compte bancaire"

        response = self.post_to_endpoint(
            authenticated_client, bank_account_id=bank_account.id, form={"label": new_label}
        )
        assert response.status_code == 303

        expected_url = url_for("backoffice_web.bank_account.get", bank_account_id=bank_account.id, _external=True)
        assert response.location == expected_url

        assert bank_account.label == new_label

        assert len(bank_account.action_history) == 1
        assert bank_account.action_history[0].actionType == history_models.ActionType.INFO_MODIFIED
        assert bank_account.action_history[0].authorUser == legit_user
        assert bank_account.action_history[0].extraData["modified_info"] == {
            "label": {"old_info": old_label, "new_info": new_label}
        }

    def test_update_bank_account_unchanged_label(self, legit_user, authenticated_client):
        bank_account = finance_factories.BankAccountFactory()
        old_label = bank_account.label

        response = self.post_to_endpoint(
            authenticated_client, bank_account_id=bank_account.id, form={"label": old_label}
        )
        assert response.status_code == 303

        expected_url = url_for("backoffice_web.bank_account.get", bank_account_id=bank_account.id, _external=True)
        assert response.location == expected_url

        assert bank_account.label == old_label
        assert len(bank_account.action_history) == 0

    @mock.patch("pcapi.routes.backoffice.bank_account.blueprint.dms_api.get_dms_stats", lambda x: None)
    def test_update_bank_account_empty_label(self, legit_user, authenticated_client):
        bank_account = finance_factories.BankAccountFactory(label="Original")

        response = self.post_to_endpoint(authenticated_client, bank_account_id=bank_account.id, form={"label": ""})
        assert response.status_code == 400

        assert bank_account.label == "Original"
        assert len(bank_account.action_history) == 0

    def test_update_bank_account_not_found(self, legit_user, authenticated_client):
        response = self.post_to_endpoint(authenticated_client, bank_account_id=1, form={"label": "Compte"})
        assert response.status_code == 404
