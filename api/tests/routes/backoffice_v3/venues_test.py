from datetime import datetime
from datetime import timedelta
from unittest import mock
from unittest.mock import patch

from flask import g
from flask import url_for
import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
import pcapi.core.history.factories as history_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.routes.backoffice_v3 import venues

from .helpers import button as button_helpers
from .helpers import html_parser
from .helpers import unauthorized as unauthorized_helpers


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


@pytest.fixture(scope="function", name="venue")
def venue_fixture(offerer):  # type: ignore
    venue = offerers_factories.VenueReimbursementPointLinkFactory().venue
    finance_factories.BankInformationFactory(
        venue=venue,
        status=finance_models.BankInformationStatus.ACCEPTED,
    )
    return venue


class GetVenueTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.venue.get"
        endpoint_kwargs = {"venue_id": 1}
        needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_bank_info_status")
    def test_get_venue(self, bank_info_mock, authenticated_client, venue):  # type: ignore
        bank_info_mock.return_value = {
            "dossier": {
                "state": "en_construction",
                "dateDepot": "2022-09-21T16:30:22+02:00",
            }
        }

        url = url_for("backoffice_v3_web.venue.get", venue_id=venue.id)

        # if venue is not removed from the current session, any get
        # query won't be executed because of this specific testing
        # environment. this would tamper the real database queries
        # count.
        db.session.expire(venue)

        # get session (1 query)
        # get user with profile and permissions (1 query)
        # get venue (1 query)
        with assert_num_queries(3):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert venue.name in response_text
        assert f"Venue ID : {venue.id} " in response_text
        assert f"SIRET : {venue.siret} " in response_text
        assert "Région : Île-de-France " in response_text
        assert f"Ville : {venue.city} " in response_text
        assert f"Code postal : {venue.postalCode} " in response_text
        assert f"E-mail : {venue.contact.email} " in response_text
        assert f"Numéro de téléphone : {venue.contact.phone_number} " in response_text
        assert "Éligible EAC : Non" in response_text
        assert "ID Adage" not in response_text
        assert f"Site web : {venue.contact.website}" in response_text
        assert "Pas de dossier DMS" in response_text

        badges = html_parser.extract(response.data, tag="span", class_="badge")
        assert "Lieu" in badges
        assert "Suspendu" not in badges

    def test_get_venue_with_adage_id(self, authenticated_client):
        venue = offerers_factories.VenueFactory(adageId="7122022", contact=None)

        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for("backoffice_v3_web.venue.get", venue_id=venue.id))
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert "Éligible EAC : Oui" in response_text
        assert "ID Adage : 7122022" in response_text

    def test_get_venue_with_no_contact(self, authenticated_client, venue_with_no_contact):
        # when
        response = authenticated_client.get(url_for("backoffice_v3_web.venue.get", venue_id=venue_with_no_contact.id))

        # then
        assert response.status_code == 200
        response_text = html_parser.content_as_text(response.data)
        assert "E-mail :" not in response_text
        assert "Numéro de téléphone :" not in response_text

    def test_get_venue_with_self_reimbursement_point(
        self, authenticated_client, venue_with_accepted_self_reimbursement_point
    ):
        # when
        response = authenticated_client.get(
            url_for("backoffice_v3_web.venue.get", venue_id=venue_with_accepted_self_reimbursement_point.id)
        )

        # then
        assert response.status_code == 200
        assert "Présence de CB : Oui" in html_parser.content_as_text(response.data)

    def test_get_venue_with_accepted_reimbursement_point(
        self, authenticated_client, venue_with_accepted_reimbursement_point
    ):
        # when
        response = authenticated_client.get(
            url_for("backoffice_v3_web.venue.get", venue_id=venue_with_accepted_reimbursement_point.id)
        )

        # then
        assert response.status_code == 200
        assert "Présence de CB : Oui" in html_parser.content_as_text(response.data)

    def test_get_venue_with_expired_reimbursement_point(
        self, authenticated_client, venue_with_expired_reimbursement_point
    ):
        # when
        response = authenticated_client.get(
            url_for("backoffice_v3_web.venue.get", venue_id=venue_with_expired_reimbursement_point.id)
        )

        # then
        assert response.status_code == 200
        assert "Présence de CB : Non" in html_parser.content_as_text(response.data)

    def test_get_venue_dms_stats(self, authenticated_client, venue_with_draft_bank_info):
        with mock.patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_bank_info_status") as bank_info_mock:
            bank_info_mock.return_value = {
                "dossier": {
                    "state": "en_construction",
                    "dateDepot": "2022-09-21T16:30:22+02:00",
                }
            }
            # when
            response = authenticated_client.get(
                url_for("backoffice_v3_web.venue.get", venue_id=venue_with_draft_bank_info.id)
            )

        # then
        assert response.status_code == 200
        response_text = html_parser.content_as_text(response.data)
        assert "Statut DMS : en_construction" in response_text
        assert "Date de dépôt du dossier DMS : 21/09/2022" in response_text
        assert "ACCÉDER AU DOSSIER DMS" in response_text

    def test_get_venue_none_dms_stats_when_no_application_id(self, authenticated_client, venue_with_accepted_bank_info):
        # when
        response = authenticated_client.get(
            url_for("backoffice_v3_web.venue.get", venue_id=venue_with_accepted_bank_info.id)
        )

        # then
        assert response.status_code == 200
        assert "Pas de dossier DMS" in html_parser.content_as_text(response.data)


class GetVenueStatsDataTest:
    def test_get_stats_data(
        self,
        venue_with_accepted_bank_info,
        offerer_active_individual_offers,
        offerer_inactive_individual_offers,
        offerer_active_collective_offers,
        offerer_inactive_collective_offers,
    ):
        venue_id = venue_with_accepted_bank_info.id

        with assert_num_queries(2):
            data = venues.get_stats_data(venue_id)

        stats = data.stats

        assert stats.active.individual == 2
        assert stats.active.collective == 4
        assert stats.inactive.individual == 3
        assert stats.inactive.collective == 5
        assert not stats.lastSync.date
        assert not stats.lastSync.provider

    def test_no_offers(self, venue):
        venue_id = venue.id

        with assert_num_queries(2):
            data = venues.get_stats_data(venue_id)

        stats = data.stats

        assert stats.active.individual == 0
        assert stats.active.collective == 0
        assert stats.inactive.individual == 0
        assert stats.inactive.collective == 0
        assert not stats.lastSync.date
        assert not stats.lastSync.provider


class GetVenueStatsTest:
    # get session (1 query)
    # get user with profile and permissions (1 query)
    # get total revenue (1 query)
    # get venue stats (1 query)
    expected_num_queries = 4

    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.venue.get_stats"
        endpoint_kwargs = {"venue_id": 1}
        needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    def test_get_stats(self, authenticated_client, venue):
        booking = bookings_factories.BookingFactory(stock__offer__venue=venue)
        url = url_for("backoffice_v3_web.venue.get_stats", venue_id=venue.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        # cast to integer to avoid errors due to amount formatting
        assert str(int(booking.amount)) in response.data.decode("utf-8")

    def test_venue_total_revenue(
        self, authenticated_client, venue_with_accepted_bank_info, individual_offerer_bookings, collective_venue_booking
    ):
        # when
        venue_id = venue_with_accepted_bank_info.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for("backoffice_v3_web.venue.get_stats", venue_id=venue_id))

        # then
        assert response.status_code == 200
        assert "72,00 € de CA" in html_parser.extract_cards_text(response.data)

    def test_venue_total_revenue_individual_bookings_only(
        self,
        authenticated_client,
        venue_with_accepted_bank_info,
        individual_offerer_bookings,
    ):
        # when
        venue_id = venue_with_accepted_bank_info.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for("backoffice_v3_web.venue.get_stats", venue_id=venue_id))

        # then
        assert response.status_code == 200
        assert "30,00 € de CA" in html_parser.extract_cards_text(response.data)

    def test_venue_total_revenue_collective_bookings_only(
        self, authenticated_client, venue_with_accepted_bank_info, collective_venue_booking
    ):
        # when
        venue_id = venue_with_accepted_bank_info.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for("backoffice_v3_web.venue.get_stats", venue_id=venue_id))

        # then
        assert response.status_code == 200
        assert "42,00 € de CA" in html_parser.extract_cards_text(response.data)

    def test_venue_total_revenue_no_booking(self, authenticated_client, venue_with_accepted_bank_info):
        # when
        venue_id = venue_with_accepted_bank_info.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for("backoffice_v3_web.venue.get_stats", venue_id=venue_id))

        # then
        assert response.status_code == 200
        assert "0,00 € de CA" in html_parser.extract_cards_text(response.data)

    def test_venue_offers_stats(
        self,
        authenticated_client,
        venue_with_accepted_bank_info,
        offerer_active_individual_offers,
        offerer_inactive_individual_offers,
        offerer_active_collective_offers,
        offerer_inactive_collective_offers,
    ):
        # when
        venue_id = venue_with_accepted_bank_info.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for("backoffice_v3_web.venue.get_stats", venue_id=venue_id))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert "6 offres actives (2 IND / 4 EAC) 8 offres inactives (3 IND / 5 EAC)" in cards_text

    def test_venue_offers_stats_0_if_no_offer(self, authenticated_client, venue_with_accepted_bank_info):
        # when
        venue_id = venue_with_accepted_bank_info.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for("backoffice_v3_web.venue.get_stats", venue_id=venue_id))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert "0 offres actives (0 IND / 0 EAC) 0 offres inactives (0 IND / 0 EAC)" in cards_text


class HasReimbursementPointTest:
    def test_venue_with_reimbursement_point_links(self, venue):
        assert venues.has_reimbursement_point(venue)

    def test_venue_with_no_current_reimbursement_point_links(self):
        venue = offerers_factories.VenueFactory()

        # starts in 10 days, ends in 100
        offerers_factories.VenueReimbursementPointLinkFactory(
            venue=venue,
            reimbursementPoint=venue,
            timespan=[datetime.utcnow() + timedelta(days=10), datetime.utcnow() + timedelta(days=100)],
        )

        # starts in 100 days and has no end
        offerers_factories.VenueReimbursementPointLinkFactory(
            venue=venue,
            reimbursementPoint=venue,
            timespan=[datetime.utcnow() + timedelta(days=100), None],
        )

        # started 100 days ago, ended 10 days ago
        offerers_factories.VenueReimbursementPointLinkFactory(
            venue=venue,
            reimbursementPoint=venue,
            timespan=[datetime.utcnow() - timedelta(days=100), datetime.utcnow() - timedelta(days=10)],
        )

        assert not venues.has_reimbursement_point(venue)

    def test_venue_with_no_reimbursement_point_links(self):
        venue = offerers_factories.VenueFactory()
        assert not venues.has_reimbursement_point(venue)


class UpdateVenueTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        endpoint = "backoffice_v3_web.venue.update_venue"
        endpoint_kwargs = {"venue_id": 1}
        needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_update_venue(self, authenticated_client, offerer):
        website = "update.venue@example.com"
        social_medias = {"instagram": "https://instagram.com/update.venue"}
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer, contact__website=website, contact__social_medias=social_medias
        )

        url = url_for("backoffice_v3_web.venue.update_venue", venue_id=venue.id)
        data = {
            "siret": venue.managingOfferer.siren + "98765",
            "city": "Umeå",
            "postalCode": "90325",
            "address": "Skolgatan 31A",
            "email": venue.contact.email + ".update",
            "phone_number": "+33102030456",
            "isPermanent": True,
        }

        response = send_request(authenticated_client, venue.id, url, data)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_v3_web.venue.get", venue_id=venue.id, _external=True)

        db.session.refresh(venue)

        assert venue.siret == data["siret"]
        assert venue.city == data["city"]
        assert venue.postalCode == data["postalCode"]
        assert venue.address == data["address"]
        assert venue.contact.email == data["email"]
        assert venue.contact.phone_number == data["phone_number"]
        assert venue.isPermanent == data["isPermanent"]

        # should not have been updated or erased
        assert venue.contact.website == website
        assert venue.contact.social_medias == social_medias

        assert len(venue.action_history) == 1

        update_snapshot = venue.action_history[0].extraData["modified_info"]

        assert update_snapshot["city"]["new_info"] == data["city"]
        assert update_snapshot["address"]["new_info"] == data["address"]
        assert update_snapshot["contact.email"]["new_info"] == data["email"]

    def test_update_venue_contact_only(self, authenticated_client, offerer):
        website = "update.venue@example.com"
        social_medias = {"instagram": "https://instagram.com/update.venue"}
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer, contact__website=website, contact__social_medias=social_medias
        )

        url = url_for("backoffice_v3_web.venue.update_venue", venue_id=venue.id)
        data = {
            "siret": venue.siret,
            "city": venue.city,
            "postalCode": venue.postalCode,
            "address": venue.address,
            "email": venue.contact.email + ".update",
            "phone_number": "+33102030456",
            "isPermanent": venue.isPermanent,
        }

        response = send_request(authenticated_client, venue.id, url, data)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_v3_web.venue.get", venue_id=venue.id, _external=True)

        db.session.refresh(venue)

        assert venue.contact.email == data["email"]
        assert venue.contact.phone_number == data["phone_number"]

        # should not have been updated or erased
        assert venue.contact.website == website
        assert venue.contact.social_medias == social_medias

        assert len(venue.action_history) == 1

        update_snapshot = venue.action_history[0].extraData["modified_info"]
        assert update_snapshot["contact.email"]["new_info"] == data["email"]

    def test_update_virtual_venue(self, authenticated_client, offerer):
        venue = offerers_factories.VirtualVenueFactory(managingOfferer=offerer)

        url = url_for("backoffice_v3_web.venue.update_venue", venue_id=venue.id)
        data = {
            "email": venue.contact.email + ".update",
            "phone_number": "+33102030456",
        }

        response = send_request(authenticated_client, venue.id, url, data)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_v3_web.venue.get", venue_id=venue.id, _external=True)

        db.session.refresh(venue)

        assert venue.contact.email == data["email"]
        assert venue.contact.phone_number == data["phone_number"]

    def test_update_with_missing_data(self, authenticated_client, venue):
        url = url_for("backoffice_v3_web.venue.update_venue", venue_id=venue.id)
        data = {"email": venue.contact.email + ".update"}

        response = authenticated_client.post(url, json=data)
        response = send_request(authenticated_client, venue.id, url, data)

        assert response.status_code == 200
        assert "Les données envoyées comportent des erreurs" in response.data.decode("utf-8")


def send_request(authenticated_client, venue_id, url, form_data=None):
    # generate and fetch (inside g) csrf token
    venue_detail_url = url_for("backoffice_v3_web.venue.get", venue_id=venue_id)
    authenticated_client.get(venue_detail_url)

    form_data = form_data if form_data else {}
    form = {"csrf_token": g.get("csrf_token", ""), **form_data}

    return authenticated_client.post(url, form=form)


class GetVenueDetailsTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.venue.get_details"
        endpoint_kwargs = {"venue_id": 1}
        needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    class CommentButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY
        button_label = "Ajouter un commentaire"

        @property
        def path(self):
            venue = offerers_factories.VenueFactory()
            return url_for("backoffice_v3_web.venue.get_details", venue_id=venue.id)

    def test_venue_history(self, authenticated_client, legit_user):
        venue = offerers_factories.VenueFactory()

        comment = "test comment"
        history_factories.ActionHistoryFactory(authorUser=legit_user, venue=venue, comment=comment)

        url = url_for("backoffice_v3_web.venue.get_details", venue_id=venue.id)

        # if venue is not removed from the current session, any get
        # query won't be executed because of this specific testing
        # environment. this would tamper the real database queries
        # count.
        db.session.expire(venue)

        # get session (1 query)
        # get user with profile and permissions (1 query)
        # get venue details (1 query)
        with assert_num_queries(3):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert comment in response.data.decode("utf-8")

    def test_venue_without_history(self, authenticated_client, legit_user):
        venue = offerers_factories.VenueFactory()

        url = url_for("backoffice_v3_web.venue.get_details", venue_id=venue.id)

        # if venue is not removed from the current session, any get
        # query won't be executed because of this specific testing
        # environment. this would tamper the real database queries
        # count.
        db.session.expire(venue)

        # get session (1 query)
        # get user with profile and permissions (1 query)
        # get venue details (1 query)
        with assert_num_queries(3):
            response = authenticated_client.get(url)
            assert response.status_code == 200
