import json
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from operator import attrgetter
from unittest.mock import patch

import pytest
import sqlalchemy as sa
from flask import url_for

from pcapi.connectors import api_adresse
from pcapi.connectors.clickhouse import query_mock as clickhouse_query_mock
from pcapi.connectors.entreprise import models as entreprise_models
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.criteria import models as criteria_models
from pcapi.core.educational import factories as educational_factories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.geography import models as geography_models
from pcapi.core.geography import utils as geography_utils
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
from pcapi.core.users import factories as users_factories
from pcapi.core.users.backoffice import api as backoffice_api
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.backoffice.pro.forms import TypeOptions
from pcapi.utils import date as date_utils
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
    return venue


@pytest.fixture(scope="function", name="venue_with_no_siret")
def venue_with_no_siret_fixture(offerer) -> offerers_models.Venue:
    venue = offerers_factories.VenueWithoutSiretFactory(
        venueLabel=offerers_factories.VenueLabelFactory(label="Lieu test"),
        contact__website="www.example.com",
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
            offererAddress__address__postalCode="82000",
            offererAddress__address__departmentCode="82",
            isPermanent=True,
        ),
        offerers_factories.VenueFactory(
            id=43,
            venueTypeCode=offerers_models.VenueTypeCode.GAMES,
            venueLabelId=offerers_factories.VenueLabelFactory(label="Scènes conventionnées").id,
            criteria=criteria[2:],
            offererAddress__address__postalCode="45000",
            offererAddress__address__departmentCode="45",
            isPermanent=False,
        ),
    ]


class ListVenuesTest(GetEndpointHelper):
    endpoint = "backoffice_web.venue.list_venues"
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    # Use assert_num_queries() instead of assert_no_duplicated_queries() which does not detect one extra query caused
    # by a field added in the jinja template.
    # - fetch session + user (1 query)
    # - fetch venue_label for select (1 query)
    # - fetch venues with joinedload including extra data (1 query)
    expected_num_queries = 3

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
        assert rows[0]["Entité juridique"] == venues[0].managingOfferer.name
        assert rows[0]["Permanent"] == "Partenaire culturel permanent"
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
            offerers_factories.VenueWithoutSiretFactory(managingOfferer=offerer),
        ]
        soft_deleted_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        soft_deleted_venue.isSoftDeleted = True
        db.session.add(soft_deleted_venue)
        db.session.flush()

        offerer_id = offerer.id
        # 1 more request is necessary to prefill form choices with selected offerer(s)
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, offerer=offerer_id))

        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == len(matching_venues)
        assert {int(row["ID"]) for row in rows} == {venue.id for venue in matching_venues}
        for row in rows:
            assert row["Entité juridique"] == offerer.name

    def test_list_venues_by_regions(self, authenticated_client, venues):
        venue = offerers_factories.VenueFactory(
            offererAddress__address__postalCode="82000",
            offererAddress__address__departmentCode="82",
        )
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

    def test_list_venues_by_provider(self, authenticated_client, venues):
        venue_provider_1 = providers_factories.VenueProviderFactory()
        provider_id = venue_provider_1.provider.id
        venue_provider_2 = providers_factories.VenueProviderFactory(provider=venue_provider_1.provider)
        providers_factories.VenueProviderFactory()

        # 1 more request to prefill form choices with selected provider
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, provider=provider_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert {int(row["ID"]) for row in rows} == {venue_provider_1.venue.id, venue_provider_2.venue.id}

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
        not_validated_offerer = offerers_factories.NewOffererFactory()
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            offererAddress__address__postalCode="62000",
            offererAddress__address__departmentCode="62",
        )
        offerers_factories.VenueFactory(
            managingOfferer=not_validated_offerer,
            offererAddress__address__postalCode="62000",
            offererAddress__address__departmentCode="62",
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, only_validated_offerers="on", department="62"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(venue.id)
        assert rows[0]["Entité juridique"] == offerer.name


class GetVenueTest(GetEndpointHelper):
    endpoint = "backoffice_web.venue.get"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # get session + user (1 query)
    # get venue (1 query)
    expected_num_queries = 2

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

    def test_get_venue(self, authenticated_client):
        venue = offerers_factories.VenueFactory(
            venueLabel=offerers_factories.VenueLabelFactory(label="Lieu test"),
            contact__website="www.example.com",
            publicName="Le grand Rantanplan 1",
            managingOfferer__allowedOnAdage=False,
            offererAddress__address__street="1 Boulevard de la Croisette",
            offererAddress__address__postalCode="06400",
            offererAddress__address__city="Cannes",
            offererAddress__address__latitude=43.551407,
            offererAddress__address__longitude=7.017984,
            offererAddress__address__inseeCode="06029",
            offererAddress__address__banId="06029_0880_00001",
            offererAddress__address__departmentCode="06",
            isOpenToPublic=True,
        )
        url = url_for(self.endpoint, venue_id=venue.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert venue.name in response_text
        assert f"Nom d'usage : {venue.publicName} " in response_text
        assert f"Venue ID : {venue.id} " in response_text
        assert f"SIRET : {venue.siret} " in response_text
        assert "Région : Provence-Alpes-Côte d'Azur" in response_text
        assert f"Ville : {venue.offererAddress.address.city} " in response_text
        assert f"Code postal : {venue.offererAddress.address.postalCode} " in response_text
        assert f"Email : {venue.bookingEmail} " in response_text
        assert f"Numéro de téléphone : {venue.contact.phone_number} " in response_text
        assert "Peut créer une offre EAC : Non" in response_text
        assert "Cartographié sur ADAGE : Non" in response_text
        assert "ID ADAGE" not in response_text
        assert "Ouvert au public : Oui" in response_text
        assert "Site web : https://www.example.com" in response_text
        assert f"Activité principale : {venue.venueTypeCode.value}" in response_text
        assert f"Label : {venue.venueLabel.label} " in response_text
        assert "Type de lieu" not in response_text
        assert f"Entité juridique : {venue.managingOfferer.name}" in response_text
        assert "Site web : https://www.example.com" in response_text
        assert "Validation des offres : Suivre les règles" in response_text

        badges = html_parser.extract(response.data, tag="span", class_="badge")
        assert "Partenaire culturel" in badges
        assert "Suspendu" not in badges

    def test_get_venue_with_adage_id(self, authenticated_client):
        venue_id = offerers_factories.VenueFactory(
            adageId="7122022", contact=None, managingOfferer__allowedOnAdage=True
        ).id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert "Peut créer une offre EAC : Oui" in response_text
        assert "Cartographié sur ADAGE : Oui" in response_text
        assert "ID ADAGE : 7122022" in response_text

    def test_get_venue_with_no_contact(self, authenticated_client):
        venue = offerers_factories.VenueFactory(contact=None)

        venue_id = venue.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert f"Email : {venue.bookingEmail}" in response_text
        assert "Numéro de téléphone :" not in response_text

    def test_get_venue_with_no_address(self, authenticated_client):
        venue = offerers_factories.VenueFactory(offererAddress=None)

        venue_id = venue.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert venue.common_name in response_text
        for field in ("Région", "Code postal", "Ville", "Coordonnées"):
            assert f"{field} :" not in response_text

    def test_get_venue_with_provider(self, authenticated_client):
        venue_provider = providers_factories.AllocineVenueProviderFactory(lastSyncDate=datetime(2024, 1, 5, 12, 0))
        venue_id = venue_provider.venue.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert "Provider : Allociné" in content
        assert "Dernière synchronisation : 05/01/2024 à 13h00" in content
        assert f"/pro/venue/{venue_id}/delete/{venue_provider.provider.id}".encode() not in response.data

    def test_get_venue_with_provider_not_allocine(
        self,
        authenticated_client,
    ):
        venue_provider = providers_factories.VenueProviderFactory()
        venue_id = venue_provider.venue.id

        response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
        assert response.status_code == 200
        assert f"/pro/venue/{venue_id}/provider/{venue_provider.provider.id}/delete".encode() in response.data

    @pytest.mark.parametrize(
        "factory, expected_text",
        [
            (offerers_factories.WhitelistedVenueConfidenceRuleFactory, "Validation auto"),
            (offerers_factories.ManualReviewVenueConfidenceRuleFactory, "Revue manuelle"),
        ],
    )
    def test_get_venue_with_confidence_rule(self, authenticated_client, factory, expected_text):
        rule = factory()
        url = url_for(self.endpoint, venue_id=rule.venue.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert f"Validation des offres : {expected_text}" in response_text

    @pytest.mark.parametrize(
        "factory, expected_text",
        [
            (offerers_factories.WhitelistedOffererConfidenceRuleFactory, "Validation auto (entité juridique)"),
            (offerers_factories.ManualReviewOffererConfidenceRuleFactory, "Revue manuelle (entité juridique)"),
        ],
    )
    def test_get_venue_with_offerer_confidence_rule(self, authenticated_client, factory, expected_text):
        rule = factory()
        venue = offerers_factories.VenueFactory(managingOfferer=rule.offerer)
        url = url_for(self.endpoint, venue_id=venue.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert f"Validation des offres : {expected_text}" in response_text

    def test_get_caledonian_venue(self, authenticated_client):
        venue = offerers_factories.CaledonianVenueFactory()
        url = url_for(self.endpoint, venue_id=venue.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert venue.name in response_text
        assert f"Venue ID : {venue.id} " in response_text
        assert venue.siret not in response_text
        assert f"RIDET : {venue.ridet} " in response_text
        assert "Région : Nouvelle-Calédonie " in response_text
        assert f"Ville : {venue.offererAddress.address.city} " in response_text
        assert f"Code postal : {venue.offererAddress.address.postalCode} " in response_text
        assert f"Numéro de téléphone : {venue.contact.phone_number} " in response_text
        assert "Peut créer une offre EAC : Non" in response_text
        assert "Cartographié sur ADAGE" not in response_text
        assert "ID ADAGE" not in response_text

    def test_get_fraudulent_venue(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        bookings_factories.FraudulentBookingTagFactory(booking__stock__offer__venue=venue)
        url = url_for(self.endpoint, venue_id=venue.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert "Réservations frauduleuses" in response_text

    def test_get_venue_managed_by_closed_offerer(self, authenticated_client):
        closed_venue = offerers_factories.VenueFactory(managingOfferer=offerers_factories.ClosedOffererFactory())
        url = url_for(self.endpoint, venue_id=closed_venue.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert "Partenaire culturel Fermé " in response_text

    def test_can_reset_venue(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        url = url_for(self.endpoint, venue_id=venue.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert ' data-has-reset="true" ' in str(response.data)


class GetVenueStatsTest(GetEndpointHelper):
    endpoint = "backoffice_web.venue.get_stats"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # get session + user (1 query)
    # get venue with pricing point (1 query)
    # get collective offers templates count (1 query)
    expected_num_queries = 3

    def test_venue_total_revenue_from_clickhouse(self, authenticated_client):
        venue_id = offerers_factories.VenueFactory().id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        response_text = html_parser.extract_cards_text(response.data)
        assert (
            "Offres 137 individuelles 125 réservables | 12 non réservables 56 collectives 54 réservables | 2 non réservables 0 vitrine"
            in response_text[0]
        )
        assert "Réservations 876 individuelles 678 collectives" in response_text[1]
        assert "Chiffre d'affaires 70,48 € Plus de détails" in response_text[2]

    def test_get_venue_not_found(self, authenticated_client):
        response = authenticated_client.get(url_for(self.endpoint, venue_id=1))
        assert response.status_code == 404

    @pytest.mark.settings(CLICKHOUSE_BACKEND="pcapi.connectors.clickhouse.backend.ClickhouseBackend")
    @patch(
        "pcapi.connectors.clickhouse.backend.BaseBackend.run_query",
        side_effect=ApiErrors(errors={"clickhouse": "Error : plouf"}, status_code=400),
    )
    def test_clickhouse_connector_raises_api_error(self, mock_run_query, authenticated_client):
        venue_id = offerers_factories.VenueFactory().id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        assert (
            "Offres N/A individuelle N/A réservable | N/A non réservable N/A collective N/A réservable | N/A non réservable 0 vitrine"
            in html_parser.extract_cards_text(response.data)[0]
        )
        assert "Réservations N/A individuelle N/A collective" in html_parser.extract_cards_text(response.data)[1]
        assert "Chiffre d'affaires N/A" in html_parser.extract_cards_text(response.data)[2]


class GetVenueRevenueDetailsTest(GetEndpointHelper):
    endpoint = "backoffice_web.venue.get_revenue_details"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # session + user
    # venue and offerer (to check is_caledonian)
    expected_num_queries = 2

    @patch(
        "pcapi.connectors.clickhouse.testing_backend.TestingBackend.run_query",
        return_value=[
            clickhouse_query_mock.MockAggregatedRevenueQueryResult(
                2024,
                individual=Decimal("246.80"),
                expected_individual=Decimal("357.90"),
                collective=Decimal("750"),
                expected_collective=Decimal("1250"),
            ),
            clickhouse_query_mock.MockAggregatedRevenueQueryResult(
                2022,
                individual=Decimal("123.40"),
                expected_individual=Decimal("123.40"),
                collective=Decimal("1500"),
                expected_collective=Decimal("1500"),
            ),
        ],
    )
    def test_venue_revenue_details_from_clickhouse(self, mock_run_query, authenticated_client):
        venue_id = offerers_factories.VenueFactory().id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        mock_run_query.assert_called_once()

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 3
        assert rows[0]["Année"] == "En cours"
        assert rows[0]["CA offres IND"] == "111,10 €"
        assert rows[0]["CA offres EAC"] == "500,00 €"
        assert rows[1]["Année"] == "2024"
        assert rows[1]["CA offres IND"] == "246,80 €"
        assert rows[1]["CA offres EAC"] == "750,00 €"
        assert rows[2]["Année"] == "2022"
        assert rows[2]["CA offres IND"] == "123,40 €"
        assert rows[2]["CA offres EAC"] == "1 500,00 €"


class DeleteVenueTest(PostEndpointHelper):
    endpoint = "backoffice_web.venue.delete_venue"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.DELETE_PRO_ENTITY

    def test_delete_venue(self, legit_user, authenticated_client):
        venue_to_delete = offerers_factories.VenueFactory()
        venue_to_delete_name = venue_to_delete.name
        venue_to_delete_id = venue_to_delete.id
        offerers_factories.VenueFactory(managingOfferer=venue_to_delete.managingOfferer)  # remaining venue

        response = self.post_to_endpoint(authenticated_client, venue_id=venue_to_delete.id)
        assert response.status_code == 303
        assert (
            db.session.query(offerers_models.Venue).filter(offerers_models.Venue.id == venue_to_delete_id).count() == 0
        )

        expected_url = url_for("backoffice_web.pro.search_pro")
        assert response.location == expected_url
        response = authenticated_client.get(expected_url)
        assert (
            html_parser.extract_alert(response.data)
            == f"Le partenaire culturel {venue_to_delete_name} ({venue_to_delete_id}) a été supprimé"
        )

    def test_cant_delete_venue_with_bookings(self, legit_user, authenticated_client):
        booking = bookings_factories.BookingFactory()
        venue_to_delete = booking.venue
        venue_to_delete_id = venue_to_delete.id

        response = self.post_to_endpoint(authenticated_client, venue_id=venue_to_delete.id)
        assert response.status_code == 303
        assert (
            db.session.query(offerers_models.Venue).filter(offerers_models.Venue.id == venue_to_delete_id).count() == 1
        )

        expected_url = url_for("backoffice_web.venue.get", venue_id=venue_to_delete.id)
        assert response.location == expected_url
        response = authenticated_client.get(expected_url)
        assert (
            html_parser.extract_alert(response.data)
            == "Impossible de supprimer un partenaire culturel pour lequel il existe des réservations"
        )

    def test_cant_delete_venue_when_pricing_point_for_another_venue(self, legit_user, authenticated_client):
        venue_to_delete = offerers_factories.VenueFactory(pricing_point="self")
        offerers_factories.VenueFactory(pricing_point=venue_to_delete, managingOfferer=venue_to_delete.managingOfferer)
        venue_to_delete_id = venue_to_delete.id

        response = self.post_to_endpoint(authenticated_client, venue_id=venue_to_delete.id)
        assert response.status_code == 303
        assert (
            db.session.query(offerers_models.Venue).filter(offerers_models.Venue.id == venue_to_delete_id).count() == 1
        )

        expected_url = url_for("backoffice_web.venue.get", venue_id=venue_to_delete.id)
        assert response.location == expected_url
        response = authenticated_client.get(expected_url)
        assert (
            html_parser.extract_alert(response.data)
            == "Impossible de supprimer un partenaire culturel utilisé comme point de valorisation d'un autre partenaire culturel"
        )

    def test_cant_delete_venue_with_custom_reimbursement_rule(self, legit_user, authenticated_client):
        venue_to_delete = offerers_factories.VenueFactory(pricing_point="self")
        finance_factories.CustomReimbursementRuleFactory(offer=None, venue=venue_to_delete)
        venue_to_delete_id = venue_to_delete.id

        response = self.post_to_endpoint(authenticated_client, venue_id=venue_to_delete.id, follow_redirects=True)
        assert response.status_code == 200  # after redirect
        assert (
            db.session.query(offerers_models.Venue).filter(offerers_models.Venue.id == venue_to_delete_id).count() == 1
        )

        assert (
            html_parser.extract_alert(response.data)
            == "Impossible de supprimer un point de valorisation ayant un tarif dérogatoire (passé, actif ou futur)"
        )

    def test_cant_delete_last_venue(self, legit_user, authenticated_client):
        venue_id = offerers_factories.VenueFactory(pricing_point="self").id

        response = self.post_to_endpoint(authenticated_client, venue_id=venue_id, follow_redirects=True)
        assert response.status_code == 200  # after redirect
        assert db.session.query(offerers_models.Venue).filter(offerers_models.Venue.id == venue_id).count() == 1

        assert html_parser.extract_alert(response.data) == (
            "Impossible de supprimer l'unique partenaire culturel de l'entité juridique. "
            "Si cela est pertinent, préférer la suppression de l'entité juridique."
        )

    def test_no_script_injection_in_venue_name(self, legit_user, authenticated_client):
        venue = offerers_factories.VenueFactory(name="Lieu <script>alert('coucou')</script>")
        offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)  # remaining venue
        venue_id = venue.id

        response = self.post_to_endpoint(authenticated_client, venue_id=venue_id)
        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == f"Le partenaire culturel Lieu <script>alert('coucou')</script> ({venue_id}) a été supprimé"
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
            "city": venue.offererAddress.address.city or "",
            "postal_code": venue.offererAddress.address.postalCode or "",
            "insee_code": venue.offererAddress.address.inseeCode or "",
            "street": venue.offererAddress.address.street or "",
            "ban_id": venue.offererAddress.address.banId or "",
            "acceslibre_url": venue.external_accessibility_url or "",
            "acceslibre_id": venue.external_accessibility_id or "",
            "booking_email": venue.bookingEmail or "",
            "phone_number": venue.contact.phone_number or "",
            "longitude": venue.offererAddress.address.longitude,
            "latitude": venue.offererAddress.address.latitude,
            "is_permanent": venue.isPermanent,
        }

    @pytest.mark.parametrize(
        "siren,old_siret,new_siret",
        [("123456789", "12345678900012", "12345678900023"), ("NC1234567", "NC1234567001XX", "NC1234567002XX")],
    )
    @patch(
        "pcapi.connectors.api_adresse.get_address",
        return_value=api_adresse.AddressInfo(
            id="75101_5888_00023",
            label="23 Boulevard de la Madeleine 75001 Paris",
            postcode="75001",
            citycode="75101",
            latitude=48.869311,
            longitude=2.325463,
            score=1,
            city="Paris",
            street="23 Boulevard de la Madeleine",
            type="housenumber",
        ),
    )
    def test_update_venue(self, mock_get_address, authenticated_client, siren, old_siret, new_siret):
        offerer = offerers_factories.OffererFactory(siren=siren)
        contact_email = "contact.venue@example.com"
        website = "update.venue@example.com"
        social_medias = {"instagram": "https://instagram.com/update.venue"}
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            siret=old_siret,
            contact__email=contact_email,
            contact__website=website,
            contact__social_medias=social_medias,
            name="Venue Name",
            isOpenToPublic=True,
        )

        data = {
            "name": "IKEA",
            "public_name": "Ikea city",
            "siret": new_siret,
            "city": "Paris",
            "postal_code": "75001",
            "insee_code": "75101",
            "street": "23 Boulevard de la Madeleine",
            "ban_id": "75101_5888_00023",
            "is_manual_address": "",  # autocompletion used
            "booking_email": venue.bookingEmail + ".update",
            "phone_number": "+33102030456",
            "is_permanent": True,
            "latitude": "48.869311",
            "longitude": "2.325463",
            "acceslibre_url": None,
        }

        # coordinates values are Decimals rounded to five digits in database
        expected_latitude = geography_utils.format_coordinate(data["latitude"])
        expected_longitude = geography_utils.format_coordinate(data["longitude"])

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id)

        db.session.refresh(venue)
        offerer_address = db.session.query(offerers_models.OffererAddress).one()  # address updated in the same OA
        address = offerer_address.address

        assert venue.name == data["name"]
        assert venue.publicName == data["public_name"]
        assert venue.siret == data["siret"]
        assert venue.bookingEmail == data["booking_email"]
        assert venue.contact.phone_number == data["phone_number"]
        assert venue.isPermanent == data["is_permanent"]
        assert address.city == data["city"]
        assert address.postalCode == data["postal_code"]
        assert address.street == data["street"]
        assert address.banId == data["ban_id"]
        assert address.latitude == expected_latitude
        assert address.longitude == expected_longitude
        assert address.inseeCode == "75101"
        assert address.isManualEdition is False
        assert venue.offererAddress == offerer_address
        assert offerer_address.type == offerers_models.LocationType.VENUE_LOCATION
        assert offerer_address.venue == venue

        # should not have been updated or erased
        assert venue.contact.email == contact_email
        assert venue.contact.website == website
        assert venue.contact.social_medias == social_medias

        assert len(venue.action_history) == 2

        # Check the venue update action
        update_action = [action for action in venue.action_history if action.extraData["modified_info"].get("name")][0]
        update_snapshot = update_action.extraData["modified_info"]
        assert update_snapshot["bookingEmail"]["new_info"] == data["booking_email"]
        assert update_snapshot["offererAddress.address.street"]["new_info"] == data["street"]
        assert update_snapshot["offererAddress.address.latitude"]["new_info"] == str(expected_latitude)
        assert update_snapshot["offererAddress.address.longitude"]["new_info"] == str(expected_longitude)
        assert update_snapshot["offererAddress.addressId"]["new_info"] == offerer_address.address.id

        # Check the acces libre update action
        # The folloing assert is a reminder that acceslibre_url must be None to get the updated acceslibre_url
        # from the associated backend. It is updated in a async task which is executed during the tests though
        # probably not asynchronously but ends up with unpredictable results.
        # Slug could be either mon-lieu-chez-acceslibre or whatever the original slug was.
        assert data["acceslibre_url"] is None
        acceslibre_action = [
            action
            for action in venue.action_history
            if action.extraData["modified_info"].get("accessibilityProvider.externalAccessibilityId")
        ][0]
        acceslibre_snapshot = acceslibre_action.extraData["modified_info"]
        assert (
            acceslibre_snapshot["accessibilityProvider.externalAccessibilityId"]["new_info"]
            == "mon-lieu-chez-acceslibre"
        )
        assert acceslibre_snapshot["accessibilityProvider.externalAccessibilityId"]["old_info"] is None
        assert (
            acceslibre_snapshot["accessibilityProvider.externalAccessibilityUrl"]["new_info"]
            == "https://acceslibre.beta.gouv.fr/app/activite/mon-lieu-chez-acceslibre/"
        )
        assert acceslibre_snapshot["accessibilityProvider.externalAccessibilityUrl"]["old_info"] is None

        assert len(mails_testing.outbox) == 1
        # check that email is sent when venue is set to permanent and has no image
        assert mails_testing.outbox[0]["To"] == venue.bookingEmail
        assert mails_testing.outbox[0]["template"] == TransactionalEmail.VENUE_NEEDS_PICTURE.value.__dict__
        assert mails_testing.outbox[0]["params"]["VENUE_NAME"] == venue.common_name
        assert mails_testing.outbox[0]["params"]["VENUE_FORM_URL"] == urls.build_pc_pro_venue_link(venue)

    def test_update_venue_location_with_offerer_address_not_manual(self, authenticated_client, offerer):
        contact_email = "contact.venue@example.com"
        website = "update.venue@example.com"
        social_medias = {"instagram": "https://instagram.com/update.venue"}
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            contact__email=contact_email,
            contact__website=website,
            contact__social_medias=social_medias,
            isOpenToPublic=True,
        )

        data = {
            "name": "IKEA",
            "public_name": "Ikea city",
            "siret": venue.managingOfferer.siren + "98765",
            "city": "Paris",
            "postal_code": "75001",
            "street": "23 Boulevard de la Madeleine",
            "ban_id": "75101_5888_00023",
            "is_manual_address": "",  # autocompletion used
            "booking_email": venue.bookingEmail + ".update",
            "phone_number": "+33102030456",
            "is_permanent": True,
            "latitude": "48.869311",
            "longitude": "2.325463",
            "acceslibre_url": "https://acceslibre.beta.gouv.fr/app/slug/",
        }

        # coordinates values are Decimals rounded to five digits in database
        expected_latitude = geography_utils.format_coordinate(data["latitude"])
        expected_longitude = geography_utils.format_coordinate(data["longitude"])

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id)

        db.session.refresh(venue)
        offerer_address = db.session.query(offerers_models.OffererAddress).one()
        assert venue.offererAddress == offerer_address
        assert len(venue.action_history) == 2
        update_action = [action for action in venue.action_history if action.extraData["modified_info"].get("name")][0]
        update_snapshot = update_action.extraData["modified_info"]

        assert update_snapshot["bookingEmail"]["new_info"] == data["booking_email"]
        assert update_snapshot["offererAddress.addressId"]["new_info"] == offerer_address.addressId
        assert update_snapshot["offererAddress.address.street"]["new_info"] == data["street"]
        assert update_snapshot["offererAddress.address.latitude"]["new_info"] == str(expected_latitude)
        assert update_snapshot["offererAddress.address.longitude"]["new_info"] == str(expected_longitude)
        assert "offererAddress.address.city" not in update_snapshot  # not changed

    @pytest.mark.parametrize(
        "api_adresse_patch_params,expected_insee_code,ban_id",
        [
            ({"side_effect": api_adresse.NoResultException}, None, "97129_hz0hwa_00044"),
            (
                {
                    "return_value": api_adresse.AddressInfo(
                        id="unused",
                        label="unused",
                        postcode="unused",
                        citycode="97129",
                        latitude=1,
                        longitude=1,
                        score=1,
                        city="unused",
                        street="unused",
                        type="housenumber",
                    )
                },
                "97129",
                None,
            ),
        ],
    )
    def test_updating_venue_manual_address(
        self,
        authenticated_client,
        offerer,
        api_adresse_patch_params,
        expected_insee_code,
        ban_id,
    ):
        contact_email = "contact.venue@example.com"
        website = "update.venue@example.com"
        social_medias = {"instagram": "https://instagram.com/update.venue"}
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            contact__email=contact_email,
            contact__website=website,
            contact__social_medias=social_medias,
            isOpenToPublic=True,
        )
        oa_id = venue.offererAddress.id

        data = {
            "name": "Musée du Rhum",
            "public_name": "Musée du Rhum",
            "siret": venue.managingOfferer.siren + "98765",
            "city": "Sainte-Rose",
            "postal_code": "97115",
            "street": "Chemin de Bellevue",
            "ban_id": ban_id,
            "is_manual_address": "on",
            "booking_email": venue.bookingEmail + ".update",
            "phone_number": "+33102030456",
            "is_permanent": True,
            "latitude": "16.306774",
            "longitude": "-61.703636",
            "acceslibre_url": "https://acceslibre.beta.gouv.fr/app/slug/",
        }

        with patch("pcapi.connectors.api_adresse.get_municipality_centroid", **api_adresse_patch_params):
            response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id)

        db.session.refresh(venue)
        offerer_address = db.session.query(offerers_models.OffererAddress).one()
        address = offerer_address.address

        assert offerer_address.id == oa_id
        assert offerer_address.addressId == address.id
        assert address.inseeCode == expected_insee_code
        assert address.timezone == "America/Guadeloupe"
        assert address.isManualEdition is True
        assert address.banId is None

        # should not have been updated or erased
        assert venue.contact.email == contact_email
        assert venue.contact.website == website
        assert venue.contact.social_medias == social_medias

        assert len(venue.action_history) == 2

        assert len(mails_testing.outbox) == 1
        # check that email is sent when venue is set to permanent and has no image
        assert mails_testing.outbox[0]["To"] == venue.bookingEmail
        assert mails_testing.outbox[0]["template"] == TransactionalEmail.VENUE_NEEDS_PICTURE.value.__dict__
        assert mails_testing.outbox[0]["params"]["VENUE_NAME"] == venue.common_name
        assert mails_testing.outbox[0]["params"]["VENUE_FORM_URL"] == urls.build_pc_pro_venue_link(venue)

    def test_updating_venue_manual_address_with_initial_ban_id(
        self,
        authenticated_client,
        offerer,
    ):
        contact_email = "contact.venue@example.com"
        website = "update.venue@example.com"
        social_medias = {"instagram": "https://instagram.com/update.venue"}
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            contact__email=contact_email,
            contact__website=website,
            contact__social_medias=social_medias,
            offererAddress__address__banId="97129_hz0hwa_00044",
            isOpenToPublic=True,
        )

        data = {
            "name": "Musée du Rhum",
            "public_name": "Musée du Rhum",
            "siret": venue.managingOfferer.siren + "98765",
            "city": "Sainte-Rose",
            "postal_code": "97115",
            "street": "Chemin de Bellevue",
            "ban_id": "97129_hz0hwa_00044",
            "is_manual_address": "on",
            "booking_email": venue.bookingEmail + ".update",
            "phone_number": "+33102030456",
            "is_permanent": True,
            "latitude": "16.306774",
            "longitude": "-61.703636",
            "acceslibre_url": "https://acceslibre.beta.gouv.fr/app/slug/",
        }

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id)

        db.session.refresh(venue)
        address = db.session.query(geography_models.Address).order_by(geography_models.Address.id.desc()).first()
        offerer_address = db.session.query(offerers_models.OffererAddress).one()
        assert venue.offererAddress == offerer_address
        assert address.isManualEdition is True
        assert address.banId is None

    @patch(
        "pcapi.connectors.api_adresse.get_municipality_centroid",
        return_value=api_adresse.AddressInfo(
            id="unused",
            label="unused",
            postcode="unused",
            citycode="97411",
            latitude=1,
            longitude=1,
            score=1,
            city="Saint-Denis",
            street="unused",
            type="housenumber",
        ),
    )
    def test_update_venue_with_address_manual_edition_clear_field_ban_id(
        self, mock_get_municipality_centroid, authenticated_client
    ):
        venue = offerers_factories.VenueFactory()
        other_venue = offerers_factories.VenueFactory(
            offererAddress__address__street="1 Rue Poivre",
            offererAddress__address__postalCode="97400",
            offererAddress__address__city="Saint-Denis",
            offererAddress__address__latitude=-20.88756,
            offererAddress__address__longitude=55.451442,
            offererAddress__address__banId="97411_1120_00001",
        )

        data = {
            "name": venue.name,
            "public_name": venue.publicName,
            "siret": venue.siret,
            "city": other_venue.offererAddress.address.city,
            "postal_code": other_venue.offererAddress.address.postalCode,
            "street": other_venue.offererAddress.address.street,
            "ban_id": other_venue.offererAddress.address.banId,
            "is_manual_address": "on",
            "booking_email": venue.bookingEmail,
            "phone_number": venue.contact.phone_number,
            "is_permanent": venue.isPermanent,
            "latitude": other_venue.offererAddress.address.latitude,
            "longitude": other_venue.offererAddress.address.longitude,
            "acceslibre_url": "",
        }

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)
        assert response.status_code == 303

        db.session.refresh(venue)

        assert venue.offererAddress != other_venue.offererAddress
        assert venue.offererAddress.addressId != other_venue.offererAddress.addressId
        address = venue.offererAddress.address
        assert address.isManualEdition is True
        assert address.street == other_venue.offererAddress.address.street
        assert address.city == other_venue.offererAddress.address.city
        assert address.banId is None

        update_snapshot = venue.action_history[0].extraData["modified_info"]
        assert not update_snapshot.get("offererAddress.address.banId")

    @patch(
        "pcapi.connectors.api_adresse.get_municipality_centroid",
        return_value=api_adresse.AddressInfo(
            id="unused",
            label="unused",
            postcode="unused",
            citycode="97411",
            latitude=1,
            longitude=1,
            score=1,
            city="Saint-Denis",
            street="unused",
            type="housenumber",
        ),
    )
    def test_update_venue_with_address_manual_edition_clear_field_street(
        self, mock_get_municipality_centroid, authenticated_client
    ):
        venue = offerers_factories.VenueFactory(
            offererAddress__address__street="1 Rue Poivre",
            offererAddress__address__postalCode="97400",
            offererAddress__address__city="Saint-Denis",
            offererAddress__address__latitude=-20.88756,
            offererAddress__address__longitude=55.451442,
            offererAddress__address__banId="97411_1120_00001",
        )
        original_offerer_address_id = venue.offererAddress.id
        original_address_id = venue.offererAddress.addressId
        original_street = venue.offererAddress.address.street

        data = self._get_current_data(venue)
        data["is_manual_address"] = "on"
        data["street"] = None

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)
        assert response.status_code == 400

        db.session.refresh(venue)

        assert venue.offererAddress.id == original_offerer_address_id
        assert venue.offererAddress.addressId == original_address_id
        assert venue.offererAddress.address.isManualEdition is False
        assert venue.offererAddress.address.street == original_street

    @patch(
        "pcapi.connectors.api_adresse.get_municipality_centroid",
        return_value=api_adresse.AddressInfo(
            id="unused",
            label="unused",
            postcode="unused",
            citycode="97411",
            latitude=1,
            longitude=1,
            score=1,
            city="Saint-Denis",
            street="unused",
            type="housenumber",
        ),
    )
    def test_update_venue_manual_address_reuses_existing_manual_edited_address_even_with_sending_old_ban_id(
        self, mock_get_municipality_centroid, authenticated_client
    ):
        venue = offerers_factories.VenueFactory()
        offerer_address_id = venue.offererAddress.id
        other_venue = offerers_factories.VenueFactory(
            offererAddress__address__street="1 Rue Poivre",
            offererAddress__address__postalCode="97400",
            offererAddress__address__city="Saint-Denis",
            offererAddress__address__latitude=-20.88756,
            offererAddress__address__longitude=55.451442,
            offererAddress__address__banId=None,
            offererAddress__address__isManualEdition=True,
            offererAddress__address__inseeCode="97411",
        )

        data = {
            "name": venue.name,
            "public_name": venue.publicName,
            "siret": venue.siret,
            "city": other_venue.offererAddress.address.city,
            "postal_code": other_venue.offererAddress.address.postalCode,
            "street": other_venue.offererAddress.address.street,
            "ban_id": venue.offererAddress.address.banId,
            "is_manual_address": "on",
            "booking_email": venue.bookingEmail,
            "phone_number": venue.contact.phone_number,
            "is_permanent": venue.isPermanent,
            "latitude": other_venue.offererAddress.address.latitude,
            "longitude": other_venue.offererAddress.address.longitude,
            "acceslibre_url": "",
        }

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)
        assert response.status_code == 303

        db.session.refresh(venue)

        assert venue.offererAddress.id == offerer_address_id
        assert venue.offererAddress.addressId == other_venue.offererAddress.addressId
        address = venue.offererAddress.address
        assert address.isManualEdition is True
        assert address.banId == other_venue.offererAddress.address.banId

    @patch(
        "pcapi.connectors.api_adresse.get_municipality_centroid",
        return_value=api_adresse.AddressInfo(
            id="unused",
            label="unused",
            postcode="unused",
            citycode="97411",
            latitude=1,
            longitude=1,
            score=1,
            city="Saint-Denis",
            street="unused",
            type="housenumber",
        ),
    )
    def test_update_venue_manual_address_reuses_existing_manual_edited_address_without_ban_id_case(
        self, mock_get_municipality_centroid, authenticated_client
    ):
        venue = offerers_factories.VenueFactory()
        offerer_address_id = venue.offererAddress.id
        other_venue = offerers_factories.VenueFactory(
            offererAddress__address__street="1 Rue Poivre",
            offererAddress__address__postalCode="97400",
            offererAddress__address__city="Saint-Denis",
            offererAddress__address__latitude=-20.88756,
            offererAddress__address__longitude=55.451442,
            offererAddress__address__banId=None,
            offererAddress__address__isManualEdition=True,
            offererAddress__address__inseeCode="97411",
        )

        data = {
            "name": venue.name,
            "public_name": venue.publicName,
            "siret": venue.siret,
            "city": other_venue.offererAddress.address.city,
            "postal_code": other_venue.offererAddress.address.postalCode,
            "street": other_venue.offererAddress.address.street,
            "banId": "",
            "is_manual_address": "on",
            "booking_email": venue.bookingEmail,
            "phone_number": venue.contact.phone_number,
            "is_permanent": venue.isPermanent,
            "latitude": other_venue.offererAddress.address.latitude,
            "longitude": other_venue.offererAddress.address.longitude,
            "acceslibre_url": "",
        }

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)
        assert response.status_code == 303

        db.session.refresh(venue)

        assert venue.offererAddress.id == offerer_address_id
        assert venue.offererAddress.addressId == other_venue.offererAddress.addressId
        assert venue.offererAddress.address.isManualEdition is True
        assert venue.offererAddress.address.banId is None

    @patch(
        "pcapi.connectors.api_adresse.get_municipality_centroid",
        return_value=api_adresse.AddressInfo(
            id="unused",
            label="unused",
            postcode="unused",
            citycode="97411",
            latitude=1,
            longitude=1,
            score=1,
            city="Saint-Denis",
            street="unused",
            type="housenumber",
        ),
    )
    def test_update_venue_manual_address_with_gps_difference(
        self, mock_get_municipality_centroid, authenticated_client
    ):
        venue = offerers_factories.VenueFactory()
        offerer_address_id = venue.offererAddress.id
        other_venue = offerers_factories.VenueFactory(
            offererAddress__address__street="1 Rue Poivre",
            offererAddress__address__postalCode="97400",
            offererAddress__address__city="Saint-Denis",
            offererAddress__address__latitude=-20.88756,
            offererAddress__address__longitude=55.451442,
            offererAddress__address__banId="97411_1120_00001",
        )

        data = {
            "name": venue.name,
            "public_name": venue.publicName,
            "siret": venue.siret,
            "city": other_venue.offererAddress.address.city,
            "postal_code": other_venue.offererAddress.address.postalCode,
            "street": other_venue.offererAddress.address.street,
            "ban_id": other_venue.offererAddress.address.banId,
            "is_manual_address": "on",
            "booking_email": venue.bookingEmail,
            "phone_number": venue.contact.phone_number,
            "is_permanent": venue.isPermanent,
            "latitude": "-20.88754",
            "longitude": "55.451008",
            "acceslibre_url": "",
        }

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)
        assert response.status_code == 303

        db.session.refresh(venue)

        assert venue.offererAddress.id == offerer_address_id  # venue location never changes
        # same street and Insee code but different GPS position: new row because of manual edition
        assert venue.offererAddress.addressId != other_venue.offererAddress.addressId
        address = venue.offererAddress.address
        assert address.latitude == Decimal("-20.88754")
        assert address.longitude == Decimal("55.45101")
        assert address.isManualEdition is True
        assert address.banId is None

    def test_update_venue_set_address_when_missing(self, authenticated_client):
        venue = offerers_factories.VenueFactory(contact=None, offererAddress=None)

        data = {
            "name": venue.name,
            "public_name": venue.publicName,
            "siret": venue.siret,
            "street": "55 Chemin des Remparts",
            "postal_code": "50170",
            "city": "Le Mont-Saint-Michel",
            "ban_id": "50353_0080_00055",
            "insee_code": "50353",
            "latitude": "48.636446",
            "longitude": "-1.510842",
            "is_manual_address": "",  # autocompletion used
            "booking_email": venue.bookingEmail,
            "phone_number": "",
            "acceslibre_url": "",
            "is_permanent": False,
        }

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data, follow_redirects=True)
        assert response.status_code == 200

        db.session.refresh(venue)
        offerer_address = db.session.query(offerers_models.OffererAddress).one()
        assert venue.offererAddress == offerer_address
        assert len(venue.action_history) == 1
        action = venue.action_history[0]
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.venue == venue
        assert action.extraData["modified_info"] == {
            "offererAddress.address.banId": {"new_info": "50353_0080_00055", "old_info": None},
            "offererAddress.address.city": {"new_info": "Le Mont-Saint-Michel", "old_info": None},
            "offererAddress.address.inseeCode": {"new_info": "50353", "old_info": None},
            "offererAddress.address.isManualEdition": {"new_info": False, "old_info": None},
            "offererAddress.address.latitude": {"new_info": "48.63645", "old_info": None},
            "offererAddress.address.longitude": {"new_info": "-1.51084", "old_info": None},
            "offererAddress.address.postalCode": {"new_info": "50170", "old_info": None},
            "offererAddress.address.street": {"new_info": "55 Chemin des Remparts", "old_info": None},
            "offererAddress.addressId": {"new_info": offerer_address.addressId, "old_info": None},
        }

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
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id)

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

    def test_update_empty_venue_contact_email(self, authenticated_client, offerer):
        website = "update.venue@example.com"
        social_medias = {"instagram": "https://instagram.com/update.venue"}
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            contact__email=None,
            contact__website=website,
            contact__social_medias=social_medias,
        )

        data = self._get_current_data(venue)
        data["phone_number"] = "+33102030456"

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id)

        db.session.refresh(venue)

        # should not have been updated or erased
        assert venue.contact.email is None

    def test_update_venue_empty_phone_number(self, authenticated_client):
        venue = offerers_factories.VenueFactory()

        data = self._get_current_data(venue)
        data["phone_number"] = ""

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303
        db.session.refresh(venue)
        assert venue.contact.phone_number is None

    @pytest.mark.parametrize(
        "original_public_name,new_name",
        [("Original name", "Original name"), ("Public name", "Original name"), ("Public name", "New name")],
    )
    def test_update_venue_empty_public_name(self, authenticated_client, original_public_name, new_name):
        venue = offerers_factories.VenueFactory(name="Original name", publicName=original_public_name)

        data = self._get_current_data(venue)
        data["name"] = new_name
        data["public_name"] = ""

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303
        db.session.refresh(venue)
        assert venue.name == new_name
        assert venue.publicName == new_name  # empty publicName defaults to name

    @pytest.mark.parametrize(
        "field,value",
        [
            ("name", ""),
            ("latitude", "48.87.004"),
            ("latitude", "98.87004"),
            ("longitude", "2.3785O"),
            ("longitude", "237.850"),
            ("latitude", ""),
            ("longitude", ""),
        ],
    )
    def test_update_venue_with_validation_error(self, authenticated_client, field, value):
        venue = offerers_factories.VenueFactory()

        data = self._get_current_data(venue)
        data[field] = value

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 400
        assert "Les données envoyées comportent des erreurs" in response.data.decode("utf-8")

        db.session.refresh(venue)
        assert venue.name

    def test_update_venue_with_same_data(self, authenticated_client):
        venue = offerers_factories.VenueFactory()

        data = self._get_current_data(venue)

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)
        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id)

        db.session.refresh(venue)

        assert len(venue.action_history) == 0

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
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id)

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
            == "Vous ne pouvez pas ajouter le SIRET d'un partenaire culturel. Contactez le support pro N2."
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
            == "Un autre partenaire culturel existe déjà avec le SIRET 11122233344444"
        )
        db.session.refresh(venue)
        assert venue.siret is None

    def test_update_venue_create_siret_when_pricing_point_exists(self, authenticated_client, offerer):
        venue = offerers_factories.VenueWithoutSiretFactory()
        offerers_factories.VenuePricingPointLinkFactory(
            venue=venue,
            pricingPoint=offerers_factories.VenueFactory(),
            timespan=[date_utils.get_naive_utc_now() - timedelta(days=60), None],
        )

        data = self._get_current_data(venue)
        data["siret"] = f"{venue.managingOfferer.siren}12345"

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 400
        assert "Ce partenaire culturel a déjà un point de valorisation" in html_parser.extract_alert(response.data)
        db.session.refresh(venue)
        assert venue.siret is None

    def test_update_venue_create_siret_inactive(self, authenticated_client, offerer):
        venue = offerers_factories.VenueWithoutSiretFactory()

        data = self._get_current_data(venue)
        data["siret"] = f"{venue.managingOfferer.siren}12345"

        with patch(
            "pcapi.connectors.entreprise.api.get_siret_open_data",
            return_value=entreprise_models.SiretInfo(
                siret=f"{venue.managingOfferer.siren}12345",
                siren=venue.managingOfferer.siren,
                name=venue.name,
                ape_code="9001Z",
                ape_label="Arts du spectacle vivant",
                legal_category_code="5710",
                address=entreprise_models.SireneAddress(
                    street="35 Boulevard de Sébastopol", postal_code="75001", insee_code="75056", city="Paris"
                ),
                active=False,
                diffusible=True,
            ),
        ):
            response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 400
        assert (
            html_parser.extract_alert(response.data)
            == "Ce SIRET n'est plus actif, on ne peut pas l'attribuer à ce partenaire culturel"
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
            == "Vous ne pouvez pas modifier le SIRET d'un partenaire culturel. Contactez le support pro N2."
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
        assert (
            html_parser.extract_alert(response.data) == "Vous ne pouvez pas retirer le SIRET d'un partenaire culturel."
        )
        db.session.refresh(venue)
        assert venue.siret

    @pytest.mark.parametrize("siret", ["1234567891234", "123456789123456", "123456789ABCDE", "11122233300001"])
    def test_update_venue_invalid_siret(self, authenticated_client, offerer, siret):
        venue = offerers_factories.VenueFactory(siret="12345678900001", managingOfferer__siren="123456789")

        data = self._get_current_data(venue)
        data["siret"] = " "

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 400

    @pytest.mark.parametrize("removed_field", ["street", "postal_code", "city"])
    def test_update_venue_remove_address_blocked_by_constraint(self, authenticated_client, removed_field):
        venue = offerers_factories.VenueWithoutSiretFactory()

        data = self._get_current_data(venue)
        data[removed_field] = ""

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 400
        assert "Les données envoyées comportent des erreurs." in html_parser.extract_alert(response.data)
        assert venue.offererAddress.address.street
        assert venue.offererAddress.address.postalCode
        assert venue.offererAddress.address.city

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
        venue = offerers_factories.VenueFactory(isPermanent=True)

        data = self._get_current_data(venue)
        data["ban_id"] = "15152_0024_00003"

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303

        db.session.refresh(venue)

        assert venue.offererAddress.address.street == data["street"]
        assert venue.offererAddress.address.banId == data["ban_id"]
        assert set(venue.action_history[0].extraData["modified_info"].keys()) == {
            "offererAddress.address.banId",
            "offererAddress.addressId",
        }
        assert venue.action_history[0].extraData["modified_info"]["offererAddress.address.banId"] == {
            "new_info": "15152_0024_00003",
            "old_info": "75102_7560_00001",
        }

    def test_update_venue_latitude_longitude_precision(self, authenticated_client):
        venue = offerers_factories.VenueFactory(
            offererAddress__address__latitude=48.87004, offererAddress__address__longitude=2.37850
        )

        data = self._get_current_data(venue)
        data["latitude"] = "48.870037"
        data["longitude"] = "2.378504"

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303

        db.session.refresh(venue)

        assert venue.offererAddress.address.latitude == Decimal("48.87004")
        assert venue.offererAddress.address.longitude == Decimal("2.37850")
        assert len(venue.action_history) == 0

    def test_update_venue_latitude_longitude_not_changed(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        data = self._get_current_data(venue)
        data["city"] = "Rome"
        data["is_manual_address"] = "on"

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303

        db.session.refresh(venue)
        assert len(venue.action_history) == 1
        update_snapshot = venue.action_history[0].extraData["modified_info"]
        assert update_snapshot["offererAddress.address.city"]["new_info"] == "Rome"
        assert venue.offererAddress.address.longitude == data["longitude"]
        assert venue.offererAddress.address.latitude == data["latitude"]
        assert "offererAddress.address.longitude" not in update_snapshot
        assert "offererAddress.address.latitude" not in update_snapshot

    def test_update_venue_accessibility_provider_with_url(self, authenticated_client):
        venue = offerers_factories.VenueFactory(venueTypeCode=offerers_models.VenueTypeCode.LIBRARY)
        assert not venue.accessibilityProvider
        data = self._get_current_data(venue)

        data["acceslibre_url"] = "https://acceslibre.beta.gouv.fr/des/trucs/et/&/enfin/mon-slug/"

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)
        assert response.status_code == 303

        db.session.refresh(venue)
        assert venue.external_accessibility_id == "mon-slug"
        assert venue.external_accessibility_url == data["acceslibre_url"]
        assert venue.accessibilityProvider
        assert venue.accessibilityProvider.externalAccessibilityData
        assert venue.action_history[0].extraData == {
            "modified_info": {
                "accessibilityProvider.externalAccessibilityId": {"new_info": "mon-slug", "old_info": None},
                "accessibilityProvider.externalAccessibilityUrl": {
                    "new_info": "https://acceslibre.beta.gouv.fr/des/trucs/et/&/enfin/mon-slug/",
                    "old_info": None,
                },
            }
        }

    def test_update_venue_accessibility_provider_id(self, authenticated_client):
        venue = offerers_factories.VenueFactory(venueTypeCode=offerers_models.VenueTypeCode.LIBRARY)
        offerers_factories.AccessibilityProviderFactory(
            venue=venue,
            externalAccessibilityId="old-slug",
            externalAccessibilityUrl="https://acceslibre.beta.gouv.fr/my/old-slug/",
        )
        data = self._get_current_data(venue)

        data["acceslibre_url"] = "https://acceslibre.beta.gouv.fr/my/new-slug/"

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)
        assert response.status_code == 303

        db.session.refresh(venue)
        assert venue.external_accessibility_id == "new-slug"
        assert venue.action_history[0].extraData == {
            "modified_info": {
                "accessibilityProvider.externalAccessibilityId": {"new_info": "new-slug", "old_info": "old-slug"},
                "accessibilityProvider.externalAccessibilityUrl": {
                    "new_info": "https://acceslibre.beta.gouv.fr/my/new-slug/",
                    "old_info": "https://acceslibre.beta.gouv.fr/my/old-slug/",
                },
            }
        }

    def test_update_venue_delete_accessibility_provider(self, authenticated_client):
        venue = offerers_factories.VenueFactory(venueTypeCode=offerers_models.VenueTypeCode.LIBRARY)
        offerers_factories.AccessibilityProviderFactory(
            venue=venue,
            externalAccessibilityId="mon-slug",
            externalAccessibilityUrl="https://acceslibre.beta.gouv.fr/erps/mon-slug/",
        )
        data = self._get_current_data(venue)

        data["acceslibre_url"] = None

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)
        assert response.status_code == 303
        db.session.refresh(venue)
        assert not venue.accessibilityProvider
        assert venue.action_history[0].extraData == {
            "modified_info": {
                "accessibilityProvider.externalAccessibilityId": {
                    "new_info": None,
                    "old_info": "mon-slug",
                },
                "accessibilityProvider.externalAccessibilityUrl": {
                    "new_info": None,
                    "old_info": "https://acceslibre.beta.gouv.fr/erps/mon-slug/",
                },
            }
        }

    def test_update_venue_accessibility_provider_id_bad_url(self, authenticated_client):
        venue = offerers_factories.VenueFactory(venueTypeCode=offerers_models.VenueTypeCode.LIBRARY)
        offerers_factories.AccessibilityProviderFactory(venue=venue, externalAccessibilityUrl="https://good.url")
        data = self._get_current_data(venue)

        data["acceslibre_url"] = "https://bad.url/"
        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)
        assert response.status_code == 400
        assert "Les données envoyées comportent des erreurs." in html_parser.extract_alert(response.data)
        db.session.refresh(venue)
        assert venue.accessibilityProvider.externalAccessibilityUrl == "https://good.url"

    def test_update_venue_accessibility_provider_id_empty_slug(self, authenticated_client):
        venue = offerers_factories.VenueFactory(venueTypeCode=offerers_models.VenueTypeCode.LIBRARY)
        offerers_factories.AccessibilityProviderFactory(
            venue=venue, externalAccessibilityUrl="https://acceslibre.beta.gouv.fr/erps/mon-slug/"
        )

        data = self._get_current_data(venue)
        data["acceslibre_url"] = "https://acceslibre.beta.gouv.fr/erps//"
        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 400
        assert "Les données envoyées comportent des erreurs." in html_parser.extract_alert(response.data)
        db.session.refresh(venue)
        assert venue.accessibilityProvider.externalAccessibilityUrl == "https://acceslibre.beta.gouv.fr/erps/mon-slug/"

    def test_update_venue_should_fail_when_add_accessibility_provider_if_not_open_to_public(self, authenticated_client):
        venue = offerers_factories.VenueFactory(
            venueTypeCode=offerers_models.VenueTypeCode.TRAVELING_CINEMA, isOpenToPublic=False
        )

        data = self._get_current_data(venue)
        data["acceslibre_url"] = "https://acceslibre.beta.gouv.fr/erps/mon-slug/"
        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 400
        assert "Les données envoyées comportent des erreurs." in html_parser.extract_alert(response.data)
        db.session.refresh(venue)
        assert venue.accessibilityProvider == None

    def test_update_venue_remove_accesslibre_url_when_becoming_non_permanent(self, authenticated_client):
        # Venue becoming none permanent, become close to public. Venue close to public does not have acceslibre sync
        venue = offerers_factories.VenueFactory(venueTypeCode=offerers_models.VenueTypeCode.LIBRARY)
        offerers_factories.AccessibilityProviderFactory(
            venue=venue,
            externalAccessibilityId="mon-slug",
            externalAccessibilityUrl="https://acceslibre.beta.gouv.fr/erps/mon-slug/",
        )
        data = self._get_current_data(venue)
        data["acceslibre_url"] = "https://acceslibre.beta.gouv.fr/erps/mon-nouveau-slug/"
        data["is_permanent"] = False

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303
        db.session.refresh(venue)
        assert not venue.accessibilityProvider
        assert venue.action_history[0].extraData == {
            "modified_info": {
                "accessibilityProvider.externalAccessibilityId": {
                    "new_info": None,
                    "old_info": "mon-slug",
                },
                "accessibilityProvider.externalAccessibilityUrl": {
                    "new_info": None,
                    "old_info": "https://acceslibre.beta.gouv.fr/erps/mon-slug/",
                },
                "isPermanent": {
                    "new_info": False,
                    "old_info": True,
                },
            }
        }

    @patch("pcapi.workers.match_acceslibre_job.match_acceslibre_job.delay")
    def test_update_venue_becomes_permanent_should_not_call_match_acceslibre_job(
        self, match_acceslibre_job, authenticated_client
    ):
        venue = offerers_factories.VenueFactory(isPermanent=False)
        data = self._get_current_data(venue)
        data["is_permanent"] = True

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303
        match_acceslibre_job.assert_not_called()

    @pytest.mark.settings(ACCESLIBRE_BACKEND="pcapi.connectors.acceslibre.AcceslibreBackend")
    def test_update_venue_unexisting_acceslibre_url_must_not_update_accessibility_provider(self, authenticated_client):
        venue = offerers_factories.VenueFactory(isPermanent=True)
        offerers_factories.AccessibilityProviderFactory(
            venue=venue,
            externalAccessibilityId="mon-slug",
            externalAccessibilityUrl="https://acceslibre.beta.gouv.fr/erps/mon-slug/",
        )
        data = self._get_current_data(venue)
        data["acceslibre_url"] = "https://acceslibre.beta.gouv.fr/erps/cette_url_n'existe_pas_chez_acceslibre/"

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 400
        assert "Les données envoyées comportent des erreurs." in html_parser.extract_alert(response.data)
        db.session.refresh(venue)
        assert venue.accessibilityProvider.externalAccessibilityId == "mon-slug"

    def test_update_venue_with_integrity_error(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        data = self._get_current_data(venue)

        with patch("pcapi.core.offerers.api.update_venue", side_effect=sa.exc.IntegrityError("test", "test", "test")):
            response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data, follow_redirects=True)

        assert response.status_code == 200  # after redirect
        assert (
            "Une erreur s'est produite : (builtins.str) test [SQL: test] [parameters: 'test']"
            in html_parser.extract_alert(response.data)
        )


class UpdateForFraudTest(PostEndpointHelper):
    endpoint = "backoffice_web.venue.update_for_fraud"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_set_rule(self, legit_user, authenticated_client):
        venue = offerers_factories.VenueFactory()

        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue.id,
            form={
                "confidence_level": offerers_models.OffererConfidenceLevel.WHITELIST.name,
                "comment": "Test",
            },
        )
        assert response.status_code == 303

        assert venue.confidenceLevel == offerers_models.OffererConfidenceLevel.WHITELIST
        assert len(venue.action_history) == 1
        action = venue.action_history[0]
        assert action.actionType == history_models.ActionType.FRAUD_INFO_MODIFIED
        assert action.authorUser == legit_user
        assert action.comment == "Test"
        assert action.extraData == {
            "modified_info": {
                "confidenceRule.confidenceLevel": {
                    "old_info": None,
                    "new_info": offerers_models.OffererConfidenceLevel.WHITELIST.name,
                }
            }
        }

    def test_update_rule(self, legit_user, authenticated_client):
        rule = offerers_factories.WhitelistedVenueConfidenceRuleFactory()
        venue = rule.venue

        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue.id,
            form={
                "confidence_level": offerers_models.OffererConfidenceLevel.MANUAL_REVIEW.name,
                "comment": "Test",
            },
        )
        assert response.status_code == 303

        assert venue.confidenceLevel == offerers_models.OffererConfidenceLevel.MANUAL_REVIEW
        assert len(venue.action_history) == 1
        action = venue.action_history[0]
        assert action.actionType == history_models.ActionType.FRAUD_INFO_MODIFIED
        assert action.authorUser == legit_user
        assert action.comment == "Test"
        assert action.extraData == {
            "modified_info": {
                "confidenceRule.confidenceLevel": {
                    "old_info": offerers_models.OffererConfidenceLevel.WHITELIST.name,
                    "new_info": offerers_models.OffererConfidenceLevel.MANUAL_REVIEW.name,
                }
            }
        }

    def test_remove_rule(self, legit_user, authenticated_client):
        rule = offerers_factories.ManualReviewVenueConfidenceRuleFactory()
        venue = rule.venue

        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue.id,
            form={
                "confidence_level": "",
                "comment": "Test",
            },
        )
        assert response.status_code == 303

        assert venue.confidenceLevel is None
        assert db.session.query(offerers_models.OffererConfidenceRule).count() == 0
        assert len(venue.action_history) == 1
        action = venue.action_history[0]
        assert action.actionType == history_models.ActionType.FRAUD_INFO_MODIFIED
        assert action.authorUser == legit_user
        assert action.comment == "Test"
        assert action.extraData == {
            "modified_info": {
                "confidenceRule.confidenceLevel": {
                    "old_info": offerers_models.OffererConfidenceLevel.MANUAL_REVIEW.name,
                    "new_info": None,
                }
            }
        }

    def test_update_nothing(self, legit_user, authenticated_client):
        rule = offerers_factories.ManualReviewVenueConfidenceRuleFactory()
        venue = rule.venue

        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue.id,
            form={
                "confidence_level": offerers_models.OffererConfidenceLevel.MANUAL_REVIEW.name,
                "comment": "",
            },
        )
        assert response.status_code == 303

        assert venue.confidenceLevel == offerers_models.OffererConfidenceLevel.MANUAL_REVIEW
        assert len(venue.action_history) == 0


class GetVenueHistoryTest(GetEndpointHelper):
    endpoint = "backoffice_web.venue.get_history"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # get session + user (1 query)
    # get history (1 query)
    expected_num_queries = 2

    class CommentButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY
        button_label = "Ajouter un commentaire"

        @property
        def path(self):
            venue = offerers_factories.VenueFactory()
            return url_for("backoffice_web.venue.get_history", venue_id=venue.id)

    def test_venue_history(self, authenticated_client, legit_user, pro_fraud_admin):
        venue = offerers_factories.VenueFactory()

        comment = "test comment"
        history_factories.ActionHistoryFactory(
            # displayed because legit_user has fraud permission
            actionType=history_models.ActionType.FRAUD_INFO_MODIFIED,
            actionDate=date_utils.get_naive_utc_now() - timedelta(days=2),
            authorUser=pro_fraud_admin,
            venue=venue,
            comment="Sous surveillance",
            extraData={
                "modified_info": {
                    "confidenceRule.confidenceLevel": {
                        "old_info": None,
                        "new_info": offerers_models.OffererConfidenceLevel.MANUAL_REVIEW.name,
                    },
                }
            },
        )
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.COMMENT,
            actionDate=date_utils.get_naive_utc_now() - timedelta(hours=3),
            authorUser=legit_user,
            venue=venue,
            comment=comment,
        )
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.INFO_MODIFIED,
            actionDate=date_utils.get_naive_utc_now() - timedelta(hours=2),
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
                    "openingHours.MONDAY.timespan": {
                        "old_info": "14:00-19:30",
                        "new_info": "10:00-13:00, 14:00-19:30",
                    },
                    "openingHours.TUESDAY.timespan": {
                        "old_info": "14:00-19:30",
                        "new_info": None,
                    },
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
        assert len(rows) == 3

        assert rows[0]["Type"] == "Modification des informations"
        assert "Informations modifiées : " in rows[0]["Commentaire"]
        assert "Activité principale : Autre → Librairie " in rows[0]["Commentaire"]
        assert "Site internet de contact : suppression de : https://old.website.com " in rows[0]["Commentaire"]
        assert "Conditions de retrait : ajout de : Come here!" in rows[0]["Commentaire"]
        assert "Accessibilité handicap visuel : Non → Oui" in rows[0]["Commentaire"]
        assert "Horaires du lundi : 14:00-19:30 → 10:00-13:00, 14:00-19:30" in rows[0]["Commentaire"]
        assert "Horaires du mardi : suppression de : 14:00-19:30" in rows[0]["Commentaire"]
        assert rows[0]["Auteur"] == legit_user.full_name

        assert rows[1]["Type"] == "Commentaire interne"
        assert rows[1]["Commentaire"] == comment
        assert rows[1]["Auteur"] == legit_user.full_name

        assert rows[2]["Type"] == "Fraude et Conformité"
        assert (
            rows[2]["Commentaire"]
            == "Sous surveillance Informations modifiées : Validation des offres : ajout de : Revue manuelle"
        )
        assert rows[2]["Auteur"] == pro_fraud_admin.full_name

    def test_venue_history_for_regularisation(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        destination_venue = offerers_factories.VenueFactory()

        history_factories.ActionHistoryFactory(
            venueId=venue.id,
            actionType=history_models.ActionType.VENUE_REGULARIZATION,
            extraData={"destination_venue_id": destination_venue.id},
            comment=None,
        )
        history_factories.ActionHistoryFactory(
            venueId=venue.id, actionType=history_models.ActionType.VENUE_SOFT_DELETED, comment=None
        )
        history_factories.ActionHistoryFactory(
            venueId=destination_venue.id,
            actionType=history_models.ActionType.VENUE_REGULARIZATION,
            extraData={
                "origin_venue_id": venue.id,
                "modified_info": {"isPermanent": {"new_info": True}},
            },
            comment=None,
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

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2

        assert rows[0]["Type"] == "Suppression réversible"
        assert rows[0]["Commentaire"] == ""

        assert rows[1]["Type"] == "Régularisation des partenaires culturels"
        assert (
            rows[1]["Commentaire"]
            == f"Tous les éléments ont été transférés vers le partenaire culturel {destination_venue.id}"
        )

        url = url_for(self.endpoint, venue_id=destination_venue.id)

        # if venue is not removed from the current session, any get
        # query won't be executed because of this specific testing
        # environment. this would tamper the real database queries
        # count.
        db.session.expire(venue)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1

        assert rows[0]["Type"] == "Régularisation des partenaires culturels"
        assert rows[0]["Commentaire"] == "Informations modifiées : Permanent : ajout de : Oui"

    def test_venue_history_without_fraud_permission(self, client, read_only_bo_user):
        venue = offerers_factories.VenueFactory()
        history_factories.ActionHistoryFactory(actionType=history_models.ActionType.COMMENT, venue=venue)
        history_factories.ActionHistoryFactory(actionType=history_models.ActionType.FRAUD_INFO_MODIFIED, venue=venue)

        url = url_for(self.endpoint, venue_id=venue.id)

        db.session.expire(venue)

        auth_client = client.with_bo_session_auth(read_only_bo_user)
        with assert_num_queries(self.expected_num_queries):
            response = auth_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["Type"] == "Commentaire interne"

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

        expected_url = url_for("backoffice_web.venue.get", venue_id=venue.id)
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


class GetVenueCollectiveDmsApplicationsTest(GetEndpointHelper):
    endpoint = "backoffice_web.venue.get_collective_dms_applications"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # get session + user (1 query)
    # get applications (1 query)
    expected_num_queries = 2

    def test_venue_with_dms_adage_application(self, authenticated_client):
        venue = offerers_factories.VenueFactory(siret="1234567891234")

        url = url_for(self.endpoint, venue_id=venue.id)

        # if venue is not removed from the current session, any get
        # query won't be executed because of this specific testing
        # environment. this would tamper the real database queries
        # count.
        db.session.expire(venue)

        accepted_application = educational_factories.CollectiveDmsApplicationFactory(
            venue=venue, depositDate=date_utils.get_naive_utc_now() - timedelta(days=10), state="accepte"
        )
        expired_application = educational_factories.CollectiveDmsApplicationFactory(
            venue=venue, depositDate=date_utils.get_naive_utc_now() - timedelta(days=5), state="refuse"
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert rows[0]["ID"] == str(expired_application.application)
        assert (
            f"https://demarche.numerique.gouv.fr/procedures/{expired_application.procedure}/dossiers/{expired_application.application}"
            in str(response.data)
        )
        assert rows[0]["Date de dépôt"] == expired_application.depositDate.strftime("%d/%m/%Y")
        assert rows[0]["État"] == "Refusé"
        assert rows[0]["Date de dernière mise à jour"] == expired_application.lastChangeDate.strftime("%d/%m/%Y")
        assert rows[1]["ID"] == str(accepted_application.application)
        assert (
            f"https://demarche.numerique.gouv.fr/procedures/{accepted_application.procedure}/dossiers/{accepted_application.application}"
            in str(response.data)
        )
        assert rows[1]["Date de dépôt"] == accepted_application.depositDate.strftime("%d/%m/%Y")
        assert rows[1]["État"] == "Accepté"
        assert rows[1]["Date de dernière mise à jour"] == accepted_application.lastChangeDate.strftime("%d/%m/%Y")

    def test_venue_with_no_dms_adage_application(self, authenticated_client):
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


class GetBatchEditVenuesFormTest(PostEndpointHelper):
    endpoint = "backoffice_web.venue.get_batch_edit_venues_form"
    endpoint_kwargs = {"object_ids": "1,2"}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_get_empty_batch_edit_venues_form(self, legit_user, authenticated_client):
        response = authenticated_client.get(url_for(self.endpoint))
        response = self.post_to_endpoint(
            authenticated_client,
            form={"object_ids": ""},
            expected_num_queries=1,  # session
        )
        assert response.status_code == 200

    def test_get_edit_batch_venues_form_with_ids(self, legit_user, authenticated_client, criteria):
        venues = [
            offerers_factories.VenueFactory(criteria=criteria[:2]),
            offerers_factories.VenueFactory(criteria=criteria[1:]),
        ]

        response = self.post_to_endpoint(
            authenticated_client,
            form={"object_ids": ",".join(str(venue.id) for venue in venues)},
            expected_num_queries=2,  # session + criteria
        )
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
        assert response.status_code == 200
        assert len(response.data) == 0

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
        assert response.status_code == 200
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
            offerers_factories.VenueFactory(
                # Ensure that inconsistency in database does not prevent from updating tags and/or permanent status
                managingOfferer__siren="111111111",
                siret="22222222233333",
                criteria=criteria[:2],
                isPermanent=set_permanent,
            ),
            offerers_factories.VenueFactory(criteria=criteria[1:], isPermanent=not set_permanent),
        ]

        form_data = {
            "object_ids": ",".join(str(venue.id) for venue in venues),
            "criteria": [criteria[0].id, new_criterion.id],
            "all_permanent": "on" if set_permanent else "",
            "all_not_permanent": "" if set_permanent else "on",
        }

        response = self.post_to_endpoint(authenticated_client, form=form_data)
        assert response.status_code == 200

        for venue in venues:
            cells = html_parser.extract_plain_row(response.data, id=f"venue-row-{venue.id}")
            assert cells[1] == str(venue.id)

        assert set(venues[0].criteria) == {criteria[0], new_criterion}  # 1 kept, 1 removed, 1 added
        assert venues[0].isPermanent is set_permanent

        assert set(venues[1].criteria) == {criteria[0], criteria[2], new_criterion}  # 1 kept, 1 added
        assert venues[1].isPermanent is set_permanent

        mock_async_index_venue_ids.assert_called_once()

        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.authorUserId == legit_user.id
        assert action.venue == venues[1]
        assert action.extraData["modified_info"] == {
            "isPermanent": {"old_info": not set_permanent, "new_info": set_permanent}
        }

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
        assert response.status_code == 200

        cells = html_parser.extract_plain_row(response.data, id=f"venue-row-{venues[0].id}")
        assert cells[1] == str(venues[0].id)

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
        assert response.status_code == 200

        cells = html_parser.extract_plain_row(response.data, id=f"venue-row-{venue.id}")
        assert cells[1] == str(venue.id)

        assert venue.isPermanent is set_permanent

        assert len(mails_testing.outbox) == expected_mail_number
        if expected_mail_number > 0:
            # check that email is sent when venue is set to permanent and has no image
            assert mails_testing.outbox[0]["To"] == venue.bookingEmail
            assert mails_testing.outbox[0]["template"] == TransactionalEmail.VENUE_NEEDS_PICTURE.value.__dict__
            assert mails_testing.outbox[0]["params"]["VENUE_NAME"] == venue.common_name
            assert mails_testing.outbox[0]["params"]["VENUE_FORM_URL"] == urls.build_pc_pro_venue_link(venue)

        mock_async_index_venue_ids.assert_called_once()

        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.authorUserId == legit_user.id
        assert action.venue == venue
        assert action.extraData["modified_info"] == {
            "isPermanent": {"old_info": not set_permanent, "new_info": set_permanent}
        }


class GetRemovePricingPointFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.venue.get_remove_pricing_point_form"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT

    def test_get_remove_pricing_point_form(self, authenticated_client, venue_with_no_siret):
        bookings_factories.ReimbursedBookingFactory(stock__price=123.4, stock__offer__venue=venue_with_no_siret)

        response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_with_no_siret.id))

        assert response.status_code == 200
        content = html_parser.content_as_text(response.data)
        assert f"Partenaire culturel : {venue_with_no_siret.name}" in content
        assert f"Venue ID : {venue_with_no_siret.id}" in content
        assert "SIRET : Pas de SIRET" in content
        assert "CA de l'année : 123,40 €" in content
        assert f"Point de valorisation : {venue_with_no_siret.current_pricing_point.name}" in content
        assert f"SIRET de valorisation : {venue_with_no_siret.current_pricing_point.siret}" in content

    def test_venue_with_siret(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.VenuePricingPointLinkFactory(
            venue=venue,
            pricingPoint=offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer),
            timespan=[date_utils.get_naive_utc_now() - timedelta(days=7), None],
        )

        response = authenticated_client.get(url_for(self.endpoint, venue_id=venue.id))

        assert response.status_code == 400
        assert (
            html_parser.extract_alert(response.data)
            == "Vous ne pouvez supprimer le point de valorisation d'un partenaire culturel avec SIRET"
        )

    def test_venue_with_no_pricing_point(self, authenticated_client):
        venue = offerers_factories.VenueWithoutSiretFactory()

        response = authenticated_client.get(url_for(self.endpoint, venue_id=venue.id))

        assert response.status_code == 400
        assert (
            html_parser.extract_alert(response.data) == "Ce partenaire culturel n'a pas de point de valorisation actif"
        )

    def test_venue_with_high_yearly_revenue(self, authenticated_client, venue_with_no_siret):
        rich_beneficiary = users_factories.BeneficiaryFactory(deposit__amount=25_000)
        bookings_factories.ReimbursedBookingFactory(
            user=rich_beneficiary, stock__price=10800, stock__offer__venue=venue_with_no_siret
        )

        response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_with_no_siret.id))

        assert response.status_code == 400
        assert (
            html_parser.extract_alert(response.data)
            == "Ce partenaire culturel a un chiffre d'affaires de l'année élevé : 10800.00"
        )


class GetSetPricingPointFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.venue.get_set_pricing_point_form"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT
    # +1 session + user
    # +1 venue and venues from the same offerer
    expected_num_queries = 2

    def get_set_pricing_point_form(self, authenticated_client):
        venue = offerers_factories.VenueWithoutSiretFactory()

        url = url_for(self.endpoint, venue_id=venue.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200


class SetPricingPointTest(PostEndpointHelper):
    endpoint = "backoffice_web.venue.set_pricing_point"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT
    # +1 session + user
    # +1 venue and venues from the same offerer
    # +1 pricing point validation
    # +1 check if the venue already has a link
    # +3 set pricing point
    expected_num_queries = 7

    def test_set_pricing_point(self, authenticated_client):
        venue_with_no_siret = offerers_factories.VenueWithoutSiretFactory()
        venue_with_siret = offerers_factories.VenueFactory(
            managingOfferer=venue_with_no_siret.managingOfferer,
        )
        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue_with_no_siret.id,
            form={
                "new_pricing_point": venue_with_siret.id,
            },
            expected_num_queries=self.expected_num_queries,
        )
        assert response.status_code == 303
        assert venue_with_no_siret.current_pricing_point is venue_with_siret
        redirected_response = authenticated_client.get(response.headers["location"])
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Ce partenaire culturel a été lié à un point de valorisation"
        )

    def test_set_pricing_point_as_self(self, authenticated_client):
        venue_with_siret = offerers_factories.VenueFactory(pricing_point=None)
        offerers_factories.VenueWithoutSiretFactory(
            managingOfferer=venue_with_siret.managingOfferer, pricing_point=venue_with_siret
        )
        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue_with_siret.id,
            form={"new_pricing_point": venue_with_siret.id},
            follow_redirects=True,
        )
        assert response.status_code == 200  # after redirect
        assert venue_with_siret.current_pricing_point is venue_with_siret
        assert html_parser.extract_alert(response.data) == "Ce partenaire culturel a été lié à un point de valorisation"

    def test_venue_not_found(self, authenticated_client):
        venue_with_siret = offerers_factories.VenueFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            venue_id="0",
            form={
                "new_pricing_point": venue_with_siret.id,
            },
        )
        assert response.status_code == 404

    def test_pricing_point_not_found(self, authenticated_client):
        venue_with_no_siret = offerers_factories.VenueWithoutSiretFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue_with_no_siret.id,
            form={
                "new_pricing_point": "0",
            },
        )
        assert response.status_code == 303
        assert venue_with_no_siret.current_pricing_point is None
        redirected_response = authenticated_client.get(response.headers["location"])
        assert "Les données envoyées comportent des erreurs." in html_parser.extract_alert(redirected_response.data)

    def test_pricing_point_in_other_offerer(self, authenticated_client):
        venue_with_no_siret = offerers_factories.VenueWithoutSiretFactory()
        venue_with_siret = offerers_factories.VenueFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue_with_no_siret.id,
            form={
                "new_pricing_point": venue_with_siret.id,
            },
        )
        assert response.status_code == 303
        assert venue_with_no_siret.current_pricing_point is None
        redirected_response = authenticated_client.get(response.headers["location"])
        assert "Les données envoyées comportent des erreurs." in html_parser.extract_alert(redirected_response.data)

    def test_venue_already_has_a_pricing_point(self, authenticated_client, venue_with_no_siret):
        previous_pricing_point = venue_with_no_siret.current_pricing_point
        venue_with_siret = offerers_factories.VenueFactory(
            managingOfferer=venue_with_no_siret.managingOfferer,
        )
        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue_with_no_siret.id,
            form={
                "new_pricing_point": venue_with_siret.id,
            },
        )
        assert response.status_code == 303
        assert venue_with_no_siret.current_pricing_point is previous_pricing_point
        redirected_response = authenticated_client.get(response.headers["location"])
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Ce partenaire culturel est déjà lié à un point de valorisation"
        )

    def test_venue_has_siret(self, authenticated_client):
        venue_with_no_siret = offerers_factories.VenueFactory()
        venue_with_siret = offerers_factories.VenueFactory(
            managingOfferer=venue_with_no_siret.managingOfferer,
        )
        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue_with_no_siret.id,
            form={
                "new_pricing_point": venue_with_siret.id,
            },
        )
        assert response.status_code == 303
        assert venue_with_no_siret.current_pricing_point is None
        redirected_response = authenticated_client.get(response.headers["location"])
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Ce partenaire culturel a un SIRET, vous ne pouvez donc pas choisir un autre partenaire culturel pour le calcul du barème de remboursement."
        )


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
        assert venue_with_no_siret.pricing_point_links[0].timespan.upper <= date_utils.get_naive_utc_now()

        action = db.session.query(history_models.ActionHistory).one()
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
            timespan=[date_utils.get_naive_utc_now() - timedelta(days=7), None],
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
            == "Vous ne pouvez supprimer le point de valorisation d'un partenaire culturel avec SIRET"
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
        assert (
            html_parser.extract_alert(response.data) == "Ce partenaire culturel n'a pas de point de valorisation actif"
        )

    def test_venue_with_high_yearly_revenue(self, authenticated_client, venue_with_no_siret):
        rich_beneficiary = users_factories.BeneficiaryFactory(deposit__amount=25_000)
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
        assert (
            html_parser.extract_alert(response.data)
            == "Ce partenaire culturel a un chiffre d'affaires de l'année élevé : 10800.00"
        )

    def test_override_yearly_revenue(self, authenticated_client, venue_with_no_siret):
        rich_beneficiary = users_factories.BeneficiaryFactory(deposit__amount=25_000)
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
        assert venue_with_no_siret.pricing_point_links[0].timespan.upper <= date_utils.get_naive_utc_now()


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
        assert f"Entité juridique : {offerer.name}" in content
        assert f"Offerer ID : {offerer.id}" in content
        assert f"Partenaire culturel : {venue.name}" in content
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

        assert response.status_code == 200
        assert html_parser.extract_alert(response.data) == "Ce partenaire culturel n'a pas de SIRET"

    def test_no_other_venue_with_siret(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.VenueWithoutSiretFactory(managingOfferer=venue.managingOfferer)

        response = authenticated_client.get(url_for(self.endpoint, venue_id=venue.id))

        assert response.status_code == 200
        assert (
            html_parser.extract_alert(response.data)
            == "L'entité juridique gérant ce partenaire culturel n'a pas d'autre partenaire culturel avec SIRET"
        )

    def test_venue_with_high_yearly_revenue(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        rich_beneficiary = users_factories.BeneficiaryFactory(deposit__amount=25_000)
        bookings_factories.ReimbursedBookingFactory(
            user=rich_beneficiary, stock__price=10800, stock__offer__venue=venue
        )

        response = authenticated_client.get(url_for(self.endpoint, venue_id=venue.id))

        assert response.status_code == 200
        html_parser.assert_no_alert(response.data)

        content = html_parser.content_as_text(response.data)
        assert "CA de l'année : 10 800,00 €" in content

    @pytest.mark.parametrize(
        "start_date, end_date",
        [
            (date_utils.get_naive_utc_now() - timedelta(days=10), None),
            (date_utils.get_naive_utc_now() - timedelta(days=10), date_utils.get_naive_utc_now() + timedelta(days=10)),
            (date_utils.get_naive_utc_now() + timedelta(days=10), None),
        ],
    )
    def test_venue_custom_reimbursement_rule(self, authenticated_client, start_date, end_date):
        venue = offerers_factories.VenueFactory()
        offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        finance_factories.CustomReimbursementRuleFactory(venue=venue, timespan=(start_date, end_date))

        response = authenticated_client.get(url_for(self.endpoint, venue_id=venue.id))

        assert response.status_code == 200
        assert (
            html_parser.extract_alert(response.data)
            == "Ce partenaire culturel est associé à au moins un tarif dérogatoire actif ou futur. Confirmer l'action mettra automatiquement fin à ce tarif dérogatoire."
        )


class RemoveSiretTest(PostEndpointHelper):
    endpoint = "backoffice_web.venue.remove_siret"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.MOVE_SIRET

    def test_remove_siret(self, legit_user, authenticated_client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.VenuePricingPointLinkFactory(venue=venue, pricingPoint=venue)
        other_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        offerers_factories.VenuePricingPointLinkFactory(venue=other_venue, pricingPoint=venue)
        target_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)

        old_siret = venue.siret

        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue.id,
            form={"override_revenue_check": False, "comment": "test", "new_pricing_point": target_venue.id},
        )
        assert response.status_code == 200

        assert venue.siret is None
        assert venue.comment == "test"
        assert venue.pricing_point_links[0].timespan.upper <= date_utils.get_naive_utc_now()
        assert venue.current_pricing_point == target_venue

        action = db.session.query(history_models.ActionHistory).filter_by(venueId=venue.id).one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.offererId == venue.managingOffererId
        assert action.comment == "test"
        assert action.extraData["modified_info"] == {
            "siret": {"old_info": old_siret, "new_info": None},
            "pricingPointSiret": {"old_info": old_siret, "new_info": target_venue.siret},
        }

        assert other_venue.pricing_point_links[0].timespan.upper <= date_utils.get_naive_utc_now()
        assert other_venue.current_pricing_point is None

        other_action = db.session.query(history_models.ActionHistory).filter_by(venueId=other_venue.id).one()
        assert other_action.actionType == history_models.ActionType.INFO_MODIFIED
        assert other_action.actionDate is not None
        assert other_action.authorUserId == legit_user.id
        assert other_action.offererId == venue.managingOffererId
        assert other_action.comment == "test"
        assert other_action.extraData["modified_info"] == {
            "pricingPointSiret": {"old_info": old_siret, "new_info": None},
        }

    @pytest.mark.parametrize(
        "start_date, end_date, update",
        [
            (date_utils.get_naive_utc_now() - timedelta(days=10), None, True),
            (
                date_utils.get_naive_utc_now() - timedelta(days=10),
                date_utils.get_naive_utc_now() + timedelta(days=10),
                True,
            ),
            (date_utils.get_naive_utc_now() + timedelta(days=10), None, False),
        ],
    )
    def test_venue_with_custom_reimbursement_rule(self, authenticated_client, start_date, end_date, update):
        venue = offerers_factories.VenueFactory()
        target_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        finance_factories.CustomReimbursementRuleFactory(
            venue=venue,
            timespan=(start_date, end_date),
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

        assert response.status_code == 200
        rules = db.session.query(finance_models.CustomReimbursementRule).all()
        assert bool(rules) == update
        if update:
            assert len(rules) == 1
            assert rules[0].timespan.upper != end_date
            assert rules[0].timespan.upper < date_utils.get_naive_utc_now() + timedelta(days=1)

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

        assert response.status_code == 200
        assert html_parser.extract_alert(response.data) == "Ce partenaire culturel n'a pas de SIRET"

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

        assert response.status_code == 200
        assert html_parser.extract_warnings(response.data) == ["Not a valid choice."]

    def test_venue_with_high_yearly_revenue(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        target_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        rich_beneficiary = users_factories.BeneficiaryFactory(deposit__amount=25_000)
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

        assert response.status_code == 200
        assert (
            html_parser.extract_alert(response.data)
            == "Ce partenaire culturel a un chiffre d'affaires de l'année élevé : 10800.00"
        )

    def test_override_yearly_revenue(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.VenuePricingPointLinkFactory(venue=venue, pricingPoint=venue)
        target_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        rich_beneficiary = users_factories.BeneficiaryFactory(deposit__amount=25_000)
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

        assert response.status_code == 200
        assert venue.siret is None
        assert venue.current_pricing_point == target_venue


class PostToggleVenueProviderIsActiveTest(PostEndpointHelper):
    endpoint = "backoffice_web.venue.toggle_venue_provider_is_active"
    endpoint_kwargs = {"venue_id": 1, "provider_id": 1}
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT

    @pytest.mark.parametrize("is_active,verb", [(True, "mise en pause"), (False, "réactivée")])
    def test_toggle_venue_provider_is_active(self, authenticated_client, legit_user, is_active, verb):
        venue_provider = providers_factories.VenueProviderFactory(provider__name="Test provider", isActive=is_active)

        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue_provider.venue.id,
            provider_id=venue_provider.provider.id,
        )
        assert response.status_code == 303

        db.session.refresh(venue_provider)
        assert venue_provider.isActive is not is_active

        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.LINK_VENUE_PROVIDER_UPDATED
        assert action.authorUserId == legit_user.id
        assert action.venueId == venue_provider.venue.id
        assert action.extraData["provider_id"] == venue_provider.provider.id
        assert action.extraData["provider_name"] == "Test provider"
        assert action.extraData["modified_info"] == {"isActive": {"old_info": is_active, "new_info": not is_active}}

        response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(response.data)
            == f"La synchronisation du partenaire culturel avec le provider a été {verb}."
        )

    def test_toggle_wrong_provider(self, authenticated_client):
        venue_provider = providers_factories.VenueProviderFactory()

        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue_provider.venue.id,
            provider_id=0,
        )
        assert response.status_code == 404
        assert (
            db.session.query(providers_models.VenueProvider)
            .filter(providers_models.VenueProvider.id == venue_provider.id)
            .one()
        )
        assert db.session.query(history_models.ActionHistory).count() == 0


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
        assert (
            db.session.query(providers_models.VenueProvider)
            .filter(providers_models.VenueProvider.id == venue_provider.id)
            .count()
            == 0
        )
        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.LINK_VENUE_PROVIDER_DELETED
        assert action.authorUserId == legit_user.id
        assert action.venueId == venue_id
        assert action.extraData["provider_id"] == provider_id
        assert action.extraData["provider_name"] == "Test provider"
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue_provider.venue.id)

        response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(response.data)
            == "Le lien entre le partenaire culturel et le provider a été supprimé."
        )

    def test_delete_venue_wrong_provider(self, authenticated_client):
        venue_provider = providers_factories.VenueProviderFactory()

        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue_provider.venue.id,
            provider_id=0,
        )
        assert response.status_code == 404
        assert (
            db.session.query(providers_models.VenueProvider)
            .filter(providers_models.VenueProvider.id == venue_provider.id)
            .count()
            == 1
        )
        assert db.session.query(history_models.ActionHistory).count() == 0

    def test_delete_venue_allocine_provider(self, authenticated_client):
        venue_provider = providers_factories.AllocineVenueProviderFactory()

        response = self.post_to_endpoint(
            authenticated_client,
            venue_id=venue_provider.venue.id,
            provider_id=venue_provider.provider.id,
        )
        assert response.status_code == 303
        assert (
            db.session.query(providers_models.VenueProvider)
            .filter(providers_models.VenueProvider.id == venue_provider.id)
            .count()
            == 1
        )
        assert db.session.query(history_models.ActionHistory).count() == 0
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue_provider.venue.id)

        response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(response.data)
            == "Impossible de supprimer le lien entre le partenaire culturel et Allociné."
        )


class GetEntrepriseInfoTest(GetEndpointHelper):
    endpoint = "backoffice_web.venue.get_entreprise_info"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTREPRISE_INFO

    # get session + user (1 query)
    # get venue (1 query)
    expected_num_queries = 2

    def test_venue_entreprise_info(self, authenticated_client):
        venue = offerers_factories.VenueFactory(siret="12345678200010")
        url = url_for(self.endpoint, venue_id=venue.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        # Values come from TestingBackend, check display
        sirene_content = html_parser.extract_cards_text(response.data)[0]
        assert "Nom : MINISTERE DE LA CULTURE" in sirene_content
        assert "Adresse : 3 RUE DE VALOIS" in sirene_content
        assert "Code postal : 75001" in sirene_content
        assert "Ville : PARIS" in sirene_content
        assert "SIRET actif : Oui" in sirene_content
        assert "Diffusible : Oui" in sirene_content
        assert "Code APE : 9003A" in sirene_content
        assert "Activité principale : Création artistique relevant des arts plastiques" in sirene_content

    def test_siret_not_found(self, authenticated_client):
        venue = offerers_factories.VenueFactory(siret="00000000000018")
        url = url_for(self.endpoint, venue_id=venue.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries + 1):  # + rollback
            response = authenticated_client.get(url)
            assert response.status_code == 200

        # Values come from TestingBackend, check display
        sirene_content = html_parser.extract_cards_text(response.data)[0]
        assert (
            "Ce SIRET est inconnu dans la base de données Sirene, y compris dans les non-diffusibles" in sirene_content
        )

    def test_venue_not_found(self, authenticated_client):
        url = url_for(self.endpoint, venue_id=1)

        with assert_num_queries(self.expected_num_queries + 1):  # + rollback
            response = authenticated_client.get(url)
            assert response.status_code == 404

    def test_venue_without_siret(self, authenticated_client):
        venue = offerers_factories.VenueWithoutSiretFactory()
        url = url_for(self.endpoint, venue_id=venue.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries + 1):  # + rollback
            response = authenticated_client.get(url)
            assert response.status_code == 404

    def test_venue_with_invalid_siret(self, authenticated_client):
        venue = offerers_factories.VenueFactory(siret="22222222222222")
        url = url_for(self.endpoint, venue_id=venue.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries + 1):  # + rollback
            response = authenticated_client.get(url)
            assert response.status_code == 200

        sirene_content = html_parser.extract_cards_text(response.data)[0]
        assert (
            "Erreur Le format du numéro SIRET est détecté comme invalide, nous ne pouvons pas récupérer de données sur l'établissement."
            in sirene_content
        )
