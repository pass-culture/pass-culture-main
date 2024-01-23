from datetime import datetime
from datetime import timedelta
from decimal import Decimal
import json
from operator import attrgetter
from unittest import mock
from unittest.mock import patch

from flask import url_for
import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.criteria import models as criteria_models
from pcapi.core.educational import factories as educational_factories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers import models as providers_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.core.users.backoffice import api as backoffice_api
from pcapi.models import db
from pcapi.routes.backoffice.filters import format_dms_status
from pcapi.routes.backoffice.forms.search import TypeOptions
from pcapi.routes.backoffice.venues import blueprint as venues_blueprint
from pcapi.utils import urls

from .helpers import button as button_helpers
from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
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


@pytest.fixture(scope="function", name="venue_with_no_siret")
def venue_with_no_siret_fixture(offerer) -> offerers_models.Venue:
    venue = offerers_factories.VenueFactory(
        venueLabel=offerers_factories.VenueLabelFactory(label="Lieu test"),
        contact__website="www.example.com",
        siret=None,
        isVirtual=True,
    )
    offerers_factories.VenuePricingPointLinkFactory(venue=venue)
    return venue


@pytest.fixture(scope="function", name="venues")
def venues_fixture(criteria) -> list[offerers_models.Venue]:
    return [
        offerers_factories.VenueFactory(
            id=42,
            name="Le Gros Rintintin",
            venueTypeCode=offerers_models.VenueTypeCode.MOVIE,
            venueLabelId=offerers_factories.VenueLabelFactory(label="Cinéma d'art et d'essai").id,
            criteria=criteria[:2],
            postalCode="82000",
            isPermanent=True,
        ),
        offerers_factories.VenueFactory(
            id=43,
            venueTypeCode=offerers_models.VenueTypeCode.GAMES,
            venueLabelId=offerers_factories.VenueLabelFactory(label="Scènes conventionnées").id,
            criteria=criteria[2:],
            postalCode="45000",
            isPermanent=False,
        ),
    ]


class ListVenuesTest(GetEndpointHelper):
    endpoint = "backoffice_web.venue.list_venues"
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    # Use assert_num_queries() instead of assert_no_duplicated_queries() which does not detect one extra query caused
    # by a field added in the jinja template.
    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch venue_label for select (1 query)
    # - fetch venues with joinedload including extra data (1 query)
    expected_num_queries = 4

    def test_list_venues_without_filter(self, authenticated_client):
        response = authenticated_client.get(url_for(self.endpoint))

        assert response.status_code == 200
        assert html_parser.count_table_rows(response.data) == 0

    def test_list_venues_by_type(self, authenticated_client, venues):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, type=offerers_models.VenueTypeCode.MOVIE.name))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert int(rows[0]["ID"]) == venues[0].id
        assert rows[0]["Nom"] == venues[0].name
        assert rows[0]["Nom d'usage"] == venues[0].publicName
        assert rows[0]["Structure"] == venues[0].managingOfferer.name
        assert rows[0]["Lieu permanent"] == "Lieu permanent"
        assert rows[0]["Label"] == venues[0].venueLabel.label
        assert sorted(rows[0]["Tags"].split()) == sorted("Criterion_cinema Criterion_art".split())
        assert rows[0]["Date de création"] == venues[0].dateCreated.strftime("%d/%m/%Y")

    def test_list_venues_by_label(self, authenticated_client, venues):
        venue_label_id = venues[0].venueLabelId
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_label=venue_label_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert int(rows[0]["ID"]) == venues[0].id

    def test_list_venues_by_tags(self, authenticated_client, venues):
        expected_num_queries = (
            self.expected_num_queries + 1
        )  # 1 more request is necessary to prefill form choices with selected tag(s)
        criteria_id = venues[0].criteria[0].id
        with assert_num_queries(expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, criteria=criteria_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert int(rows[0]["ID"]) == venues[0].id

    def test_list_venues_by_offerer(self, authenticated_client, venues):
        # non-matching venues added in venues fixture
        offerer = offerers_factories.OffererFactory()
        matching_venues = [
            offerers_factories.VenueFactory(managingOfferer=offerer),
            offerers_factories.VirtualVenueFactory(managingOfferer=offerer),
            offerers_factories.VenueWithoutSiretFactory(managingOfferer=offerer),
        ]

        offerer_id = offerer.id
        # 1 more request is necessary to prefill form choices with selected offerer(s)
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, offerer=offerer_id))

        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == len(matching_venues)
        assert {int(row["ID"]) for row in rows} == {venue.id for venue in matching_venues}
        for row in rows:
            assert row["Structure"] == offerer.name

    def test_list_venues_by_regions(self, authenticated_client, venues):
        venue = offerers_factories.VenueFactory(postalCode="82000")
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, regions="Occitanie", order="asc"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert {int(row["ID"]) for row in rows} == {venues[0].id, venue.id}

    def test_list_venues_by_department(self, authenticated_client, venues):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, department="82"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert int(rows[0]["ID"]) == venues[0].id

    def test_list_venues_by_id(self, authenticated_client, venues):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=42))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert int(rows[0]["ID"]) == venues[0].id

    def test_list_venue_by_multiple_ids(self, authenticated_client, venues):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="42, 43"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert {int(row["ID"]) for row in rows} == {venues[1].id, venues[0].id}

    def test_list_venue_by_name(self, authenticated_client, venues):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="Le Gros Rintintin"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["Nom"] == venues[0].name

    def test_list_venue_by_name_prefill(self, authenticated_client, venues):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="Rintintin"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert {row["Nom"] for row in rows} == {venues[1].name, venues[0].name}

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
            offerers_factories.VenueFactory(venueTypeCode=offerers_models.VenueTypeCode.MOVIE),
            offerers_factories.VenueFactory(venueTypeCode=offerers_models.VenueTypeCode.MOVIE),
        ]
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, order=order, type=offerers_models.VenueTypeCode.MOVIE.name)
            )
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        # Without sort, table is ordered by dateCreated desc
        venues.sort(key=attrgetter("id"), reverse=(order == "desc"))
        assert [row[row_key] for row in rows] == [venue.dateCreated.strftime("%d/%m/%Y") for venue in venues]

    def test_list_venues_by_only_validated_offerer(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        not_validated_offerer = offerers_factories.NotValidatedOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer, postalCode="62000", departementCode="62")
        offerers_factories.VenueFactory(managingOfferer=not_validated_offerer, postalCode="62000", departementCode="62")

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, only_validated_offerers="on", department="62"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(venue.id)
        assert rows[0]["Structure"] == offerer.name


class GetVenueTest(GetEndpointHelper):
    endpoint = "backoffice_web.venue.get"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # get session (1 query)
    # get user with profile and permissions (1 query)
    # get venue (1 query)
    # get feature flag: WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY (1 query)
    expected_num_queries = 4

    def test_keep_search_parameters_on_top(self, authenticated_client, venue):
        url = url_for(self.endpoint, venue_id=venue.id, q=venue.name, departments=["75", "77"])

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert html_parser.extract_input_value(response.data, "q") == venue.name
        selected_type = html_parser.extract_select_options(response.data, "pro_type", selected_only=True)
        assert set(selected_type.keys()) == {TypeOptions.VENUE.name}
        selected_departments = html_parser.extract_select_options(response.data, "departments", selected_only=True)
        assert set(selected_departments.keys()) == {"75", "77"}

    def test_search_have_departements_preference_parameters_on_top(self, authenticated_client, legit_user, venue):
        url = url_for(self.endpoint, venue_id=venue.id)
        legit_user.backoffice_profile.preferences = {"departments": ["04", "05", "06"]}
        db.session.flush()

        response = authenticated_client.get(url)
        assert response.status_code == 200

        assert html_parser.extract_input_value(response.data, "q") == ""
        selected_type = html_parser.extract_select_options(response.data, "pro_type", selected_only=True)
        assert set(selected_type.keys()) == {TypeOptions.VENUE.name}
        selected_departments = html_parser.extract_select_options(response.data, "departments", selected_only=True)
        assert set(selected_departments.keys()) == {"04", "05", "06"}

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
        assert f"Email : {venue.bookingEmail} " in response_text
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

    def test_get_venue_with_adage_id(self, authenticated_client):
        venue_id = offerers_factories.VenueFactory(adageId="7122022", contact=None).id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert "Peut créer une offre EAC : Oui" in response_text
        assert "ID Adage : 7122022" in response_text

    def test_get_venue_with_no_contact(self, authenticated_client, venue_with_no_contact):
        venue_id = venue_with_no_contact.id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert f"Email : {venue_with_no_contact.bookingEmail}" in response_text
        assert "Numéro de téléphone :" not in response_text

    def test_get_venue_with_self_reimbursement_point(
        self, authenticated_client, venue_with_accepted_self_reimbursement_point
    ):
        venue_id = venue_with_accepted_self_reimbursement_point.id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        assert "Relié à un point de remboursement : Oui" in html_parser.content_as_text(response.data)

    def test_get_venue_with_accepted_reimbursement_point(
        self, authenticated_client, venue_with_accepted_reimbursement_point
    ):
        venue_id = venue_with_accepted_reimbursement_point.id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        assert "Relié à un point de remboursement : Oui" in html_parser.content_as_text(response.data)

    def test_get_venue_with_expired_reimbursement_point(
        self, authenticated_client, venue_with_expired_reimbursement_point
    ):
        venue_id = venue_with_expired_reimbursement_point.id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        assert "Relié à un point de remboursement : Non" in html_parser.content_as_text(response.data)

    def test_get_venue_dms_stats(self, authenticated_client, venue_with_draft_bank_info):
        with mock.patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_bank_info_status") as bank_info_mock:
            bank_info_mock.return_value = {
                "dossier": {
                    "state": "en_construction",
                    "dateDepot": "2022-09-21T16:30:22+02:00",
                    "dateDerniereModification": "2022-09-23T16:30:22+02:00",
                    "datePassageEnConstruction": "2022-09-22T16:30:22+02:00",
                }
            }
            venue_id = venue_with_draft_bank_info.id

            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
                assert response.status_code == 200

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
                    "dateDerniereModification": "2022-09-25T16:30:22+02:00",
                    "datePassageEnConstruction": "2022-09-22T16:30:22+02:00",
                    "datePassageEnInstruction": "2022-09-23T16:30:22+02:00",
                    "dateTraitement": "2022-09-24T16:30:22+02:00",
                }
            }
            venue_id = venue_with_draft_bank_info.id

            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
                assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert "Statut DMS CB : Accepté" in response_text
        assert "Date de validation du dossier DMS CB : 24/09/2022" in response_text
        assert "Date de dépôt du dossier DMS CB" not in response_text
        assert "ACCÉDER AU DOSSIER DMS CB" in response_text

    def test_get_venue_none_dms_stats_when_no_application_id(self, authenticated_client, venue_with_accepted_bank_info):
        venue_id = venue_with_accepted_bank_info.id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        assert "Pas de dossier DMS CB" in html_parser.content_as_text(response.data)

    def test_get_venue_with_no_dms_adage_application(self, authenticated_client, random_venue):
        venue_id = random_venue.id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
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
        venue_id = random_venue.id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert f"Statut du dossier DMS Adage : {format_dms_status(state)}" in content
        assert f"{label} : " + (getattr(collectiveDmsApplication, dateKey)).strftime("%d/%m/%Y") in content

    def test_get_venue_with_provider(self, authenticated_client, random_venue):
        venue_provider = providers_factories.AllocineVenueProviderFactory(
            venue=random_venue, lastSyncDate=datetime.utcnow() - timedelta(hours=5)
        )
        venue_id = random_venue.id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert "Provider : Allociné" in content
        assert f"Dernière synchronisation : {venue_provider.lastSyncDate.strftime('%d/%m/%Y à ')}" in content
        assert f"/pro/venue/{venue_id}/delete/{venue_provider.provider.id}".encode() not in response.data

    def test_get_venue_with_provider_not_allocine(self, authenticated_client, random_venue):
        venue_provider = providers_factories.VenueProviderFactory(venue=random_venue)
        venue_id = random_venue.id

        response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
        assert response.status_code == 200
        assert f"/pro/venue/{venue_id}/provider/{venue_provider.provider.id}/delete".encode() in response.data

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
        assert f"Email : {venue.bookingEmail} " in response_text
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

        with assert_num_queries(7):
            stats = venues_blueprint.get_stats_data(venue_id)

        assert stats["active"]["individual"] == 2
        assert stats["active"]["collective"] == 4
        assert stats["inactive"]["individual"] == 5
        assert stats["inactive"]["collective"] == 7

    def test_no_offers(self, venue):
        venue_id = venue.id

        with assert_num_queries(7):
            stats = venues_blueprint.get_stats_data(venue_id)

        assert stats["active"]["individual"] == 0
        assert stats["active"]["collective"] == 0
        assert stats["inactive"]["individual"] == 0
        assert stats["inactive"]["collective"] == 0


class GetVenueStatsTest(GetEndpointHelper):
    endpoint = "backoffice_web.venue.get_stats"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # get session (1 query)
    # get user with profile and permissions (1 query)
    # get venue with reimbursement and pricing points (1 query)
    # get total revenue (1 query)
    # get venue stats (6 query)
    # get feature flag: WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY (1 query)
    expected_num_queries = 11

    def test_get_venue_with_no_reimbursement_point_bank_information(
        self, authenticated_client, venue_with_accepted_bank_info
    ):
        venue_id = venue_with_accepted_bank_info.id
        url = url_for(self.endpoint, venue_id=venue_id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        cards_content = html_parser.extract_cards_text(response.data)

        assert venue_with_accepted_bank_info.name is not None
        assert len(venue_with_accepted_bank_info.reimbursement_point_links) == 0
        assert f"Point de remboursement : {venue_with_accepted_bank_info.common_name} " not in cards_content[2]
        assert f"Siret de valorisation : {venue_with_accepted_bank_info.common_name} " in cards_content[2]

    def test_get_venue_with_no_bank_info_bank_information(self, authenticated_client, venue_with_no_bank_info):
        venue_id = venue_with_no_bank_info.id
        url = url_for(self.endpoint, venue_id=venue_id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        cards_content = html_parser.extract_cards_text(response.data)

        assert len(venue_with_no_bank_info.reimbursement_point_links) == 0
        assert f"Point de remboursement : {venue_with_no_bank_info.common_name}" not in cards_content[2]
        assert f"Siret de valorisation : {venue_with_no_bank_info.common_name}" in cards_content[2]

    def test_get_venue_with_accepted_reimbursement_point_bank_information(
        self, authenticated_client, venue_with_accepted_reimbursement_point
    ):
        venue_id = venue_with_accepted_reimbursement_point.id
        url = url_for(self.endpoint, venue_id=venue_id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        cards_content = html_parser.extract_cards_text(response.data)
        expected_reimbursement_point: offerers_models.Venue = (
            venue_with_accepted_reimbursement_point.reimbursement_point_links[0].reimbursementPoint
        )

        assert f"Point de remboursement : {expected_reimbursement_point.common_name}" in cards_content[2]
        assert f"Siret de valorisation : {venue_with_accepted_reimbursement_point.common_name}" in cards_content[2]
        assert f"BIC : {expected_reimbursement_point.bic}" in cards_content[2]
        assert f"IBAN : {expected_reimbursement_point.iban}" in cards_content[2]

    def test_get_venue_with_expired_reimbursement_point_bank_information(
        self, authenticated_client, venue_with_expired_reimbursement_point
    ):
        venue_id = venue_with_expired_reimbursement_point.id
        url = url_for(self.endpoint, venue_id=venue_id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        cards_content = html_parser.extract_cards_text(response.data)
        expired_reimbursement_point = venue_with_expired_reimbursement_point.reimbursement_point_links[
            0
        ].reimbursementPoint

        assert f"Point de remboursement : {expired_reimbursement_point.common_name}" not in cards_content[2]
        assert f"Siret de valorisation : {venue_with_expired_reimbursement_point.common_name}" in cards_content[2]
        assert f"BIC : {expired_reimbursement_point.bic}" not in cards_content[2]
        assert f"IBAN : {expired_reimbursement_point.iban}" not in cards_content[2]

    def test_get_venue_with_no_siret_bank_information(self, authenticated_client, venue_with_no_siret):
        venue_id = venue_with_no_siret.id
        url = url_for(self.endpoint, venue_id=venue_id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        cards_content = html_parser.extract_cards_text(response.data)
        pricing_point = venue_with_no_siret.pricing_point_links[0].pricingPoint
        assert venue_with_no_siret.siret is None
        assert f"Siret de valorisation : {pricing_point.name}" in cards_content[2]

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_get_venue_with_no_bank_account(self, authenticated_client, venue_with_no_bank_info):
        venue_id = venue_with_no_bank_info.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        cards_content = html_parser.extract_cards_text(response.data)
        assert cards_content[2].endswith("Compte bancaire :")

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_get_venue_with_bank_accounts(self, authenticated_client, venue_with_accepted_reimbursement_point):
        venue_id = venue_with_accepted_reimbursement_point.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        cards_content = html_parser.extract_cards_text(response.data)
        assert (
            f"Compte bancaire : Nouveau compte ({(datetime.utcnow() - timedelta(days=1)).strftime('%d/%m/%Y')})"
            in cards_content[2]
        )

    # Remove test when WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY is removed
    def test_get_venue_without_bank_account_feature_flag(
        self, authenticated_client, venue_with_accepted_reimbursement_point
    ):
        venue_id = venue_with_accepted_reimbursement_point.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        cards_content = html_parser.extract_cards_text(response.data)
        assert "Compte bancaire :" not in cards_content[2]

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
        venue_id = venue_with_accepted_bank_info.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        assert "72,00 € de CA" in html_parser.extract_cards_text(response.data)

    def test_venue_total_revenue_individual_bookings_only(
        self,
        authenticated_client,
        venue_with_accepted_bank_info,
        individual_offerer_bookings,
    ):
        venue_id = venue_with_accepted_bank_info.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        assert "30,00 € de CA" in html_parser.extract_cards_text(response.data)

    def test_venue_total_revenue_collective_bookings_only(
        self, authenticated_client, venue_with_accepted_bank_info, collective_venue_booking
    ):
        venue_id = venue_with_accepted_bank_info.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        assert "42,00 € de CA" in html_parser.extract_cards_text(response.data)

    def test_venue_total_revenue_no_booking(self, authenticated_client, venue_with_accepted_bank_info):
        venue_id = venue_with_accepted_bank_info.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
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
        venue_id = venue_with_accepted_bank_info.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert "7 offres actives ( 2 IND / 5 EAC ) 16 offres inactives ( 5 IND / 11 EAC )" in cards_text

    def test_venue_offers_stats_0_if_no_offer(self, authenticated_client, venue_with_accepted_bank_info):
        venue_id = venue_with_accepted_bank_info.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert "0 offres actives ( 0 IND / 0 EAC ) 0 offres inactives ( 0 IND / 0 EAC )" in cards_text

    def test_get_venue_not_found(self, authenticated_client):
        response = authenticated_client.get(url_for(self.endpoint, venue_id=1))
        assert response.status_code == 404


class HasReimbursementPointTest:
    def test_venue_with_reimbursement_point_links(self, venue):
        assert venue.current_reimbursement_point

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

        assert venue.current_reimbursement_point is None

    def test_venue_with_no_reimbursement_point_links(self):
        venue = offerers_factories.VenueFactory()
        assert venue.current_reimbursement_point is None


class DeleteVenueTest(PostEndpointHelper):
    endpoint = "backoffice_web.venue.delete_venue"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.DELETE_PRO_ENTITY

    def test_delete_venue(self, legit_user, authenticated_client):
        venue_to_delete = offerers_factories.VenueFactory()
        venue_to_delete_name = venue_to_delete.name
        venue_to_delete_id = venue_to_delete.id

        response = self.post_to_endpoint(authenticated_client, venue_id=venue_to_delete.id)
        assert response.status_code == 303
        assert offerers_models.Venue.query.filter(offerers_models.Venue.id == venue_to_delete_id).count() == 0

        expected_url = url_for("backoffice_web.search_pro", _external=True)
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

        expected_url = url_for("backoffice_web.venue.get", venue_id=venue_to_delete.id, _external=True)
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

        expected_url = url_for("backoffice_web.venue.get", venue_id=venue_to_delete.id, _external=True)
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

        expected_url = url_for("backoffice_web.venue.get", venue_id=venue_to_delete.id, _external=True)
        assert response.location == expected_url
        response = authenticated_client.get(expected_url)
        assert (
            html_parser.extract_alert(response.data)
            == "Impossible d'effacer un lieu utilisé comme point de remboursement d'un autre lieu"
        )

    def test_no_script_injection_in_venue_name(self, legit_user, authenticated_client):
        venue_id = offerers_factories.VenueFactory(name="Lieu <script>alert('coucou')</script>").id

        response = self.post_to_endpoint(authenticated_client, venue_id=venue_id)
        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == f"Le lieu Lieu <script>alert('coucou')</script> ({venue_id}) a été supprimé"
        )


class UpdateVenueTest(PostEndpointHelper):
    endpoint = "backoffice_web.venue.update_venue"
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
            "ban_id": venue.banId or "",
            "booking_email": venue.bookingEmail or "",
            "phone_number": venue.contact.phone_number or "",
            "longitude": venue.longitude,
            "latitude": venue.latitude,
            "venue_type_code": venue.venueTypeCode.name,
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
            "latitude": "63.82850",
            "longitude": "20.25473",
            "venue_type_code": offerers_models.VenueTypeCode.CREATIVE_ARTS_STORE.name,
        }

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id, _external=True)

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
        assert venue.latitude == Decimal("63.82850")
        assert venue.longitude == Decimal("20.25473")
        assert venue.venueTypeCode == offerers_models.VenueTypeCode.CREATIVE_ARTS_STORE

        # should not have been updated or erased
        assert venue.contact.email == contact_email
        assert venue.contact.website == website
        assert venue.contact.social_medias == social_medias

        assert len(venue.action_history) == 1

        update_snapshot = venue.action_history[0].extraData["modified_info"]

        assert update_snapshot["city"]["new_info"] == data["city"]
        assert update_snapshot["address"]["new_info"] == data["address"]
        assert update_snapshot["bookingEmail"]["new_info"] == data["booking_email"]
        assert update_snapshot["latitude"]["new_info"] == data["latitude"]
        assert update_snapshot["longitude"]["new_info"] == data["longitude"]
        assert update_snapshot["venueTypeCode"]["new_info"] == data["venue_type_code"]

        assert len(mails_testing.outbox) == 1
        # check that email is sent when venue is set to permanent and has no image
        assert mails_testing.outbox[0]["To"] == venue.bookingEmail
        assert mails_testing.outbox[0]["template"] == TransactionalEmail.VENUE_NEEDS_PICTURE.value.__dict__
        assert mails_testing.outbox[0]["params"]["VENUE_NAME"] == venue.common_name
        assert mails_testing.outbox[0]["params"]["VENUE_FORM_URL"] == urls.build_pc_pro_venue_link(venue)

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
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id, _external=True)

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
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id, _external=True)

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
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id, _external=True)

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
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id, _external=True)

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
                "siret": {"old_info": None, "new_info": data["siret"]},
                "comment": {"old_info": "No SIRET", "new_info": None},
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
        assert html_parser.extract_alert(response.data) == "Un autre lieu existe déjà avec le SIRET 11122233344444"
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

    def test_update_venue_ban_id(self, authenticated_client):
        bo_user = users_factories.AdminFactory()
        backoffice_api.upsert_roles(bo_user, [perm_models.Roles.SUPPORT_PRO])

        venue = offerers_factories.VenueFactory()

        data = self._get_current_data(venue)
        data["is_permanent"] = True
        data["ban_id"] = "15152_0024_00003"

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303

        db.session.refresh(venue)

        assert venue.address == data["address"]
        assert venue.banId == data["ban_id"]
        assert venue.isPermanent == data["is_permanent"]
        assert venue.action_history[0].extraData == {
            "modified_info": {
                "banId": {"new_info": "15152_0024_00003", "old_info": "75102_7560_00001"},
                "isPermanent": {"new_info": True, "old_info": False},
            }
        }


class GetVenueHistoryTest(GetEndpointHelper):
    endpoint = "backoffice_web.venue.get_history"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # get session (1 query)
    # get user with profile and permissions (1 query)
    # get history (1 query)
    expected_num_queries = 3

    class CommentButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY
        button_label = "Ajouter un commentaire"

        @property
        def path(self):
            venue = offerers_factories.VenueFactory()
            return url_for("backoffice_web.venue.get_history", venue_id=venue.id)

    def test_venue_history(self, authenticated_client, legit_user):
        venue = offerers_factories.VenueFactory()

        comment = "test comment"
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.COMMENT,
            actionDate=datetime.utcnow() - timedelta(hours=3),
            authorUser=legit_user,
            venue=venue,
            comment=comment,
        )
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.INFO_MODIFIED,
            actionDate=datetime.utcnow() - timedelta(hours=2),
            authorUser=legit_user,
            venue=venue,
            comment=None,
            extraData={
                "modified_info": {
                    "venueTypeCode": {
                        "new_info": offerers_models.VenueTypeCode.BOOKSTORE.name,
                        "old_info": offerers_models.VenueTypeCode.OTHER.name,
                    },
                    "withdrawalDetails": {"new_info": "Come here!", "old_info": None},
                    "contact.website": {"new_info": None, "old_info": "https://old.website.com"},
                    "visualDisabilityCompliant": {"new_info": True, "old_info": False},
                }
            },
        )

        url = url_for(self.endpoint, venue_id=venue.id)

        # if venue is not removed from the current session, any get
        # query won't be executed because of this specific testing
        # environment. this would tamper the real database queries
        # count.
        db.session.expire(venue)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert comment in response.data.decode("utf-8")

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert rows[0]["Type"] == "Modification des informations"
        assert "Informations modifiées : " in rows[0]["Commentaire"]
        assert "Activité principale : Autre => Librairie " in rows[0]["Commentaire"]
        assert "Site internet de contact : suppression de : https://old.website.com " in rows[0]["Commentaire"]
        assert "Conditions de retrait : ajout de : Come here!" in rows[0]["Commentaire"]
        assert "Accessibilité handicap visuel : Non => Oui" in rows[0]["Commentaire"]
        assert rows[0]["Auteur"] == legit_user.full_name
        assert rows[1]["Type"] == "Commentaire interne"
        assert rows[1]["Commentaire"] == comment
        assert rows[1]["Auteur"] == legit_user.full_name

    def test_venue_without_history(self, authenticated_client, legit_user):
        venue = offerers_factories.VenueFactory()

        url = url_for(self.endpoint, venue_id=venue.id)

        # if venue is not removed from the current session, any get
        # query won't be executed because of this specific testing
        # environment. this would tamper the real database queries
        # count.
        db.session.expire(venue)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert html_parser.count_table_rows(response.data) == 0


class CommentVenueTest(PostEndpointHelper):
    endpoint = "backoffice_web.venue.comment_venue"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_add_comment(self, authenticated_client, legit_user, venue):
        comment = "Juste un commentaire"
        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form={"comment": comment})

        assert response.status_code == 303

        expected_url = url_for("backoffice_web.venue.get", venue_id=venue.id, _external=True)
        assert response.location == expected_url

        db.session.refresh(venue)
        assert len(venue.action_history) == 1
        action = venue.action_history[0]
        assert action.actionType == history_models.ActionType.COMMENT
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId is None
        assert action.offererId is None
        assert action.venueId == venue.id
        assert action.comment == comment

    def test_add_invalid_comment(self, authenticated_client, venue):
        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form={"comment": ""})

        assert response.status_code == 303
        redirected_response = authenticated_client.get(response.headers["location"])
        assert "Les données envoyées comportent des erreurs" in redirected_response.data.decode("utf8")


class GetVenueInvoicesTest(GetEndpointHelper):
    endpoint = "backoffice_web.venue.get_invoices"
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
            bankInformation=finance_factories.BankInformationFactory(venue=venue),
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


class DownloadReimbursementDetailsTest(PostEndpointHelper):
    endpoint = "backoffice_web.venue.download_reimbursement_details"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    def test_download_reimbursement_details(self, authenticated_client):
        booking = bookings_factories.UsedBookingFactory(stock__offer__venue__reimbursement_point="self")
        reimbursement_point = booking.venue
        finance_factories.BankInformationFactory(venue=reimbursement_point)
        pricing = finance_factories.PricingFactory(
            booking=booking,
            status=finance_models.PricingStatus.INVOICED,
        )
        cashflow = finance_factories.CashflowFactory(
            reimbursementPoint=reimbursement_point,
            pricings=[pricing],
        )
        invoice = finance_factories.InvoiceFactory(cashflows=[cashflow])

        second_booking = bookings_factories.UsedBookingFactory(
            stock__offer__venue__reimbursement_point=reimbursement_point
        )
        second_pricing = finance_factories.PricingFactory(
            booking=second_booking,
            status=finance_models.PricingStatus.INVOICED,
        )
        second_cashflow = finance_factories.CashflowFactory(
            reimbursementPoint=reimbursement_point,
            pricings=[second_pricing],
        )
        second_invoice = finance_factories.InvoiceFactory(cashflows=[second_cashflow])

        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=reimbursement_point.id,
            form={"object_ids": f"{invoice.id}, {second_invoice.id}"},
        )
        assert response.status_code == 200

        expected_length = 1  # headers
        expected_length += 1  # invoice
        expected_length += 1  # second_invoice
        expected_length += 1  # empty line
        print(response.data)

        assert len(response.data.split(b"\n")) == expected_length


class GetBatchEditVenuesFormTest(PostEndpointHelper):
    endpoint = "backoffice_web.venue.get_batch_edit_venues_form"
    endpoint_kwargs = {"object_ids": "1,2"}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_get_empty_batch_edit_venues_form(self, legit_user, authenticated_client):
        with assert_num_queries(2):  # session + current user
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

        with assert_num_queries(self.fetch_csrf_num_queries + 3):  # session + current user + criteria
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
    endpoint = "backoffice_web.venue.batch_edit_venues"
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
    @patch("pcapi.core.search.async_index_venue_ids")
    def test_batch_edit_venues(
        self,
        mock_async_index_venue_ids,
        legit_user,
        authenticated_client,
        criteria,
        set_permanent,
    ):
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

        mock_async_index_venue_ids.assert_called_once()

    def test_batch_edit_venues_only_criteria(self, legit_user, authenticated_client, criteria):
        new_criterion = criteria_factories.CriterionFactory()
        venues = [
            offerers_factories.VenueFactory(criteria=[criteria[0]]),
        ]

        form_data = {
            "object_ids": ",".join(str(venue.id) for venue in venues),
            "criteria": [criteria[0].id, new_criterion.id],
            "all_permanent": "",
            "all_not_permanent": "",
        }

        response = self.post_to_endpoint(authenticated_client, form=form_data)
        assert response.status_code == 303

        assert set(venues[0].criteria) == {criteria[0], new_criterion}

    @pytest.mark.parametrize(
        "set_permanent,thumb_count,expected_mail_number",
        [
            (True, 0, 1),
            (False, 0, 0),
            (True, 1, 0),
        ],
    )
    @patch("pcapi.core.search.async_index_venue_ids")
    def test_batch_edit_venues_set_permanent_sends_mail(
        self,
        mock_async_index_venue_ids,
        legit_user,
        authenticated_client,
        criteria,
        set_permanent,
        thumb_count,
        expected_mail_number,
    ):
        venue = offerers_factories.VenueFactory(isPermanent=not set_permanent)
        venue.thumbCount = thumb_count

        form_data = {
            "object_ids": str(venue.id),
            "all_permanent": "on" if set_permanent else "",
            "all_not_permanent": "" if set_permanent else "on",
        }

        response = self.post_to_endpoint(authenticated_client, form=form_data)
        assert response.status_code == 303

        assert venue.isPermanent is set_permanent

        assert len(mails_testing.outbox) == expected_mail_number
        if expected_mail_number > 0:
            # check that email is sent when venue is set to permanent and has no image
            assert mails_testing.outbox[0]["To"] == venue.bookingEmail
            assert mails_testing.outbox[0]["template"] == TransactionalEmail.VENUE_NEEDS_PICTURE.value.__dict__
            assert mails_testing.outbox[0]["params"]["VENUE_NAME"] == venue.common_name
            assert mails_testing.outbox[0]["params"]["VENUE_FORM_URL"] == urls.build_pc_pro_venue_link(venue)

        mock_async_index_venue_ids.assert_called_once()


class GetRemovePricingPointFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.venue.get_remove_pricing_point_form"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT

    def test_get_remove_pricing_point_form(self, authenticated_client, venue_with_no_siret):
        bookings_factories.ReimbursedBookingFactory(stock__price=123.4, stock__offer__venue=venue_with_no_siret)

        response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_with_no_siret.id))

        assert response.status_code == 200
        content = html_parser.content_as_text(response.data)
        assert f"Lieu : {venue_with_no_siret.name}" in content
        assert f"Venue ID : {venue_with_no_siret.id}" in content
        assert "SIRET : Pas de SIRET" in content
        assert "CA de l'année : 123,40 €" in content
        assert f"Point de valorisation : {venue_with_no_siret.current_pricing_point.name}" in content
        assert f"SIRET de valorisation : {venue_with_no_siret.current_pricing_point.siret}" in content
        assert "Point de remboursement : Aucun" in content
        assert "SIRET de remboursement : Aucun" in content

    def test_venue_with_siret(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.VenuePricingPointLinkFactory(
            venue=venue,
            pricingPoint=offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer),
            timespan=[datetime.utcnow() - timedelta(days=7), None],
        )

        response = authenticated_client.get(url_for(self.endpoint, venue_id=venue.id))

        assert response.status_code == 400
        assert (
            html_parser.extract_alert(response.data)
            == "Vous ne pouvez supprimer le point de valorisation d'un lieu avec SIRET"
        )

    def test_venue_with_no_pricing_point(self, authenticated_client):
        venue = offerers_factories.VenueWithoutSiretFactory()

        response = authenticated_client.get(url_for(self.endpoint, venue_id=venue.id))

        assert response.status_code == 400
        assert html_parser.extract_alert(response.data) == "Ce lieu n'a pas de point de valorisation actif"

    def test_venue_with_high_yearly_revenue(self, authenticated_client, venue_with_no_siret):
        rich_beneficiary = users_factories.BeneficiaryGrant18Factory(deposit__amount=25_000)
        bookings_factories.ReimbursedBookingFactory(
            user=rich_beneficiary, stock__price=10800, stock__offer__venue=venue_with_no_siret
        )

        response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_with_no_siret.id))

        assert response.status_code == 400
        assert html_parser.extract_alert(response.data) == "Ce lieu a un chiffre d'affaires de l'année élevé : 10800.00"


class RemovePricingPointTest(PostEndpointHelper):
    endpoint = "backoffice_web.venue.remove_pricing_point"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT

    def test_remove_pricing_point(self, legit_user, authenticated_client, venue_with_no_siret):
        old_pricing_siret = venue_with_no_siret.current_pricing_point.siret

        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue_with_no_siret.id,
            form={
                "override_revenue_check": False,
                "comment": "test",
            },
        )
        assert response.status_code == 303

        assert venue_with_no_siret.current_pricing_point is None
        assert venue_with_no_siret.pricing_point_links[0].timespan.upper <= datetime.utcnow()
        assert len(venue_with_no_siret.reimbursement_point_links) == 0

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId is None
        assert action.offererId == venue_with_no_siret.managingOffererId
        assert action.venueId == venue_with_no_siret.id
        assert action.comment == "test"
        assert action.extraData["modified_info"] == {
            "pricingPointSiret": {"new_info": None, "old_info": old_pricing_siret},
        }

    def test_remove_pricing_point_and_reimbursement_point(self, legit_user, authenticated_client, venue_with_no_siret):
        offerers_factories.VenueReimbursementPointLinkFactory(venue=venue_with_no_siret)
        old_pricing_siret = venue_with_no_siret.current_pricing_point.siret
        old_reimbursement_point_id = venue_with_no_siret.current_reimbursement_point.id

        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue_with_no_siret.id,
            form={
                "override_revenue_check": False,
                "comment": "test",
            },
        )
        assert response.status_code == 303

        assert venue_with_no_siret.current_pricing_point is None
        assert venue_with_no_siret.current_reimbursement_point.id == old_reimbursement_point_id  # unchanged
        assert venue_with_no_siret.pricing_point_links[0].timespan.upper <= datetime.utcnow()

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId is None
        assert action.offererId == venue_with_no_siret.managingOffererId
        assert action.venueId == venue_with_no_siret.id
        assert action.comment == "test"
        assert action.extraData["modified_info"] == {
            "pricingPointSiret": {"new_info": None, "old_info": old_pricing_siret},
        }

    def test_venue_with_siret(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.VenuePricingPointLinkFactory(
            venue=venue,
            pricingPoint=offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer),
            timespan=[datetime.utcnow() - timedelta(days=7), None],
        )

        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue.id,
            form={
                "comment": "test",
                "override_revenue_check": True,
            },
        )

        assert response.status_code == 400
        assert (
            html_parser.extract_alert(response.data)
            == "Vous ne pouvez supprimer le point de valorisation d'un lieu avec SIRET"
        )

    def test_venue_with_no_pricing_point(self, authenticated_client):
        venue = offerers_factories.VenueWithoutSiretFactory()

        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue.id,
            form={
                "comment": "test",
                "override_revenue_check": True,
            },
        )

        assert response.status_code == 400
        assert html_parser.extract_alert(response.data) == "Ce lieu n'a pas de point de valorisation actif"

    def test_venue_with_high_yearly_revenue(self, authenticated_client, venue_with_no_siret):
        rich_beneficiary = users_factories.BeneficiaryGrant18Factory(deposit__amount=25_000)
        bookings_factories.ReimbursedBookingFactory(
            user=rich_beneficiary, stock__price=10800, stock__offer__venue=venue_with_no_siret
        )

        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue_with_no_siret.id,
            form={
                "comment": "test",
                "override_revenue_check": False,
            },
        )

        assert response.status_code == 400
        assert html_parser.extract_alert(response.data) == "Ce lieu a un chiffre d'affaires de l'année élevé : 10800.00"

    def test_override_yearly_revenue(self, authenticated_client, venue_with_no_siret):
        rich_beneficiary = users_factories.BeneficiaryGrant18Factory(deposit__amount=25_000)
        bookings_factories.ReimbursedBookingFactory(
            user=rich_beneficiary, stock__price=10800, stock__offer__venue=venue_with_no_siret
        )

        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue_with_no_siret.id,
            form={
                "comment": "test",
                "override_revenue_check": True,
            },
        )

        assert response.status_code == 303
        assert venue_with_no_siret.current_pricing_point is None
        assert venue_with_no_siret.pricing_point_links[0].timespan.upper <= datetime.utcnow()


class GetRemoveSiretFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.venue.get_remove_siret_form"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.MOVE_SIRET

    def test_get_remove_siret_form(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        other_venues = offerers_factories.VenueFactory.create_batch(2, managingOfferer=offerer)

        response = authenticated_client.get(url_for(self.endpoint, venue_id=venue.id))

        assert response.status_code == 200
        html_parser.assert_no_alert(response.data)

        content = html_parser.content_as_text(response.data)
        assert f"Structure : {offerer.name}" in content
        assert f"Offerer ID : {offerer.id}" in content
        assert f"Lieu : {venue.name}" in content
        assert f"Venue ID : {venue.id}" in content
        assert f"SIRET : {venue.siret}" in content
        assert "CA de l'année : 0,00 €" in content

        assert html_parser.extract_select_options(response.data, "new_pricing_point") == {
            str(other_venue.id): f"{other_venue.name} ({other_venue.siret})" for other_venue in other_venues
        }

    def test_venue_without_siret(self, authenticated_client):
        venue = offerers_factories.VenueWithoutSiretFactory()
        offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)

        response = authenticated_client.get(url_for(self.endpoint, venue_id=venue.id))

        assert response.status_code == 400
        assert html_parser.extract_alert(response.data) == "Ce lieu n'a pas de SIRET"

    def test_no_other_venue_with_siret(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.VenueWithoutSiretFactory(managingOfferer=venue.managingOfferer)

        response = authenticated_client.get(url_for(self.endpoint, venue_id=venue.id))

        assert response.status_code == 400
        assert html_parser.extract_alert(response.data) == "La structure gérant ce lieu n'a pas d'autre lieu avec SIRET"

    def test_venue_with_high_yearly_revenue(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        rich_beneficiary = users_factories.BeneficiaryGrant18Factory(deposit__amount=25_000)
        bookings_factories.ReimbursedBookingFactory(
            user=rich_beneficiary, stock__price=10800, stock__offer__venue=venue
        )

        response = authenticated_client.get(url_for(self.endpoint, venue_id=venue.id))

        assert response.status_code == 200
        html_parser.assert_no_alert(response.data)

        content = html_parser.content_as_text(response.data)
        assert "CA de l'année : 10 800,00 €" in content


class RemoveSiretTest(PostEndpointHelper):
    endpoint = "backoffice_web.venue.remove_siret"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.MOVE_SIRET

    def test_remove_siret(self, legit_user, authenticated_client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.VenuePricingPointLinkFactory(venue=venue, pricingPoint=venue)
        offerers_factories.VenueReimbursementPointLinkFactory(venue=venue, reimbursementPoint=venue)
        other_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        offerers_factories.VenuePricingPointLinkFactory(venue=other_venue, pricingPoint=venue)
        offerers_factories.VenueReimbursementPointLinkFactory(venue=other_venue, reimbursementPoint=venue)
        target_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)

        old_siret = venue.siret

        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue.id,
            form={"override_revenue_check": False, "comment": "test", "new_pricing_point": target_venue.id},
        )
        assert response.status_code == 303

        assert venue.siret is None
        assert venue.comment == "test"
        assert venue.pricing_point_links[0].timespan.upper <= datetime.utcnow()
        assert venue.current_pricing_point == target_venue
        assert venue.reimbursement_point_links[0].timespan.upper is None  # unchanged
        assert venue.current_reimbursement_point == venue

        action = history_models.ActionHistory.query.filter_by(venueId=venue.id).one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.offererId == venue.managingOffererId
        assert action.comment == "test"
        assert action.extraData["modified_info"] == {
            "siret": {"old_info": old_siret, "new_info": None},
            "pricingPointSiret": {"old_info": old_siret, "new_info": target_venue.siret},
        }

        assert other_venue.pricing_point_links[0].timespan.upper <= datetime.utcnow()
        assert other_venue.current_pricing_point is None
        assert other_venue.reimbursement_point_links[0].timespan.upper is None  # unchanged
        assert other_venue.current_reimbursement_point == venue

        other_action = history_models.ActionHistory.query.filter_by(venueId=other_venue.id).one()
        assert other_action.actionType == history_models.ActionType.INFO_MODIFIED
        assert other_action.actionDate is not None
        assert other_action.authorUserId == legit_user.id
        assert other_action.offererId == venue.managingOffererId
        assert other_action.comment == "test"
        assert other_action.extraData["modified_info"] == {
            "pricingPointSiret": {"old_info": old_siret, "new_info": None},
        }

    def test_venue_without_siret(self, authenticated_client):
        venue = offerers_factories.VenueWithoutSiretFactory()
        target_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)

        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue.id,
            form={
                "comment": "test",
                "override_revenue_check": False,
                "new_pricing_point": target_venue.id,
            },
        )

        assert response.status_code == 400
        assert html_parser.extract_alert(response.data) == "Ce lieu n'a pas de SIRET"

    def test_invalid_new_pricing_point(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        target_venue = offerers_factories.VenueWithoutSiretFactory(managingOfferer=venue.managingOfferer)

        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue.id,
            form={
                "comment": "test",
                "override_revenue_check": False,
                "new_pricing_point": target_venue.id,
            },
        )

        assert response.status_code == 400
        assert html_parser.extract_warnings(response.data) == ["Not a valid choice."]

    def test_venue_with_high_yearly_revenue(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        target_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        rich_beneficiary = users_factories.BeneficiaryGrant18Factory(deposit__amount=25_000)
        bookings_factories.ReimbursedBookingFactory(
            user=rich_beneficiary, stock__price=10800, stock__offer__venue=venue
        )

        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue.id,
            form={
                "comment": "test",
                "override_revenue_check": False,
                "new_pricing_point": target_venue.id,
            },
        )

        assert response.status_code == 400
        assert html_parser.extract_alert(response.data) == "Ce lieu a un chiffre d'affaires de l'année élevé : 10800.00"

    def test_override_yearly_revenue(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.VenuePricingPointLinkFactory(venue=venue, pricingPoint=venue)
        target_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        rich_beneficiary = users_factories.BeneficiaryGrant18Factory(deposit__amount=25_000)
        bookings_factories.ReimbursedBookingFactory(
            user=rich_beneficiary, stock__price=10800, stock__offer__venue=venue
        )

        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue.id,
            form={
                "comment": "test",
                "override_revenue_check": True,
                "new_pricing_point": target_venue.id,
            },
        )

        assert response.status_code == 303
        assert venue.siret is None
        assert venue.current_pricing_point == target_venue


class PostDeleteVenueProviderTest(PostEndpointHelper):
    endpoint = "backoffice_web.venue.delete_venue_provider"
    endpoint_kwargs = {"venue_id": 1, "provider_id": 1}
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT

    def test_delete_venue_provider(self, authenticated_client, legit_user):
        venue_provider = providers_factories.VenueProviderFactory(provider__name="Test provider")
        venue_id = venue_provider.venue.id
        provider_id = venue_provider.provider.id

        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue_id,
            provider_id=provider_id,
        )
        assert response.status_code == 303
        assert not providers_models.VenueProvider.query.filter(
            providers_models.VenueProvider.id == venue_provider.id
        ).all()
        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.LINK_VENUE_PROVIDER_DELETED
        assert action.authorUserId == legit_user.id
        assert action.venueId == venue_id
        assert action.extraData["provider_id"] == provider_id
        assert action.extraData["provider_name"] == "Test provider"
        assert response.location == url_for(
            "backoffice_web.venue.get", venue_id=venue_provider.venue.id, _external=True
        )

        response = authenticated_client.get(response.location)
        assert "Le lien entre le lieu et le provider a été effacé." in html_parser.extract_alert(response.data)

    def test_delete_venue_wrong_provider(self, authenticated_client):
        venue_provider = providers_factories.VenueProviderFactory()

        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue_provider.venue.id,
            provider_id=0,
        )
        assert response.status_code == 404
        assert (
            providers_models.VenueProvider.query.filter(providers_models.VenueProvider.id == venue_provider.id).count()
            == 1
        )
        assert history_models.ActionHistory.query.count() == 0

    def test_delete_venue_allocine_provider(self, authenticated_client):
        venue_provider = providers_factories.AllocineVenueProviderFactory()

        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue_provider.venue.id,
            provider_id=venue_provider.provider.id,
        )
        assert response.status_code == 303
        assert (
            providers_models.VenueProvider.query.filter(providers_models.VenueProvider.id == venue_provider.id).count()
            == 1
        )
        assert history_models.ActionHistory.query.count() == 0
        assert response.location == url_for(
            "backoffice_web.venue.get", venue_id=venue_provider.venue.id, _external=True
        )

        response = authenticated_client.get(response.location)
        assert "Impossible d'effacer le lien entre le lieu et Allociné." in html_parser.extract_alert(response.data)
