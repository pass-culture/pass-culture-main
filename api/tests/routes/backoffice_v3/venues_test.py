from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from unittest import mock

from flask import url_for
import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.educational import factories as educational_factories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.history import models as history_models
import pcapi.core.history.factories as history_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.models import db
from pcapi.routes.backoffice_v3 import venues
from pcapi.routes.backoffice_v3.filters import format_dms_status

from .helpers import button as button_helpers
from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


@pytest.fixture(scope="function", name="venue")
def venue_fixture(offerer) -> offerers_models.Venue:
    venue = offerers_factories.VenueFactory(venueLabel=offerers_factories.VenueLabelFactory(label="Lieu test"))
    offerers_factories.VenueReimbursementPointLinkFactory(venue=venue)
    finance_factories.BankInformationFactory(
        venue=venue,
        status=finance_models.BankInformationStatus.ACCEPTED,
    )
    return venue


class GetVenueTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.venue.get"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    @override_features(WIP_ENABLE_NEW_ONBOARDING=True)
    def test_get_venue(self, authenticated_client, venue):
        venue.publicName = "Le grand Rantanplan 1"

        url = url_for(self.endpoint, venue_id=venue.id)

        # if venue is not removed from the current session, any get
        # query won't be executed because of this specific testing
        # environment. this would tamper the real database queries
        # count.
        db.session.expire(venue)

        # get session (1 query)
        # get user with profile and permissions (1 query)
        # get venue (1 query)
        # check WIP_ENABLE_NEW_ONBOARDING FF (1 query)
        with assert_num_queries(4):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert venue.name in response_text
        assert f"Nom d'usage : {venue.publicName} " in response_text
        assert f"Venue ID : {venue.id} " in response_text
        assert f"SIRET : {venue.siret} " in response_text
        assert "Région : Île-de-France " in response_text
        assert f"Ville : {venue.city} " in response_text
        assert f"Code postal : {venue.postalCode} " in response_text
        assert f"E-mail : {venue.bookingEmail} " in response_text
        assert f"Numéro de téléphone : {venue.contact.phone_number} " in response_text
        assert "Peut créer une offre EAC : Non" in response_text
        assert "Statut dossier DMS Adage :" not in response_text
        assert "ID Adage" not in response_text
        assert f"Site web : {venue.contact.website}" in response_text
        assert "Pas de dossier DMS CB" in response_text
        assert f"Activité principale : {venue.venueTypeCode.value}" in response_text
        assert f"Label : {venue.venueLabel.label} " in response_text
        assert "Type de lieu" not in response_text

        badges = html_parser.extract(response.data, tag="span", class_="badge")
        assert "Lieu" in badges
        assert "Suspendu" not in badges

    @override_features(WIP_ENABLE_NEW_ONBOARDING=False)
    def test_get_venue_ff_off(self, authenticated_client, venue):
        url = url_for(self.endpoint, venue_id=venue.id)

        response = authenticated_client.get(url)

        response_text = html_parser.content_as_text(response.data)
        assert f"Type de lieu : {venue.venueTypeCode.value}" in response_text
        assert "Activité principale" not in response_text

    def test_get_venue_with_adage_id(self, authenticated_client):
        venue = offerers_factories.VenueFactory(adageId="7122022", contact=None)

        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue.id))
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert "Peut créer une offre EAC : Oui" in response_text
        assert "ID Adage : 7122022" in response_text

    def test_get_venue_with_no_contact(self, authenticated_client, venue_with_no_contact):
        # when
        response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_with_no_contact.id))

        # then
        assert response.status_code == 200
        response_text = html_parser.content_as_text(response.data)
        assert f"E-mail : {venue_with_no_contact.bookingEmail}" in response_text
        assert "Numéro de téléphone :" not in response_text

    def test_get_venue_with_self_reimbursement_point(
        self, authenticated_client, venue_with_accepted_self_reimbursement_point
    ):
        # when
        response = authenticated_client.get(
            url_for(self.endpoint, venue_id=venue_with_accepted_self_reimbursement_point.id)
        )

        # then
        assert response.status_code == 200
        assert "Relié à un point de remboursement : Oui" in html_parser.content_as_text(response.data)

    def test_get_venue_with_accepted_reimbursement_point(
        self, authenticated_client, venue_with_accepted_reimbursement_point
    ):
        # when
        response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_with_accepted_reimbursement_point.id))

        # then
        assert response.status_code == 200
        assert "Relié à un point de remboursement : Oui" in html_parser.content_as_text(response.data)

    def test_get_venue_with_expired_reimbursement_point(
        self, authenticated_client, venue_with_expired_reimbursement_point
    ):
        # when
        response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_with_expired_reimbursement_point.id))

        # then
        assert response.status_code == 200
        assert "Relié à un point de remboursement : Non" in html_parser.content_as_text(response.data)

    def test_get_venue_dms_stats(self, authenticated_client, venue_with_draft_bank_info):
        with mock.patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_bank_info_status") as bank_info_mock:
            bank_info_mock.return_value = {
                "dossier": {
                    "state": "en_construction",
                    "dateDepot": "2022-09-21T16:30:22+02:00",
                    "dateDerniereModification": "2022-09-22T16:30:22+02:00",
                }
            }
            # when
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_with_draft_bank_info.id))

        # then
        assert response.status_code == 200
        response_text = html_parser.content_as_text(response.data)
        assert "Statut DMS CB : En construction" in response_text
        assert "Date de dépôt du dossier DMS CB : 21/09/2022" in response_text
        assert "Date de validation du dossier DMS CB" not in response_text
        assert "ACCÉDER AU DOSSIER DMS CB" in response_text

    def test_get_venue_dms_stats_for_accepted_file(self, authenticated_client, venue_with_draft_bank_info):
        with mock.patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_bank_info_status") as bank_info_mock:
            bank_info_mock.return_value = {
                "dossier": {
                    "state": "accepte",
                    "dateDepot": "2022-09-21T16:30:22+02:00",
                    "dateDerniereModification": "2022-09-23T16:30:22+02:00",
                }
            }
            # when
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_with_draft_bank_info.id))

        # then
        assert response.status_code == 200
        response_text = html_parser.content_as_text(response.data)
        assert "Statut DMS CB : Accepté" in response_text
        assert "Date de validation du dossier DMS CB : 23/09/2022" in response_text
        assert "Date de dépôt du dossier DMS CB" not in response_text
        assert "ACCÉDER AU DOSSIER DMS CB" in response_text

    def test_get_venue_none_dms_stats_when_no_application_id(self, authenticated_client, venue_with_accepted_bank_info):
        # when
        response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_with_accepted_bank_info.id))

        # then
        assert response.status_code == 200
        assert "Pas de dossier DMS CB" in html_parser.content_as_text(response.data)

    def test_get_venue_with_no_dms_adage_application(self, authenticated_client, random_venue):
        # when
        response = authenticated_client.get(url_for(self.endpoint, venue_id=random_venue.id))

        # then
        assert response.status_code == 200
        content = html_parser.content_as_text(response.data)
        assert "Pas de dossier DMS Adage" in content

    @pytest.mark.parametrize(
        "state,dateKey,label",
        [
            ("en_construction", "depositDate", "Date de dépôt DMS Adage"),
            ("accepte", "lastChangeDate", "Date de validation DMS Adage"),
        ],
    )
    def test_get_venue_with_dms_adage_application(self, authenticated_client, random_venue, state, dateKey, label):
        collectiveDmsApplication = educational_factories.CollectiveDmsApplicationFactory(
            venue=random_venue, state=state
        )

        # when
        response = authenticated_client.get(url_for(self.endpoint, venue_id=random_venue.id))

        # then
        assert response.status_code == 200
        content = html_parser.content_as_text(response.data)
        assert f"Statut du dossier DMS Adage : {format_dms_status(state)}" in content
        assert f"{label} : " + (getattr(collectiveDmsApplication, dateKey)).strftime("%d/%m/%Y") in content


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


class GetVenueStatsTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.venue.get_stats"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # get session (1 query)
    # get user with profile and permissions (1 query)
    # get total revenue (1 query)
    # get venue stats (1 query)
    expected_num_queries = 4

    def test_get_stats(self, authenticated_client, venue):
        booking = bookings_factories.BookingFactory(stock__offer__venue=venue)
        url = url_for(self.endpoint, venue_id=venue.id)

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
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))

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
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))

        # then
        assert response.status_code == 200
        assert "30,00 € de CA" in html_parser.extract_cards_text(response.data)

    def test_venue_total_revenue_collective_bookings_only(
        self, authenticated_client, venue_with_accepted_bank_info, collective_venue_booking
    ):
        # when
        venue_id = venue_with_accepted_bank_info.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))

        # then
        assert response.status_code == 200
        assert "42,00 € de CA" in html_parser.extract_cards_text(response.data)

    def test_venue_total_revenue_no_booking(self, authenticated_client, venue_with_accepted_bank_info):
        # when
        venue_id = venue_with_accepted_bank_info.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))

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
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert "6 offres actives (2 IND / 4 EAC) 8 offres inactives (3 IND / 5 EAC)" in cards_text

    def test_venue_offers_stats_0_if_no_offer(self, authenticated_client, venue_with_accepted_bank_info):
        # when
        venue_id = venue_with_accepted_bank_info.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))

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


class DeleteVenueTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.venue.delete_venue"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.DELETE_PRO_ENTITY

    def test_delete_venue(self, legit_user, authenticated_client):
        venue_to_delete = offerers_factories.VenueFactory()
        venue_to_delete_name = venue_to_delete.name
        venue_to_delete_id = venue_to_delete.id

        response = self.post_to_endpoint(authenticated_client, venue_id=venue_to_delete.id)
        assert response.status_code == 303
        assert offerers_models.Venue.query.filter(offerers_models.Venue.id == venue_to_delete_id).count() == 0

        expected_url = url_for("backoffice_v3_web.search_pro", _external=True)
        assert response.location == expected_url
        response = authenticated_client.get(expected_url)
        assert (
            html_parser.extract_alert(response.data)
            == f"Le lieu {venue_to_delete_name} ({venue_to_delete_id}) a été supprimé"
        )

    def test_cant_delete_venue_with_bookings(self, legit_user, authenticated_client):
        booking = bookings_factories.BookingFactory()
        venue_to_delete = booking.venue
        venue_to_delete_id = venue_to_delete.id

        response = self.post_to_endpoint(authenticated_client, venue_id=venue_to_delete.id)
        assert response.status_code == 303
        assert offerers_models.Venue.query.filter(offerers_models.Venue.id == venue_to_delete_id).count() == 1

        expected_url = url_for("backoffice_v3_web.venue.get", venue_id=venue_to_delete.id, _external=True)
        assert response.location == expected_url
        response = authenticated_client.get(expected_url)
        assert (
            html_parser.extract_alert(response.data)
            == "Impossible d'effacer un lieu pour lequel il existe des réservations"
        )

    def test_cant_delete_venue_when_pricing_point_for_another_venue(self, legit_user, authenticated_client):
        venue_to_delete = offerers_factories.VenueFactory(pricing_point="self")
        offerers_factories.VenueFactory(pricing_point=venue_to_delete, managingOfferer=venue_to_delete.managingOfferer)
        venue_to_delete_id = venue_to_delete.id

        response = self.post_to_endpoint(authenticated_client, venue_id=venue_to_delete.id)
        assert response.status_code == 303
        assert offerers_models.Venue.query.filter(offerers_models.Venue.id == venue_to_delete_id).count() == 1

        expected_url = url_for("backoffice_v3_web.venue.get", venue_id=venue_to_delete.id, _external=True)
        assert response.location == expected_url
        response = authenticated_client.get(expected_url)
        assert (
            html_parser.extract_alert(response.data)
            == "Impossible d'effacer un lieu utilisé comme point de valorisation d'un autre lieu"
        )

    def test_cant_delete_venue_when_reimbursement_point_for_another_venue(self, legit_user, authenticated_client):
        venue_to_delete = offerers_factories.VenueFactory(pricing_point="self")
        offerers_factories.VenueFactory(
            reimbursement_point=venue_to_delete, managingOfferer=venue_to_delete.managingOfferer
        )
        venue_to_delete_id = venue_to_delete.id

        response = self.post_to_endpoint(authenticated_client, venue_id=venue_to_delete.id)
        assert response.status_code == 303
        assert offerers_models.Venue.query.filter(offerers_models.Venue.id == venue_to_delete_id).count() == 1

        expected_url = url_for("backoffice_v3_web.venue.get", venue_id=venue_to_delete.id, _external=True)
        assert response.location == expected_url
        response = authenticated_client.get(expected_url)
        assert (
            html_parser.extract_alert(response.data)
            == "Impossible d'effacer un lieu utilisé comme point de remboursement d'un autre lieu"
        )


class UpdateVenueTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.venue.update_venue"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def _get_current_data(self, venue: offerers_models.Venue) -> dict:
        return {
            "tags": [criteria.id for criteria in venue.criteria],
            "name": venue.name or "",
            "public_name": venue.publicName or "",
            "siret": venue.siret or "",
            "city": venue.city or "",
            "postal_code": venue.postalCode or "",
            "address": venue.address or "",
            "booking_email": venue.bookingEmail or "",
            "phone_number": venue.contact.phone_number or "",
            "longitude": venue.longitude,
            "latitude": venue.latitude,
        }

    def test_update_venue(self, authenticated_client, offerer):
        contact_email = "contact.venue@example.com"
        website = "update.venue@example.com"
        social_medias = {"instagram": "https://instagram.com/update.venue"}
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            contact__email=contact_email,
            contact__website=website,
            contact__social_medias=social_medias,
        )

        data = {
            "name": "IKEA",
            "public_name": "Kanelbulle café",
            "siret": venue.managingOfferer.siren + "98765",
            "city": "Umeå",
            "postal_code": "90325",
            "address": "Skolgatan 31A",
            "booking_email": venue.bookingEmail + ".update",
            "phone_number": "+33102030456",
            "is_permanent": True,
            "latitude": "48.87056",
            "longitude": "2.34767",
        }

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_v3_web.venue.get", venue_id=venue.id, _external=True)

        db.session.refresh(venue)

        assert venue.name == data["name"]
        assert venue.publicName == data["public_name"]
        assert venue.siret == data["siret"]
        assert venue.city == data["city"]
        assert venue.postalCode == data["postal_code"]
        assert venue.address == data["address"]
        assert venue.bookingEmail == data["booking_email"]
        assert venue.contact.phone_number == data["phone_number"]
        assert venue.isPermanent == data["is_permanent"]
        assert venue.latitude == Decimal("48.87056")
        assert venue.longitude == Decimal("2.34767")

        # should not have been updated or erased
        assert venue.contact.email == contact_email
        assert venue.contact.website == website
        assert venue.contact.social_medias == social_medias

        assert len(venue.action_history) == 1

        update_snapshot = venue.action_history[0].extraData["modified_info"]

        assert update_snapshot["city"]["new_info"] == data["city"]
        assert update_snapshot["address"]["new_info"] == data["address"]
        assert update_snapshot["bookingEmail"]["new_info"] == data["booking_email"]

    def test_update_venue_contact_only(self, authenticated_client, offerer):
        contact_email = "contact.venue@example.com"
        website = "update.venue@example.com"
        social_medias = {"instagram": "https://instagram.com/update.venue"}
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            contact__email=contact_email,
            contact__website=website,
            contact__social_medias=social_medias,
        )

        data = self._get_current_data(venue)
        data["phone_number"] = "+33102030456"

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_v3_web.venue.get", venue_id=venue.id, _external=True)

        db.session.refresh(venue)

        assert venue.contact.phone_number == data["phone_number"]

        # should not have been updated or erased
        assert venue.contact.email == contact_email
        assert venue.contact.website == website
        assert venue.contact.social_medias == social_medias

        assert len(venue.action_history) == 1

        update_snapshot = venue.action_history[0].extraData["modified_info"]
        assert set(update_snapshot.keys()) == {"contact.phone_number"}
        assert update_snapshot["contact.phone_number"]["new_info"] == data["phone_number"]

    def test_update_venue_empty_phone_number(self, authenticated_client):
        venue = offerers_factories.VenueFactory()

        data = self._get_current_data(venue)
        data["phone_number"] = ""

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303
        db.session.refresh(venue)
        assert venue.contact.phone_number is None

    def test_update_venue_with_same_data(self, authenticated_client):
        venue = offerers_factories.VenueFactory()

        data = self._get_current_data(venue)

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)
        assert response.status_code == 303
        assert response.location == url_for("backoffice_v3_web.venue.get", venue_id=venue.id, _external=True)

        db.session.refresh(venue)

        assert len(venue.action_history) == 0

    def test_update_virtual_venue(self, authenticated_client, offerer):
        venue = offerers_factories.VirtualVenueFactory(managingOfferer=offerer)

        data = {
            "booking_email": venue.bookingEmail + ".update",
            "phone_number": "+33102030456",
        }

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_v3_web.venue.get", venue_id=venue.id, _external=True)

        db.session.refresh(venue)

        assert venue.bookingEmail == data["booking_email"]
        assert venue.contact.phone_number == data["phone_number"]

    def test_update_with_missing_data(self, authenticated_client, venue):
        data = {"email": venue.contact.email + ".update"}

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 400
        assert "Les données envoyées comportent des erreurs" in response.data.decode("utf-8")

    def test_update_venue_tags(self, legit_user, authenticated_client):
        venue = offerers_factories.VenueFactory()
        tag1 = criteria_factories.CriterionFactory(name="Premier")
        tag2 = criteria_factories.CriterionFactory(name="Deuxième")
        tag3 = criteria_factories.CriterionFactory(name="Troisième")
        criteria_factories.VenueCriterionFactory(venueId=venue.id, criterionId=tag1.id)
        criteria_factories.VenueCriterionFactory(venueId=venue.id, criterionId=tag2.id)

        data = self._get_current_data(venue)
        data["tags"] = [tag2.id, tag3.id]

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)
        assert response.status_code == 303
        assert response.location == url_for("backoffice_v3_web.venue.get", venue_id=venue.id, _external=True)

        db.session.refresh(venue)

        assert set(venue.criteria) == {tag2, tag3}
        assert len(venue.action_history) == 1
        assert venue.action_history[0].actionType == history_models.ActionType.INFO_MODIFIED
        assert venue.action_history[0].authorUser == legit_user
        assert venue.action_history[0].extraData == {
            "modified_info": {"criteria": {"old_info": ["Premier", "Deuxième"], "new_info": ["Deuxième", "Troisième"]}}
        }

    def test_update_venue_without_siret(self, authenticated_client, offerer):
        offerers_factories.VenueFactory(siret="", comment="other venue without siret")
        venue = offerers_factories.VenueWithoutSiretFactory()

        data = self._get_current_data(venue)
        data["phone_number"] = "+33203040506"

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303
        db.session.refresh(venue)
        assert venue.siret is None
        assert venue.contact.phone_number == "+33203040506"

    def test_update_venue_create_siret(self, authenticated_client, offerer):
        venue = offerers_factories.VenueWithoutSiretFactory()

        data = self._get_current_data(venue)
        data["siret"] = f"{venue.managingOfferer.siren}12345"

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 400
        db.session.refresh(venue)
        assert venue.siret is None
        assert "Vous ne pouvez pas créer le SIRET d'un lieu. Contactez le support pro." in html_parser.extract_alert(
            response.data
        )

    @pytest.mark.parametrize("siret", ["", " "])
    def test_update_venue_remove_siret(self, authenticated_client, offerer, siret):
        venue = offerers_factories.VenueFactory()

        data = self._get_current_data(venue)
        data["siret"] = siret

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 400
        db.session.refresh(venue)
        assert venue.siret
        assert "Vous ne pouvez pas retirer le SIRET d'un lieu. Contactez le support pro." in html_parser.extract_alert(
            response.data
        )

    @pytest.mark.parametrize("siret", ["1234567891234", "123456789123456", "123456789ABCDE", "11122233300001"])
    def test_update_venue_invalid_siret(self, authenticated_client, offerer, siret):
        venue = offerers_factories.VenueFactory(siret="12345678900001", managingOfferer__siren="123456789")

        data = self._get_current_data(venue)
        data["siret"] = " "

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 400


class GetVenueDetailsTest(GetEndpointHelper):
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

        url = url_for(self.endpoint, venue_id=venue.id)

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

        url = url_for(self.endpoint, venue_id=venue.id)

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
