from datetime import datetime
from datetime import timedelta
from decimal import Decimal
import json
from operator import attrgetter
from unittest.mock import patch

from flask import url_for
import pytest

from pcapi.connectors import api_adresse
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.criteria import models as criteria_models
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import factories as finance_factories
from pcapi.core.geography import models as geography_models
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
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users.backoffice import api as backoffice_api
from pcapi.models import db
from pcapi.routes.backoffice.pro.forms import TypeOptions
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
    return venue


@pytest.fixture(scope="function", name="venue_with_no_siret")
def venue_with_no_siret_fixture(offerer) -> offerers_models.Venue:
    venue = offerers_factories.VirtualVenueFactory(
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
    expected_num_queries = 3

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
        assert "Région : Île-de-France " in response_text
        assert f"Ville : {venue.city} " in response_text
        assert f"Code postal : {venue.postalCode} " in response_text
        assert f"Email : {venue.bookingEmail} " in response_text
        assert f"Numéro de téléphone : {venue.contact.phone_number} " in response_text
        assert "Peut créer une offre EAC : Non" in response_text
        assert "Cartographié sur ADAGE : Non" in response_text
        assert "ID ADAGE" not in response_text
        assert "Site web : https://www.example.com" in response_text
        assert f"Activité principale : {venue.venueTypeCode.value}" in response_text
        assert f"Label : {venue.venueLabel.label} " in response_text
        assert "Type de lieu" not in response_text
        assert f"Structure : {venue.managingOfferer.name}" in response_text
        assert "Site web : https://www.example.com" in response_text
        assert "Validation des offres : Suivre les règles" in response_text

        badges = html_parser.extract(response.data, tag="span", class_="badge")
        assert "Lieu" in badges
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

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue.id))
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert f"Email : {venue.bookingEmail}" in response_text
        assert "Numéro de téléphone :" not in response_text

    def test_get_venue_with_provider(self, authenticated_client, random_venue):
        venue_provider = providers_factories.AllocineVenueProviderFactory(
            venue=random_venue,
            lastSyncDate=datetime(2024, 1, 5, 12, 0),
        )
        venue_id = random_venue.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert "Provider : Allociné" in content
        assert "Dernière synchronisation : 05/01/2024 à 13h00" in content
        assert f"/pro/venue/{venue_id}/delete/{venue_provider.provider.id}".encode() not in response.data

    def test_get_venue_with_provider_not_allocine(self, authenticated_client, random_venue):
        venue_provider = providers_factories.VenueProviderFactory(venue=random_venue)
        venue_id = random_venue.id

        response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
        assert response.status_code == 200
        assert f"/pro/venue/{venue_id}/provider/{venue_provider.provider.id}/delete".encode() in response.data

    def test_display_fully_sync_provider_button(self, authenticated_client, random_venue):
        provider = providers_factories.APIProviderFactory()
        providers_factories.AllocineVenueProviderFactory(
            venue=random_venue,
            lastSyncDate=datetime.utcnow() - timedelta(hours=4),
            isActive=True,
            provider=provider,
        )
        venue_id = random_venue.id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        buttons = html_parser.extract(response.data, tag="button")
        assert "Resynchroniser les offres" in buttons

    def test_hide_fully_sync_provider_button(self, authenticated_client, random_venue):
        provider = providers_factories.APIProviderFactory(name="Praxiel")
        provider = providers_factories.AllocineVenueProviderFactory(
            venue=random_venue,
            lastSyncDate=datetime.utcnow() - timedelta(hours=4),
            isActive=True,
            provider=provider,
        )
        venue_id = random_venue.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        buttons = html_parser.extract(response.data, tag="button")
        assert "Resynchroniser les offres" not in buttons

    def test_get_virtual_venue(self, authenticated_client):
        venue = offerers_factories.VirtualVenueFactory(managingOfferer__allowedOnAdage=True)

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
        assert "Peut créer une offre EAC : Oui" in response_text
        assert "Cartographié sur ADAGE : Non" in response_text
        assert "ID ADAGE" not in response_text
        assert "Site web : https://my.website.com" in response_text

        badges = html_parser.extract(response.data, tag="span", class_="badge")
        assert "Lieu" in badges
        assert "Suspendu" not in badges

    @pytest.mark.parametrize(
        "has_new_nav,has_old_nav",
        [
            (True, True),
            (True, False),
            (False, True),
            (False, False),
        ],
    )
    def test_get_venue_with_new_nav_badges(self, authenticated_client, venue, has_new_nav, has_old_nav):
        if has_new_nav:
            user_with_new_nav = users_factories.ProFactory()
            offerers_factories.UserOffererFactory(user=user_with_new_nav, offerer=venue.managingOfferer)
            users_factories.UserProNewNavStateFactory(user=user_with_new_nav, newNavDate=datetime.utcnow())
        if has_old_nav:
            user_with_old_nav = users_factories.ProFactory()
            offerers_factories.UserOffererFactory(user=user_with_old_nav, offerer=venue.managingOfferer)

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

        badges = html_parser.extract(response.data, tag="span", class_="badge")
        assert "Lieu" in badges
        assert "Suspendu" not in badges

        if has_new_nav:
            assert "Nouvelle interface" in badges
        if has_old_nav:
            assert "Ancienne interface" in badges

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
            (offerers_factories.WhitelistedOffererConfidenceRuleFactory, "Validation auto (structure)"),
            (offerers_factories.ManualReviewOffererConfidenceRuleFactory, "Revue manuelle (structure)"),
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


class GetVenueStatsDataTest:
    def test_get_stats_data(
        self,
        venue_with_accepted_bank_account,
        offerer_active_individual_offers,
        offerer_inactive_individual_offers,
        offerer_active_collective_offers,
        offerer_inactive_collective_offers,
    ):
        venue_id = venue_with_accepted_bank_account.id

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
    # get venue with pricing point (1 query)
    # get total revenue (1 query)
    # get venue stats (6 query)
    expected_num_queries = 10

    def test_get_venue_with_no_siret(self, authenticated_client, venue_with_no_siret):
        venue_id = venue_with_no_siret.id
        url = url_for(self.endpoint, venue_id=venue_id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        cards_content = html_parser.extract_cards_text(response.data)
        pricing_point = venue_with_no_siret.pricing_point_links[0].pricingPoint
        assert venue_with_no_siret.siret is None
        assert f"Point de valorisation : {pricing_point.name}" in cards_content[2]

    def test_get_venue_with_no_bank_account(self, authenticated_client):
        venue = offerers_factories.VenueFactory(pricing_point="self")
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue.id))
            assert response.status_code == 200

        cards_content = html_parser.extract_cards_text(response.data)
        assert cards_content[2].endswith("Compte bancaire :")

    def test_get_venue_with_bank_account(self, authenticated_client):
        bank_account = finance_factories.BankAccountFactory()
        venue = offerers_factories.VenueFactory(pricing_point="self")
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue, bankAccount=bank_account, timespan=(datetime.utcnow() - timedelta(days=1),)
        )
        url = url_for(self.endpoint, venue_id=venue.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        cards_content = html_parser.extract_cards_text(response.data)
        assert (
            f"Compte bancaire : {bank_account.label} ({(datetime.utcnow() - timedelta(days=1)).strftime('%d/%m/%Y')})"
            in cards_content[2]
        )

    def test_get_stats(self, authenticated_client, venue):
        booking = bookings_factories.BookingFactory(stock__offer__venue=venue)
        url = url_for(self.endpoint, venue_id=venue.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        # cast to integer to avoid errors due to amount formatting
        assert str(int(booking.amount)) in response.data.decode("utf-8")

    def test_venue_total_revenue(
        self,
        authenticated_client,
        venue_with_accepted_bank_account,
        individual_offerer_bookings,
        collective_venue_booking,
    ):
        venue_id = venue_with_accepted_bank_account.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        assert "72,00 € de CA" in html_parser.extract_cards_text(response.data)[0]

    def test_venue_total_revenue_individual_bookings_only(
        self,
        authenticated_client,
        venue_with_accepted_bank_account,
        individual_offerer_bookings,
    ):
        venue_id = venue_with_accepted_bank_account.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        assert "30,00 € de CA" in html_parser.extract_cards_text(response.data)[0]

    def test_venue_total_revenue_collective_bookings_only(
        self, authenticated_client, venue_with_accepted_bank_account, collective_venue_booking
    ):
        venue_id = venue_with_accepted_bank_account.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        assert "42,00 € de CA" in html_parser.extract_cards_text(response.data)[0]

    def test_venue_total_revenue_no_booking(self, authenticated_client, venue_with_accepted_bank_account):
        venue_id = venue_with_accepted_bank_account.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        assert "0,00 € de CA" in html_parser.extract_cards_text(response.data)

    def test_venue_offers_stats(
        self,
        authenticated_client,
        venue_with_accepted_bank_account,
        offerer_active_individual_offers,
        offerer_inactive_individual_offers,
        offerer_active_collective_offers,
        offerer_inactive_collective_offers,
        offerer_active_collective_offer_templates,
        offerer_inactive_collective_offer_templates,
    ):
        venue_id = venue_with_accepted_bank_account.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert "7 offres actives ( 2 IND / 5 EAC ) 16 offres inactives ( 5 IND / 11 EAC )" in cards_text

    def test_venue_offers_stats_0_if_no_offer(self, authenticated_client, venue_with_accepted_bank_account):
        venue_id = venue_with_accepted_bank_account.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert "0 offres actives ( 0 IND / 0 EAC ) 0 offres inactives ( 0 IND / 0 EAC )" in cards_text

    def test_get_venue_not_found(self, authenticated_client):
        response = authenticated_client.get(url_for(self.endpoint, venue_id=1))
        assert response.status_code == 404


class GetVenueRevenueDetailsTest(GetEndpointHelper):
    endpoint = "backoffice_web.venue.get_revenue_details"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # session
    # user
    # bookings revenue stats
    # collective bookings revenue stats
    expected_num_queries = 4

    def test_venue_revenue_details(
        self,
        db_session,
        authenticated_client,
        venue_with_accepted_bank_account,
        individual_offerer_bookings,
        collective_venue_booking,
    ):
        venue_id = venue_with_accepted_bank_account.id
        current_year = datetime.utcnow().year

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, venue_id=venue_id))
            assert response.status_code == 200

        table_rows = html_parser.extract_table_rows(response.data)

        assert len(table_rows) == 2
        assert {row["Année"] for row in table_rows} == {str(current_year), "En cours"}

        current_year_revenues = [row for row in table_rows if row["Année"] == str(current_year)][0]
        assert current_year_revenues["CA offres IND"] == "10,00 €"
        assert current_year_revenues["CA offres EAC"] == "42,00 €"

        current_revenues = [row for row in table_rows if row["Année"] == "En cours"][0]
        assert current_revenues["CA offres IND"] == "20,00 €"
        assert current_revenues["CA offres EAC"] == "0,00 €"


class FullySyncVenueTest(PostEndpointHelper):
    endpoint = "backoffice_web.venue.fully_sync_venue"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    @patch("pcapi.workers.fully_sync_venue_job.fully_sync_venue_job.delay")
    def test_fully_sync_venue(self, fully_sync_venue_job, authenticated_client, random_venue):
        provider = providers_factories.APIProviderFactory()
        providers_factories.AllocineVenueProviderFactory(
            venue=random_venue,
            lastSyncDate=datetime.utcnow() - timedelta(hours=5),
            isActive=True,
            provider=provider,
        )

        response = self.post_to_endpoint(authenticated_client, venue_id=random_venue.id)
        assert response.status_code == 303
        fully_sync_venue_job.assert_called_once_with(random_venue.id)

    @patch("pcapi.workers.fully_sync_venue_job.fully_sync_venue_job.delay")
    def test_fully_sync_venue_disabled_provider(self, fully_sync_venue_job, authenticated_client, random_venue):
        provider = providers_factories.APIProviderFactory()
        providers_factories.AllocineVenueProviderFactory(
            venue=random_venue,
            lastSyncDate=datetime.utcnow() - timedelta(hours=4),
            isActive=False,
            provider=provider,
        )
        response = self.post_to_endpoint(authenticated_client, venue_id=random_venue.id)
        assert response.status_code == 404


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
        assert educational_models.AdageVenueAddress.query.filter_by(venueId=venue_to_delete_id).count() == 0

        expected_url = url_for("backoffice_web.pro.search_pro", _external=True)
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
            == "Impossible de supprimer un lieu pour lequel il existe des réservations"
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
            == "Impossible de supprimer un lieu utilisé comme point de valorisation d'un autre lieu"
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
            == "Impossible de supprimer un lieu utilisé comme point de remboursement d'un autre lieu"
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
            "street": venue.street or "",
            "ban_id": venue.banId or "",
            "acceslibre_url": venue.external_accessibility_url or "",
            "acceslibre_id": venue.external_accessibility_id or "",
            "booking_email": venue.bookingEmail or "",
            "phone_number": venue.contact.phone_number or "",
            "longitude": venue.longitude,
            "latitude": venue.latitude,
            "is_permanent": venue.isPermanent,
            "venue_type_code": venue.venueTypeCode.name,
        }

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
        ),
    )
    @override_features(ENABLE_ADDRESS_WRITING_WHILE_CREATING_UPDATING_VENUE=True)
    def test_update_venue(self, mock_get_address, authenticated_client, offerer):
        contact_email = "contact.venue@example.com"
        website = "update.venue@example.com"
        social_medias = {"instagram": "https://instagram.com/update.venue"}
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            contact__email=contact_email,
            contact__website=website,
            contact__social_medias=social_medias,
            offererAddress=None,
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
            "venue_type_code": offerers_models.VenueTypeCode.CREATIVE_ARTS_STORE.name,
            "acceslibre_url": "https://acceslibre.beta.gouv.fr/app/slug/",
        }

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id, _external=True)

        db.session.refresh(venue)
        address = geography_models.Address.query.one()
        offerer_address = offerers_models.OffererAddress.query.one()

        assert venue.name == data["name"]
        assert venue.publicName == data["public_name"]
        assert venue.siret == data["siret"]
        assert venue.city == address.city == data["city"]
        assert venue.postalCode == address.postalCode == data["postal_code"]
        assert venue.street == address.street == data["street"]
        assert venue.banId == address.banId == data["ban_id"]
        assert venue.bookingEmail == data["booking_email"]
        assert venue.contact.phone_number == data["phone_number"]
        assert venue.isPermanent == data["is_permanent"]
        assert venue.latitude == address.latitude == Decimal("48.86931")
        assert venue.longitude == address.longitude == Decimal("2.32546")
        assert venue.venueTypeCode == offerers_models.VenueTypeCode.CREATIVE_ARTS_STORE
        assert address.inseeCode == "75101"
        assert address.isManualEdition is False

        assert venue.offererAddressId == offerer_address.id
        assert offerer_address.addressId == address.id

        # should not have been updated or erased
        assert venue.contact.email == contact_email
        assert venue.contact.website == website
        assert venue.contact.social_medias == social_medias

        assert len(venue.action_history) == 1

        update_snapshot = venue.action_history[0].extraData["modified_info"]

        assert update_snapshot["street"]["new_info"] == data["street"]
        assert update_snapshot["bookingEmail"]["new_info"] == data["booking_email"]
        assert update_snapshot["latitude"]["new_info"] == data["latitude"]
        assert update_snapshot["longitude"]["new_info"] == data["longitude"]
        assert update_snapshot["venueTypeCode"]["new_info"] == data["venue_type_code"]
        assert update_snapshot["offererAddressId"]["new_info"] == offerer_address.id
        assert update_snapshot["offererAddress.address.latitude"]["new_info"] == data["latitude"]
        assert update_snapshot["offererAddress.address.longitude"]["new_info"] == data["longitude"]
        assert update_snapshot["offererAddress.address.city"]["new_info"] == data["city"]

        assert len(mails_testing.outbox) == 1
        # check that email is sent when venue is set to permanent and has no image
        assert mails_testing.outbox[0]["To"] == venue.bookingEmail
        assert mails_testing.outbox[0]["template"] == TransactionalEmail.VENUE_NEEDS_PICTURE.value.__dict__
        assert mails_testing.outbox[0]["params"]["VENUE_NAME"] == venue.common_name
        assert mails_testing.outbox[0]["params"]["VENUE_FORM_URL"] == urls.build_pc_pro_venue_link(venue)

    @override_features(ENABLE_ADDRESS_WRITING_WHILE_CREATING_UPDATING_VENUE=True)
    def test_update_venue_location_with_offerer_address(self, authenticated_client, offerer):
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
            "venue_type_code": offerers_models.VenueTypeCode.CREATIVE_ARTS_STORE.name,
            "acceslibre_url": "https://acceslibre.beta.gouv.fr/app/slug/",
        }
        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id, _external=True)

        db.session.refresh(venue)
        offerer_address = offerers_models.OffererAddress.query.one()
        addresses = geography_models.Address.query.all()
        assert venue.offererAddressId == offerer_address.id

        assert len(addresses) == 2
        address = [address for address in addresses if address.id == offerer_address.addressId][0]
        assert offerer_address.addressId == address.id
        assert len(venue.action_history) == 1

        update_snapshot = venue.action_history[0].extraData["modified_info"]

        assert update_snapshot["offererAddress.addressId"]["new_info"] == offerer_address.addressId

        assert update_snapshot["street"]["new_info"] == "3 Rue de Valois"
        assert update_snapshot["bookingEmail"]["new_info"] == data["booking_email"]
        assert update_snapshot["latitude"]["new_info"] == "48.87171"
        assert update_snapshot["longitude"]["new_info"] == "2.308289"  # rounding due to Decimal column in db
        assert update_snapshot["venueTypeCode"]["new_info"] == data["venue_type_code"]
        assert update_snapshot["offererAddress.address.latitude"]["new_info"] == "48.87171"
        assert update_snapshot["offererAddress.address.longitude"]["new_info"] == "2.308289"
        assert "offererAddress.address.city" not in update_snapshot  # not changed

    @pytest.mark.parametrize(
        "api_adresse_patch_params,expected_insee_code",
        [
            ({"side_effect": api_adresse.NoResultException}, None),
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
                    )
                },
                "97129",
            ),
        ],
    )
    @override_features(ENABLE_ADDRESS_WRITING_WHILE_CREATING_UPDATING_VENUE=True)
    def test_updating_venue_manual_address(
        self, authenticated_client, offerer, api_adresse_patch_params, expected_insee_code
    ):
        contact_email = "contact.venue@example.com"
        website = "update.venue@example.com"
        social_medias = {"instagram": "https://instagram.com/update.venue"}
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            contact__email=contact_email,
            contact__website=website,
            contact__social_medias=social_medias,
            offererAddress=None,
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
            "venue_type_code": offerers_models.VenueTypeCode.CULTURAL_CENTRE.name,
            "acceslibre_url": "https://acceslibre.beta.gouv.fr/app/slug/",
        }

        with patch("pcapi.connectors.api_adresse.get_municipality_centroid", **api_adresse_patch_params):
            response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id, _external=True)

        db.session.refresh(venue)
        address = geography_models.Address.query.one()
        offerer_address = offerers_models.OffererAddress.query.one()

        assert venue.timezone == "America/Guadeloupe"

        assert venue.offererAddressId == offerer_address.id
        assert offerer_address.addressId == address.id
        assert address.inseeCode == expected_insee_code
        assert address.timezone == "America/Guadeloupe"
        assert address.isManualEdition is True

        # should not have been updated or erased
        assert venue.contact.email == contact_email
        assert venue.contact.website == website
        assert venue.contact.social_medias == social_medias

        assert len(venue.action_history) == 1

        assert len(mails_testing.outbox) == 1
        # check that email is sent when venue is set to permanent and has no image
        assert mails_testing.outbox[0]["To"] == venue.bookingEmail
        assert mails_testing.outbox[0]["template"] == TransactionalEmail.VENUE_NEEDS_PICTURE.value.__dict__
        assert mails_testing.outbox[0]["params"]["VENUE_NAME"] == venue.common_name
        assert mails_testing.outbox[0]["params"]["VENUE_FORM_URL"] == urls.build_pc_pro_venue_link(venue)

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
        ),
    )
    @override_features(ENABLE_ADDRESS_WRITING_WHILE_CREATING_UPDATING_VENUE=True)
    def test_update_venue_manual_address_reuses_existing_address(
        self, mock_get_municipality_centroid, authenticated_client
    ):
        venue = offerers_factories.VenueFactory()
        offerer_address_id = venue.offererAddressId
        other_venue = offerers_factories.VenueFactory(
            street="1 Rue Poivre",
            postalCode="97400",
            city="97411",
            latitude=-20.88756,
            longitude=55.451442,
            banId="97411_1120_00001",
        )

        data = {
            "name": venue.name,
            "public_name": venue.publicName,
            "siret": venue.siret,
            "city": other_venue.city,
            "postal_code": other_venue.postalCode,
            "street": other_venue.street,
            "ban_id": other_venue.banId,
            "is_manual_address": "on",
            "booking_email": venue.bookingEmail,
            "phone_number": venue.contact.phone_number,
            "is_permanent": venue.isPermanent,
            "latitude": other_venue.latitude,
            "longitude": other_venue.longitude,
            "venue_type_code": venue.venueTypeCode.name,
            "acceslibre_url": "",
        }

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)
        assert response.status_code == 303

        db.session.refresh(venue)

        assert venue.banId == other_venue.banId
        assert venue.timezone == "Indian/Reunion"

        assert venue.offererAddressId == offerer_address_id  # unchanged
        assert venue.offererAddress.addressId == other_venue.offererAddress.addressId
        assert venue.offererAddress.address.isManualEdition is False

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
        ),
    )
    @override_features(ENABLE_ADDRESS_WRITING_WHILE_CREATING_UPDATING_VENUE=True)
    def test_update_venue_manual_address_with_gps_difference(
        self, mock_get_municipality_centroid, authenticated_client
    ):
        venue = offerers_factories.VenueFactory()
        offerer_address_id = venue.offererAddressId
        other_venue = offerers_factories.VenueFactory(
            street="1 Rue Poivre",
            postalCode="97400",
            city="97411",
            latitude=-20.88756,
            longitude=55.451442,
            banId="97411_1120_00001",
        )

        data = {
            "name": venue.name,
            "public_name": venue.publicName,
            "siret": venue.siret,
            "city": other_venue.city,
            "postal_code": other_venue.postalCode,
            "street": other_venue.street,
            "ban_id": other_venue.banId,
            "is_manual_address": "on",
            "booking_email": venue.bookingEmail,
            "phone_number": venue.contact.phone_number,
            "is_permanent": venue.isPermanent,
            "latitude": "-20.88754",
            "longitude": "55.451008",
            "venue_type_code": venue.venueTypeCode.name,
            "acceslibre_url": "",
        }

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)
        assert response.status_code == 303

        db.session.refresh(venue)

        assert venue.banId == other_venue.banId
        assert venue.timezone == "Indian/Reunion"

        assert venue.offererAddressId == offerer_address_id  # unchanged
        # same street and Insee code but different GPS position: new row because of manual edition
        assert venue.offererAddress.addressId != other_venue.offererAddress.addressId
        address = venue.offererAddress.address
        assert address.latitude == Decimal("-20.88754")
        assert address.longitude == Decimal("55.45101")
        assert address.isManualEdition is True

    @override_features(ENABLE_ADDRESS_WRITING_WHILE_CREATING_UPDATING_VENUE=False)
    def test_update_venue_without_double_model_writing(self, authenticated_client, offerer):
        contact_email = "contact.venue@example.com"
        website = "update.venue@example.com"
        social_medias = {"instagram": "https://instagram.com/update.venue"}
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            contact__email=contact_email,
            contact__website=website,
            contact__social_medias=social_medias,
            offererAddress=None,
        )

        data = {
            "name": "IKEA",
            "public_name": "Ikea city",
            "siret": venue.managingOfferer.siren + "98765",
            "city": "Paris",
            "postal_code": "75001",
            "street": "23 Boulevard de la Madeleine",
            "booking_email": venue.bookingEmail + ".update",
            "phone_number": "+33102030456",
            "is_permanent": True,
            "latitude": "48.869311",
            "longitude": "2.325463",
            "venue_type_code": offerers_models.VenueTypeCode.CREATIVE_ARTS_STORE.name,
            "acceslibre_url": "https://acceslibre.beta.gouv.fr/app/slug/",
        }

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id, _external=True)

        db.session.refresh(venue)
        assert not geography_models.Address.query.one_or_none()
        assert not offerers_models.OffererAddress.query.one_or_none()

        assert venue.name == data["name"]
        assert venue.publicName == data["public_name"]
        assert venue.siret == data["siret"]
        assert venue.city == data["city"]
        assert venue.postalCode == data["postal_code"]
        assert venue.banId is None
        assert venue.street == data["street"]
        assert venue.bookingEmail == data["booking_email"]
        assert venue.contact.phone_number == data["phone_number"]
        assert venue.isPermanent == data["is_permanent"]
        assert venue.latitude == Decimal("48.86931")
        assert venue.longitude == Decimal("2.32546")
        assert venue.venueTypeCode == offerers_models.VenueTypeCode.CREATIVE_ARTS_STORE

        assert not venue.offererAddressId

        # should not have been updated or erased
        assert venue.contact.email == contact_email
        assert venue.contact.website == website
        assert venue.contact.social_medias == social_medias

        assert len(venue.action_history) == 1

        update_snapshot = venue.action_history[0].extraData["modified_info"]

        assert update_snapshot["street"]["new_info"] == data["street"]
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

    @pytest.mark.parametrize(
        "field,value",
        [
            ("name", ""),
            ("latitude", "48.87.004"),
            ("latitude", "98.87004"),
            ("longitude", "2.3785O"),
            ("longitude", "237.850"),
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

    @patch("pcapi.connectors.entreprise.sirene.siret_is_active", return_value=False)
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

    @pytest.mark.parametrize("removed_field", ["street", "postal_code", "city"])
    def test_update_venue_remove_address_blocked_by_constraint(self, authenticated_client, removed_field):
        venue = offerers_factories.VenueWithoutSiretFactory()

        data = self._get_current_data(venue)
        data[removed_field] = ""

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 400
        assert "Les données envoyées comportent des erreurs." in html_parser.extract_alert(response.data)
        assert venue.street
        assert venue.postalCode
        assert venue.city

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

        assert venue.street == data["street"]
        assert venue.banId == data["ban_id"]
        assert venue.action_history[0].extraData == {
            "modified_info": {
                "banId": {"new_info": "15152_0024_00003", "old_info": "75102_7560_00001"},
            }
        }

    def test_update_venue_latitude_longitude_precision(self, authenticated_client):
        venue = offerers_factories.VenueFactory()

        data = self._get_current_data(venue)
        data["latitude"] = "48.870037"
        data["longitude"] = "2.378504"

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303

        db.session.refresh(venue)

        assert venue.latitude == Decimal("48.87004")
        assert venue.longitude == Decimal("2.37850")
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
        assert update_snapshot["city"]["new_info"] == "Rome"
        assert venue.longitude == data["longitude"]
        assert venue.latitude == data["latitude"]
        assert venue.offererAddress.address.longitude == data["longitude"]
        assert venue.offererAddress.address.latitude == data["latitude"]
        assert "offererAddress.address.longitude" not in update_snapshot
        assert "offererAddress.address.latitude" not in update_snapshot
        assert "longitude" not in update_snapshot
        assert "latitude" not in update_snapshot

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

    def test_update_venue_accessibility_provider_from_acceslibre_url_when_becoming_permanent(
        self, authenticated_client
    ):
        venue = offerers_factories.VenueFactory(venueTypeCode=offerers_models.VenueTypeCode.TRAVELING_CINEMA)

        data = self._get_current_data(venue)
        data["acceslibre_url"] = "https://acceslibre.beta.gouv.fr/erps/mon-slug/"
        data["is_permanent"] = True

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303
        db.session.refresh(venue)
        assert venue.accessibilityProvider
        assert venue.action_history[0].extraData == {
            "modified_info": {
                "accessibilityProvider.externalAccessibilityId": {
                    "new_info": "mon-slug",
                    "old_info": None,
                },
                "accessibilityProvider.externalAccessibilityUrl": {
                    "new_info": "https://acceslibre.beta.gouv.fr/erps/mon-slug/",
                    "old_info": None,
                },
                "isPermanent": {
                    "new_info": True,
                    "old_info": False,
                },
            }
        }

    def test_update_venue_should_not_add_accessibility_provider_if_not_permanent(self, authenticated_client):
        venue = offerers_factories.VenueFactory(venueTypeCode=offerers_models.VenueTypeCode.TRAVELING_CINEMA)

        data = self._get_current_data(venue)
        data["acceslibre_url"] = "https://acceslibre.beta.gouv.fr/erps/mon-slug/"
        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 400
        assert "Les données envoyées comportent des erreurs." in html_parser.extract_alert(response.data)
        db.session.refresh(venue)
        assert venue.accessibilityProvider == None

    def test_update_venue_remove_accesslibre_url_when_becoming_non_permanent(self, authenticated_client):
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
    def test_update_venue_becomes_permanent_should_call_match_acceslibre_job(
        self, match_acceslibre_job, authenticated_client
    ):
        venue = offerers_factories.VenueFactory(isPermanent=False)
        data = self._get_current_data(venue)
        data["is_permanent"] = True

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id, form=data)

        assert response.status_code == 303
        match_acceslibre_job.assert_called_once_with(venue.id)

    @override_settings(ACCESLIBRE_BACKEND="pcapi.connectors.acceslibre.AcceslibreBackend")
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
        assert offerers_models.OffererConfidenceRule.query.count() == 0
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

    def test_venue_history(self, authenticated_client, legit_user, pro_fraud_admin):
        venue = offerers_factories.VenueFactory()

        comment = "test comment"
        history_factories.ActionHistoryFactory(
            # displayed because legit_user has fraud permission
            actionType=history_models.ActionType.FRAUD_INFO_MODIFIED,
            actionDate=datetime.utcnow() - timedelta(days=2),
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
        assert "Activité principale : Autre => Librairie " in rows[0]["Commentaire"]
        assert "Site internet de contact : suppression de : https://old.website.com " in rows[0]["Commentaire"]
        assert "Conditions de retrait : ajout de : Come here!" in rows[0]["Commentaire"]
        assert "Accessibilité handicap visuel : Non => Oui" in rows[0]["Commentaire"]
        assert "Horaires du lundi : 14:00-19:30 => 10:00-13:00, 14:00-19:30" in rows[0]["Commentaire"]
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


class GetVenueCollectiveDmsApplicationsTest(GetEndpointHelper):
    endpoint = "backoffice_web.venue.get_collective_dms_applications"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # get session (1 query)
    # get user with profile and permissions (1 query)
    # get applications (1 query)
    expected_num_queries = 3

    def test_venue_with_dms_adage_application(self, authenticated_client):
        venue = offerers_factories.VenueFactory(siret="1234567891234")

        url = url_for(self.endpoint, venue_id=venue.id)

        # if venue is not removed from the current session, any get
        # query won't be executed because of this specific testing
        # environment. this would tamper the real database queries
        # count.
        db.session.expire(venue)

        accepted_application = educational_factories.CollectiveDmsApplicationFactory(
            venue=venue, depositDate=datetime.utcnow() - timedelta(days=10), state="accepte"
        )
        expired_application = educational_factories.CollectiveDmsApplicationFactory(
            venue=venue, depositDate=datetime.utcnow() - timedelta(days=5), state="refuse"
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert rows[0]["ID"] == str(expired_application.application)
        assert (
            f"https://www.demarches-simplifiees.fr/procedures/{expired_application.procedure}/dossiers/{expired_application.application}"
            in str(response.data)
        )
        assert rows[0]["Date de dépôt"] == expired_application.depositDate.strftime("%d/%m/%Y")
        assert rows[0]["État"] == "Refusé"
        assert rows[0]["Date de dernière mise à jour"] == expired_application.lastChangeDate.strftime("%d/%m/%Y")
        assert rows[1]["ID"] == str(accepted_application.application)
        assert (
            f"https://www.demarches-simplifiees.fr/procedures/{accepted_application.procedure}/dossiers/{accepted_application.application}"
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

        action = history_models.ActionHistory.query.one()
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

        action = history_models.ActionHistory.query.one()
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
        assert f"Lieu : {venue_with_no_siret.name}" in content
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


class GetSetPricingPointFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.venue.get_set_pricing_point_form"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT
    # +1 session
    # +1 user
    # +1 venue and venues from the same offerer
    expected_num_queries = 3

    def get_set_pricing_point_form(self, authenticated_client):
        venue = offerers_factories.VirtualVenueFactory()

        url = url_for(self.endpoint, venue_id=venue.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200


class SetPricingPointTest(PostEndpointHelper):
    endpoint = "backoffice_web.venue.set_pricing_point"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT
    # +1 session
    # +1 user
    # +1 venue and venues from the same offerer
    # +1 FF USE_END_DATE_FOR_COLLECTIVE_PRICING
    # +1 pricing point validation
    # +1 check if the venue already has a link
    # +3 set pricing point
    # +1 reload venue
    expected_num_queries = 10

    def test_set_pricing_point(self, authenticated_client):
        venue_with_no_siret = offerers_factories.VirtualVenueFactory()
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
        assert html_parser.extract_alert(redirected_response.data) == "Ce lieu a été lié à un point de valorisation"

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
        venue_with_no_siret = offerers_factories.VirtualVenueFactory()
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
        venue_with_no_siret = offerers_factories.VirtualVenueFactory()
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
        assert html_parser.extract_alert(redirected_response.data) == "Ce lieu est déja lié à un point de valorisation"

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
            == "Ce lieu a un SIRET, vous ne pouvez donc pas choisir un autre lieu pour le calcul du barème de remboursement."
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

    def test_remove_pricing_point_and_reimbursement_point(self, legit_user, authenticated_client, venue_with_no_siret):
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue_with_no_siret, bankAccount=finance_factories.BankAccountFactory()
        )
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
        other_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        offerers_factories.VenuePricingPointLinkFactory(venue=other_venue, pricingPoint=venue)
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
        assert "Le lien entre le lieu et le provider a été supprimé." in html_parser.extract_alert(response.data)

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
        assert "Impossible de supprimer le lien entre le lieu et Allociné." in html_parser.extract_alert(response.data)


class GetEntrepriseInfoTest(GetEndpointHelper):
    endpoint = "backoffice_web.venue.get_entreprise_info"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTREPRISE_INFO

    # get session (1 query)
    # get user with profile and permissions (1 query)
    # get venue (1 query)
    expected_num_queries = 3

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
        assert "Code APE : 90.03A" in sirene_content
        assert "Activité principale : Création artistique relevant des arts plastiques" in sirene_content

    def test_siret_not_found(self, authenticated_client):
        venue = offerers_factories.VenueFactory(siret="00000000000018")
        url = url_for(self.endpoint, venue_id=venue.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        # Values come from TestingBackend, check display
        sirene_content = html_parser.extract_cards_text(response.data)[0]
        assert (
            "Ce SIRET est inconnu dans la base de données Sirene, y compris dans les non-diffusibles" in sirene_content
        )

    def test_venue_not_found(self, authenticated_client):
        url = url_for(self.endpoint, venue_id=1)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 404

    def test_venue_without_siret(self, authenticated_client):
        venue = offerers_factories.VenueWithoutSiretFactory()
        url = url_for(self.endpoint, venue_id=venue.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 404

    def test_venue_with_invalid_siret(self, authenticated_client):
        venue = offerers_factories.VenueFactory(siret="22222222222222")
        url = url_for(self.endpoint, venue_id=venue.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        sirene_content = html_parser.extract_cards_text(response.data)[0]
        assert (
            "Erreur Le format du numéro SIRET est détecté comme invalide, nous ne pouvons pas récupérer de données sur l'établissement."
            in sirene_content
        )
