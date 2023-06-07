from datetime import datetime
from datetime import timedelta
from decimal import Decimal
import json
from operator import attrgetter
from unittest import mock
from unittest.mock import patch

from flask import url_for
import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.criteria import models as criteria_models
from pcapi.core.educational import factories as educational_factories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.history import models as history_models
import pcapi.core.history.factories as history_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
from pcapi.core.offerers.models import VenueTypeCode
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.core.users.backoffice import api as backoffice_api
from pcapi.models import db
from pcapi.routes.backoffice_v3 import venues as venues_blueprint
from pcapi.routes.backoffice_v3.filters import format_dms_status

from .helpers import button as button_helpers
from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


@pytest.fixture(scope="function", name="criteria")
def criteria_fixture() -> list[criteria_models.Criterion]:
    return [
        criteria_factories.CriterionFactory(name="Criterion_cinema"),
        criteria_factories.CriterionFactory(name="Criterion_art"),
        criteria_factories.CriterionFactory(name="Criterion_game"),
    ]


@pytest.fixture(scope="function", name="venue")
def venue_fixture(offerer) -> offerers_models.Venue:
    venue = offerers_factories.VenueFactory(
        venueLabel=offerers_factories.VenueLabelFactory(label="Lieu test"), contact__website="www.example.com"
    )
    offerers_factories.VenueReimbursementPointLinkFactory(venue=venue)
    finance_factories.BankInformationFactory(
        venue=venue,
        status=finance_models.BankInformationStatus.ACCEPTED,
    )
    return venue


@pytest.fixture(scope="function", name="venues")
def venues_fixture(criteria) -> list[offerers_models.Venue]:
    return [
        offerers_factories.VenueFactory(
            venueTypeCode=VenueTypeCode.MOVIE,
            venueLabelId=offerers_factories.VenueLabelFactory(label="Cinéma d'art et d'essai").id,
            criteria=criteria[:2],
            postalCode="82000",
            isPermanent=True,
        ),
        offerers_factories.VenueFactory(
            venueTypeCode=VenueTypeCode.GAMES,
            venueLabelId=offerers_factories.VenueLabelFactory(label="Scènes conventionnées").id,
            criteria=criteria[2:],
            postalCode="45000",
            isPermanent=False,
        ),
    ]


class ListVenuesTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.venue.list_venues"
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    # Use assert_num_queries() instead of assert_no_duplicated_queries() which does not detect one extra query caused
    # by a field added in the jinja template.
    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch venue_label for select (1 query)
    # - fetch venues with joinedload including extra data (1 query)
    expected_num_queries = 4

    def test_list_venues_without_filter(self, authenticated_client):
        # when
        response = authenticated_client.get(url_for(self.endpoint))

        # then
        assert response.status_code == 200
        assert html_parser.count_table_rows(response.data) == 0

    def test_list_venues_by_type(self, authenticated_client, venues):
        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, type=VenueTypeCode.MOVIE.name))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert int(rows[0]["ID"]) == venues[0].id
        assert rows[0]["Nom"] == venues[0].name
        assert rows[0]["Structure"] == venues[0].managingOfferer.name
        assert rows[0]["Lieu permanent"] == "Lieu permanent"
        assert rows[0]["Label"] == venues[0].venueLabel.label
        assert sorted(rows[0]["Tags"].split()) == sorted("Criterion_cinema Criterion_art".split())
        assert rows[0]["Date de création"] == venues[0].dateCreated.strftime("%d/%m/%Y")

    def test_list_venues_by_label(self, authenticated_client, venues):
        # when
        venue_label_id = venues[0].venueLabelId
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_label=venue_label_id))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert int(rows[0]["ID"]) == venues[0].id

    def test_list_venues_by_tags(self, authenticated_client, venues):
        # when
        expected_num_queries = (
            self.expected_num_queries + 1
        )  # 1 more request is necessary to prefill form choices with selected tag(s)
        criteria_id = venues[0].criteria[0].id
        with assert_num_queries(expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, criteria=criteria_id))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert int(rows[0]["ID"]) == venues[0].id

    def test_list_venues_by_regions(self, authenticated_client, venues):
        # when
        venue = offerers_factories.VenueFactory(postalCode="82000")
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, regions="Occitanie", order="asc"))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert int(rows[0]["ID"]) == venues[0].id
        assert int(rows[1]["ID"]) == venue.id

    def test_list_venues_by_department(self, authenticated_client, venues):
        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, department="82"))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert int(rows[0]["ID"]) == venues[0].id

    @pytest.mark.parametrize(
        "row_key,order",
        [
            ("Date de création", None),
            ("Date de création", ""),
            ("Date de création", "asc"),
            ("Date de création", "desc"),
        ],
    )
    def test_list_venues_by_order(self, authenticated_client, row_key, order):
        venues = [
            offerers_factories.VenueFactory(venueTypeCode=VenueTypeCode.MOVIE),
            offerers_factories.VenueFactory(venueTypeCode=VenueTypeCode.MOVIE),
        ]
        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, order=order, type=VenueTypeCode.MOVIE.name))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        # Without sort, table is ordered by dateCreated desc
        venues.sort(key=attrgetter("id"), reverse=(order == "desc"))
        assert [row[row_key] for row in rows] == [venue.dateCreated.strftime("%d/%m/%Y") for venue in venues]


class GetVenueTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.venue.get"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # get session (1 query)
    # get user with profile and permissions (1 query)
    # get venue (1 query)
    # check WIP_ENABLE_NEW_ONBOARDING FF (1 query)
    expected_num_queries = 4

    @override_features(WIP_ENABLE_NEW_ONBOARDING=True)
    def test_get_venue(self, authenticated_client, venue):
        venue.publicName = "Le grand Rantanplan 1"

        url = url_for(self.endpoint, venue_id=venue.id)

        # if venue is not removed from the current session, any get
        # query won't be executed because of this specific testing
        # environment. this would tamper the real database queries
        # count.
        db.session.expire(venue)

        with assert_num_queries(self.expected_num_queries):
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
        assert "Site web : https://www.example.com" in response_text
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

    def test_get_virtual_venue(self, authenticated_client):
        venue = offerers_factories.VirtualVenueFactory()

        url = url_for(self.endpoint, venue_id=venue.id)

        # if venue is not removed from the current session, any get
        # query won't be executed because of this specific testing
        # environment. this would tamper the real database queries
        # count.
        db.session.expire(venue)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert venue.name in response_text
        assert "Nom d'usage :" not in response_text
        assert f"Venue ID : {venue.id} " in response_text
        assert f"E-mail : {venue.bookingEmail} " in response_text
        assert f"Numéro de téléphone : {venue.contact.phone_number} " in response_text
        assert "Peut créer une offre EAC : Non" in response_text
        assert "Statut dossier DMS Adage :" not in response_text
        assert "ID Adage" not in response_text
        assert "Site web : https://my.website.com" in response_text
        assert "Pas de dossier DMS CB" in response_text

        badges = html_parser.extract(response.data, tag="span", class_="badge")
        assert "Lieu" in badges
        assert "Suspendu" not in badges


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
            data = venues_blueprint.get_stats_data(venue_id)

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
            data = venues_blueprint.get_stats_data(venue_id)

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
        offerer_active_collective_offer_templates,
        offerer_inactive_collective_offer_templates,
    ):
        # when
        venue_id = venue_with_accepted_bank_info.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert "7 offres actives (2 IND / 5 EAC) 10 offres inactives (3 IND / 7 EAC)" in cards_text

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
        assert venues_blueprint.has_reimbursement_point(venue)

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

        assert not venues_blueprint.has_reimbursement_point(venue)

    def test_venue_with_no_reimbursement_point_links(self):
        venue = offerers_factories.VenueFactory()
        assert not venues_blueprint.has_reimbursement_point(venue)


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

    def test_update_venue_create_siret(self, authenticated_client, legit_user, offerer):
        venue = offerers_factories.VenueWithoutSiretFactory()

        data = self._get_current_data(venue)
        data["siret"] = f"{venue.managingOfferer.siren}12345"

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303
        db.session.refresh(venue)
        assert venue.siret == data["siret"]
        assert venue.comment is None
        assert venue.current_pricing_point_id == venue.id
        assert len(venue.action_history) == 1
        assert venue.action_history[0].actionType == history_models.ActionType.INFO_MODIFIED
        assert venue.action_history[0].authorUser == legit_user
        assert venue.action_history[0].extraData == {
            "modified_info": {
                "siret": {"old_info": "None", "new_info": data["siret"]},
                "comment": {"old_info": "No SIRET", "new_info": "None"},
            }
        }

    def test_update_venue_create_siret_without_permission(self, client, roles_with_permissions, offerer):
        bo_user = users_factories.AdminFactory()
        backoffice_api.upsert_roles(bo_user, [perm_models.Roles.SUPPORT_PRO])

        venue = offerers_factories.VenueWithoutSiretFactory()

        data = self._get_current_data(venue)
        data["siret"] = f"{venue.managingOfferer.siren}12345"

        response = self.post_to_endpoint(client.with_bo_session_auth(bo_user), venue_id=venue.id, form=data)

        assert response.status_code == 400
        assert (
            html_parser.extract_alert(response.data)
            == "Vous ne pouvez pas ajouter le SIRET d'un lieu. Contactez le support pro N2."
        )
        db.session.refresh(venue)
        assert venue.siret is None

    def test_update_venue_create_siret_wrong_siren(self, authenticated_client, offerer):
        venue = offerers_factories.VenueWithoutSiretFactory()

        data = self._get_current_data(venue)
        data["siret"] = "12345678912345"

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 400
        assert "Les données envoyées comportent des erreurs." in html_parser.extract_alert(response.data)
        db.session.refresh(venue)
        assert venue.siret is None

    def test_update_venue_create_siret_which_exists(self, authenticated_client, offerer):
        offerer = offerers_factories.OffererFactory(siren="111222333")
        offerers_factories.VenueFactory(managingOfferer=offerer, siret="11122233344444")
        venue = offerers_factories.VenueWithoutSiretFactory(managingOfferer=offerer)

        data = self._get_current_data(venue)
        data["siret"] = "11122233344444"

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 400
        assert (
            html_parser.extract_alert(response.data)
            == "[siret] Une entrée avec cet identifiant existe déjà dans notre base de données"
        )
        db.session.refresh(venue)
        assert venue.siret is None

    def test_update_venue_create_siret_when_pricing_point_exists(self, authenticated_client, offerer):
        venue = offerers_factories.VenueWithoutSiretFactory()
        offerers_factories.VenuePricingPointLinkFactory(
            venue=venue,
            pricingPoint=offerers_factories.VenueFactory(),
            timespan=[datetime.utcnow() - timedelta(days=60), None],
        )

        data = self._get_current_data(venue)
        data["siret"] = f"{venue.managingOfferer.siren}12345"

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 400
        assert "Ce lieu a déjà un point de valorisation" in html_parser.extract_alert(response.data)
        db.session.refresh(venue)
        assert venue.siret is None

    @patch("pcapi.connectors.sirene.siret_is_active", return_value=False)
    def test_update_venue_create_siret_inactive(self, mock_siret_is_active, authenticated_client, offerer):
        venue = offerers_factories.VenueWithoutSiretFactory()

        data = self._get_current_data(venue)
        data["siret"] = f"{venue.managingOfferer.siren}12345"

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 400
        assert (
            html_parser.extract_alert(response.data)
            == "Ce SIRET n'est plus actif, on ne peut pas l'attribuer à ce lieu"
        )
        db.session.refresh(venue)
        assert venue.siret is None

    def test_update_venue_update_siret_without_permission(self, client, roles_with_permissions, offerer):
        bo_user = users_factories.AdminFactory()
        backoffice_api.upsert_roles(bo_user, [perm_models.Roles.SUPPORT_PRO])

        venue = offerers_factories.VenueFactory(siret="11122233344444", managingOfferer__siren="111222333")

        data = self._get_current_data(venue)
        data["siret"] = "11122233355555"

        response = self.post_to_endpoint(client.with_bo_session_auth(bo_user), venue_id=venue.id, form=data)

        assert response.status_code == 400
        assert (
            html_parser.extract_alert(response.data)
            == "Vous ne pouvez pas modifier le SIRET d'un lieu. Contactez le support pro N2."
        )
        db.session.refresh(venue)
        assert venue.siret == "11122233344444"

    @pytest.mark.parametrize("siret", ["", " "])
    def test_update_venue_remove_siret(self, authenticated_client, offerer, siret):
        venue = offerers_factories.VenueFactory()

        data = self._get_current_data(venue)
        data["siret"] = siret

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 400
        assert html_parser.extract_alert(response.data) == "Vous ne pouvez pas retirer le SIRET d'un lieu."
        db.session.refresh(venue)
        assert venue.siret

    @pytest.mark.parametrize("siret", ["1234567891234", "123456789123456", "123456789ABCDE", "11122233300001"])
    def test_update_venue_invalid_siret(self, authenticated_client, offerer, siret):
        venue = offerers_factories.VenueFactory(siret="12345678900001", managingOfferer__siren="123456789")

        data = self._get_current_data(venue)
        data["siret"] = " "

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 400

    def test_update_venue_siret_disabled(self, client, roles_with_permissions, offerer):
        bo_user = users_factories.AdminFactory()
        backoffice_api.upsert_roles(bo_user, [perm_models.Roles.SUPPORT_PRO])

        venue = offerers_factories.VenueFactory()
        original_siret = venue.siret

        data = self._get_current_data(venue)
        data["public_name"] = "Ma boutique"
        del data["siret"]

        response = self.post_to_endpoint(client.with_bo_session_auth(bo_user), venue_id=venue.id, form=data)

        assert response.status_code == 303
        db.session.refresh(venue)
        assert venue.publicName == "Ma boutique"
        assert venue.siret == original_siret


class GetVenueHistoryTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.venue.get_history"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    class CommentButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY
        button_label = "Ajouter un commentaire"

        @property
        def path(self):
            venue = offerers_factories.VenueFactory()
            return url_for("backoffice_v3_web.venue.get_history", venue_id=venue.id)

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


class GetVenueInvoicesTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.venue.get_invoices"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # get session (1 query)
    # get user with profile and permissions (1 query)
    # get venue reimbursement point (1 query)
    # get invoices (1 query)
    expected_num_queries = 4

    def test_venue_has_no_reimbursement_point(self, authenticated_client):
        venue = offerers_factories.VenueFactory(reimbursement_point=None)
        venue_id = venue.id
        finance_factories.InvoiceFactory(reimbursementPoint=offerers_factories.VenueFactory(reimbursement_point="self"))

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        assert "Aucun remboursement à ce jour" in html_parser.content_as_text(response.data)

    def test_venue_has_different_reimbursement_point(self, authenticated_client):
        venue = offerers_factories.VenueFactory(reimbursement_point=offerers_factories.VenueFactory(name="PDR"))
        venue_id = venue.id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        assert "Le point de remboursement du lieu est actuellement : PDR" in html_parser.content_as_text(response.data)

    def test_venue_has_invoices(self, authenticated_client):
        venue = offerers_factories.VenueFactory(reimbursement_point="self")
        venue_id = venue.id
        invoice1 = finance_factories.InvoiceFactory(reimbursementPoint=venue, date=datetime(2023, 4, 1), amount=-1000)
        invoice2 = finance_factories.InvoiceFactory(reimbursementPoint=venue, date=datetime(2023, 5, 1), amount=-1250)
        finance_factories.CashflowFactory(
            invoices=[invoice1, invoice2],
            reimbursementPoint=venue,
            bankAccount=finance_factories.BankInformationFactory(venue=venue),
            amount=-2250,
            batch=finance_factories.CashflowBatchFactory(label="TEST123"),
        )
        finance_factories.InvoiceFactory(reimbursementPoint=offerers_factories.VenueFactory(reimbursement_point="self"))

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
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


class GetBatchEditVenuesFormTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.venue.get_batch_edit_venues_form"
    endpoint_kwargs = {"object_ids": "1,2"}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_get_empty_batch_edit_venues_form(self, legit_user, authenticated_client):
        with assert_num_queries(2):  # session + user
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

    def test_get_edit_batch_venues_form_with_ids(self, legit_user, authenticated_client, criteria):
        venues = [
            offerers_factories.VenueFactory(criteria=criteria[:2]),
            offerers_factories.VenueFactory(criteria=criteria[1:]),
        ]

        form_data = {
            "object_ids": ",".join(str(venue.id) for venue in venues),
        }

        with assert_num_queries(self.fetch_csrf_num_queries + 3):  # session + user + criteria
            response = self.post_to_endpoint(authenticated_client, form=form_data)
            assert response.status_code == 200

        autocomplete_select = html_parser.get_soup(response.data).find(
            "select", attrs={"data-tomselect-autocomplete-url": "/autocomplete/criteria"}
        )
        assert json.loads(autocomplete_select.attrs["data-tomselect-options"]) == [
            {"id": str(criteria[1].id), "text": criteria[1].name}
        ]
        assert json.loads(autocomplete_select.attrs["data-tomselect-items"]) == [str(criteria[1].id)]


class BatchEditVenuesTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.venue.batch_edit_venues"
    endpoint_kwargs = {"object_ids": "1,2"}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_empty_batch_edit_venues(self, legit_user, authenticated_client):
        form_data = {
            "object_ids": "",
            "all_permanent": "",
            "all_not_permanent": "",
        }

        response = self.post_to_endpoint(authenticated_client, form=form_data)
        assert response.status_code == 303

        redirected_response = authenticated_client.get(response.location)
        assert "L'un des identifiants sélectionnés est invalide" in html_parser.extract_alert(redirected_response.data)

    @pytest.mark.parametrize("is_permanent", [True, False])
    def test_batch_edit_venues_two_checkboxes(self, legit_user, authenticated_client, is_permanent):
        venue = offerers_factories.VenueFactory(isPermanent=is_permanent)

        form_data = {
            "object_ids": str(venue.id),
            "criteria": "",
            "all_permanent": "on",
            "all_not_permanent": "on",
        }

        response = self.post_to_endpoint(authenticated_client, form=form_data)
        assert response.status_code == 303

        redirected_response = authenticated_client.get(response.location)
        assert "Impossible de passer tous les lieux en permanents et non permanents" in html_parser.extract_alert(
            redirected_response.data
        )

        assert venue.isPermanent is is_permanent  # unchanged

    @pytest.mark.parametrize("set_permanent", [True, False])
    def test_batch_edit_venues(self, legit_user, authenticated_client, criteria, set_permanent):
        new_criterion = criteria_factories.CriterionFactory()
        venues = [
            offerers_factories.VenueFactory(criteria=criteria[:2], isPermanent=set_permanent),
            offerers_factories.VenueFactory(criteria=criteria[1:], isPermanent=not set_permanent),
        ]

        form_data = {
            "object_ids": ",".join(str(venue.id) for venue in venues),
            "criteria": [criteria[0].id, new_criterion.id],
            "all_permanent": "on" if set_permanent else "",
            "all_not_permanent": "" if set_permanent else "on",
        }

        response = self.post_to_endpoint(authenticated_client, form=form_data)
        assert response.status_code == 303

        assert set(venues[0].criteria) == {criteria[0], new_criterion}  # 1 kept, 1 removed, 1 added
        assert venues[0].isPermanent is set_permanent

        assert set(venues[1].criteria) == {criteria[0], criteria[2], new_criterion}  # 1 kept, 1 added
        assert venues[1].isPermanent is set_permanent
