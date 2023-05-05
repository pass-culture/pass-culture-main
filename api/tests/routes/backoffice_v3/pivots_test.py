from flask import url_for
import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers import models as providers_models
import pcapi.core.providers.repository as providers_repository
from pcapi.core.testing import assert_num_queries
from pcapi.models import db

from tests.connectors.cgr import soap_definitions
from tests.local_providers.cinema_providers.cgr import fixtures

from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class GetPivotsPageTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.pivots.get_pivots"
    needed_permission = perm_models.Permissions.MANAGE_PROVIDERS

    def test_get_pivots_page(self, authenticated_client):
        with assert_num_queries(2):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200


class ListPivotsTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.pivots.list_pivots"
    endpoint_kwargs = {"name": "allocine"}
    needed_permission = perm_models.Permissions.MANAGE_PROVIDERS

    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch a single pivot with joinedload (1 query)
    expected_num_queries = 3

    def test_list_pivots_allocine(self, authenticated_client):
        # given
        allocine_pivot = providers_factories.AllocinePivotFactory()

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="allocine"))
            assert response.status_code == 200

        # then
        allocine_rows = html_parser.extract_table_rows(response.data)
        assert allocine_rows[0]["Id du Lieu"] == str(allocine_pivot.venue.id)
        assert allocine_rows[0]["Lieu"] == allocine_pivot.venue.name
        assert allocine_rows[0]["Identifiant cinéma (Allociné)"] == allocine_pivot.theaterId
        assert allocine_rows[0]["Identifiant interne Allociné"] == allocine_pivot.internalId

    @pytest.mark.parametrize(
        "query_string,expected_venues",
        [
            ("10", {"Cinéma Edison"}),  # id
            ("91", set()),
            ("cinéma", {"Cinéma Edison", "Cinéma Lumière"}),  # beginning, accent
            ("lumiere", {"Cinéma Lumière", "Chez les Frères Lumière"}),  # end, no accent
            ("ABCDEFGHIJKLMNOPQR==", {"Cinéma Edison"}),  # full theater id
            ("CDEFGHIJKLMNOPQR", set()),  # part of theater id
            ("P01891", set()),  # not searchable
        ],
    )
    def test_filter_pivots_allocine(self, authenticated_client, query_string, expected_venues):
        # given
        providers_factories.AllocinePivotFactory(
            venue__id=10, venue__name="Cinéma Edison", theaterId="ABCDEFGHIJKLMNOPQR==", internalId="P01891"
        )
        providers_factories.AllocinePivotFactory(
            venue__id=11, venue__name="Cinéma Lumière", theaterId="BCDEFGHIJKLMNOPQRS==", internalId="P01895"
        )
        providers_factories.AllocinePivotFactory(
            venue__id=12, venue__name="Chez les Frères Lumière", theaterId="CDEFGHIJKLMNOPQRST==", internalId="P18950"
        )

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="allocine", q=query_string))
            assert response.status_code == 200

        # then
        allocine_rows = html_parser.extract_table_rows(response.data)
        assert {row["Lieu"] for row in allocine_rows} == expected_venues

    def test_list_pivots_boost(self, authenticated_client):
        # given
        boost_pivot = providers_factories.BoostCinemaDetailsFactory()

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="boost"))
            assert response.status_code == 200

        # then
        boost_rows = html_parser.extract_table_rows(response.data)
        assert boost_rows[0]["Id du Lieu"] == str(boost_pivot.cinemaProviderPivot.venue.id)
        assert boost_rows[0]["Lieu"] == boost_pivot.cinemaProviderPivot.venue.name
        assert boost_rows[0]["Identifiant cinéma (Boost)"] == boost_pivot.cinemaProviderPivot.idAtProvider
        assert boost_rows[0]["Nom de l'utilisateur (Boost)"] == boost_pivot.username
        assert boost_rows[0]["Mot de passe (Boost)"] == boost_pivot.password
        assert boost_rows[0]["URL du cinéma (Boost)"] == boost_pivot.cinemaUrl

    @pytest.mark.parametrize(
        "query_string,expected_venues",
        [
            ("10", {"Cinéma Edison"}),  # id
            ("91", set()),
            ("cinéma", {"Cinéma Edison", "Cinéma Lumière"}),  # beginning, accent
            ("lumiere", {"Cinéma Lumière", "Chez les Frères Lumière"}),  # end, no accent
            ("idProvider1010", {"Cinéma Edison"}),  # full idAtProvider
            ("idProvider101", set()),  # part idAtProvider
            ("http://boost-cinema-", set()),  # not searchable
        ],
    )
    def test_filter_pivots_boost(self, authenticated_client, query_string, expected_venues):
        # given
        cgr_provider = providers_repository.get_provider_by_local_class("BoostStocks")
        providers_factories.BoostCinemaDetailsFactory(
            cinemaProviderPivot=providers_factories.CinemaProviderPivotFactory(
                venue=offerers_factories.VenueFactory(id=10, name="Cinéma Edison"),
                provider=cgr_provider,
                idAtProvider="idProvider1010",
            ),
        )
        providers_factories.BoostCinemaDetailsFactory(
            cinemaProviderPivot=providers_factories.CinemaProviderPivotFactory(
                venue=offerers_factories.VenueFactory(id=11, name="Cinéma Lumière"),
                provider=cgr_provider,
                idAtProvider="idProvider1111",
            ),
        )
        providers_factories.BoostCinemaDetailsFactory(
            cinemaProviderPivot=providers_factories.CinemaProviderPivotFactory(
                venue=offerers_factories.VenueFactory(id=12, name="Chez les Frères Lumière"),
                provider=cgr_provider,
                idAtProvider="idProvider1212",
            ),
        )

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="boost", q=query_string))
            assert response.status_code == 200

        # then
        cgr_rows = html_parser.extract_table_rows(response.data)
        assert {row["Lieu"] for row in cgr_rows} == expected_venues

    def test_list_pivots_cgr(self, authenticated_client):
        # given
        cgr_pivot = providers_factories.CGRCinemaDetailsFactory()

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="cgr"))
            assert response.status_code == 200

        # then
        cgr_rows = html_parser.extract_table_rows(response.data)
        assert cgr_rows[0]["Id du Lieu"] == str(cgr_pivot.cinemaProviderPivot.venue.id)
        assert cgr_rows[0]["Lieu"] == cgr_pivot.cinemaProviderPivot.venue.name
        assert cgr_rows[0]["Identifiant cinéma (CGR)"] == cgr_pivot.cinemaProviderPivot.idAtProvider
        assert cgr_rows[0]["URL du cinéma (CGR)"] == cgr_pivot.cinemaUrl

    @pytest.mark.parametrize(
        "query_string,expected_venues",
        [
            ("10", {"Cinéma Edison"}),  # id
            ("91", set()),
            ("cinéma", {"Cinéma Edison", "Cinéma Lumière"}),  # beginning, accent
            ("lumiere", {"Cinéma Lumière", "Chez les Frères Lumière"}),  # end, no accent
            ("idProvider1010", {"Cinéma Edison"}),  # full idAtProvider
            ("idProvider101", set()),  # part idAtProvider
            ("http://cgr-cinema-", set()),  # not searchable
        ],
    )
    def test_filter_pivots_cgr(self, authenticated_client, query_string, expected_venues):
        # given
        cgr_provider = providers_repository.get_provider_by_local_class("CGRStocks")
        providers_factories.CGRCinemaDetailsFactory(
            cinemaProviderPivot=providers_factories.CinemaProviderPivotFactory(
                venue=offerers_factories.VenueFactory(id=10, name="Cinéma Edison"),
                provider=cgr_provider,
                idAtProvider="idProvider1010",
            ),
        )
        providers_factories.CGRCinemaDetailsFactory(
            cinemaProviderPivot=providers_factories.CinemaProviderPivotFactory(
                venue=offerers_factories.VenueFactory(id=11, name="Cinéma Lumière"),
                provider=cgr_provider,
                idAtProvider="idProvider1111",
            ),
        )
        providers_factories.CGRCinemaDetailsFactory(
            cinemaProviderPivot=providers_factories.CinemaProviderPivotFactory(
                venue=offerers_factories.VenueFactory(id=12, name="Chez les Frères Lumière"),
                provider=cgr_provider,
                idAtProvider="idProvider1212",
            ),
        )

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="cgr", q=query_string))
            assert response.status_code == 200

        # then
        cgr_rows = html_parser.extract_table_rows(response.data)
        assert {row["Lieu"] for row in cgr_rows} == expected_venues

    def test_list_pivots_cineoffice(self, authenticated_client):
        # given
        cineoffice_pivot = providers_factories.CDSCinemaDetailsFactory()

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="cineoffice"))
            assert response.status_code == 200

        # then
        cineoffice_rows = html_parser.extract_table_rows(response.data)
        assert cineoffice_rows[0]["Id du Lieu"] == str(cineoffice_pivot.cinemaProviderPivot.venue.id)
        assert cineoffice_rows[0]["Lieu"] == cineoffice_pivot.cinemaProviderPivot.venue.name
        assert cineoffice_rows[0]["Identifiant cinéma (CDS)"] == cineoffice_pivot.cinemaProviderPivot.idAtProvider
        assert cineoffice_rows[0]["Nom de l'utilisateur (CDS)"] == cineoffice_pivot.accountId
        assert cineoffice_rows[0]["Clé API (CDS)"] == cineoffice_pivot.cinemaApiToken

    @pytest.mark.parametrize(
        "query_string,expected_venues",
        [
            ("10", {"Cinéma Edison"}),  # id
            ("91", set()),
            ("cinéma", {"Cinéma Edison", "Cinéma Lumière"}),  # beginning, accent
            ("lumiere", {"Cinéma Lumière", "Chez les Frères Lumière"}),  # end, no accent
            ("accountId1010", {"Cinéma Edison"}),  # full idAtProvider
            ("accountId101", set()),  # part idAtProvider
            ("http://cineoffice-cinema-", set()),  # not searchable
        ],
    )
    def test_filter_pivots_cineoffice(self, authenticated_client, query_string, expected_venues):
        # given
        cds_provider = providers_repository.get_provider_by_local_class("CDSStocks")
        providers_factories.CDSCinemaDetailsFactory(
            cinemaProviderPivot=providers_factories.CinemaProviderPivotFactory(
                venue=offerers_factories.VenueFactory(id=10, name="Cinéma Edison"),
                provider=cds_provider,
                idAtProvider="accountId1010",
            ),
            accountId="Super compte 1",
            cinemaApiToken="azerty1",
        )
        providers_factories.CDSCinemaDetailsFactory(
            cinemaProviderPivot=providers_factories.CinemaProviderPivotFactory(
                venue=offerers_factories.VenueFactory(id=11, name="Cinéma Lumière"),
                provider=cds_provider,
                idAtProvider="accountId1111",
            ),
            accountId="admin account!",
            cinemaApiToken="azerty13",
        )
        providers_factories.CDSCinemaDetailsFactory(
            cinemaProviderPivot=providers_factories.CinemaProviderPivotFactory(
                venue=offerers_factories.VenueFactory(id=12, name="Chez les Frères Lumière"),
                provider=cds_provider,
                idAtProvider="accountId1212",
            ),
            accountId="compte pro #54",
            cinemaApiToken="azerty123",
        )

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="cineoffice", q=query_string))
            assert response.status_code == 200

        # then
        cgr_rows = html_parser.extract_table_rows(response.data)
        assert {row["Lieu"] for row in cgr_rows} == expected_venues


class GetCreatePivotFormTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.pivots.get_create_pivot_form"
    endpoint_kwargs = {"name": "allocine"}
    needed_permission = perm_models.Permissions.MANAGE_PROVIDERS

    # - fetch session (1 query)
    # - fetch user (1 query)
    expected_num_queries = 2

    def test_get_create_pivot_form_allocine(self, authenticated_client):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="allocine"))
            assert response.status_code == 200

    def test_get_create_pivot_form_boost(self, authenticated_client):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="boost"))
            assert response.status_code == 200

    def test_get_create_pivot_form_cgr(self, authenticated_client):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="cgr"))
            assert response.status_code == 200

    def test_get_create_pivot_form_cineoffice(self, authenticated_client):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="cineoffice"))
            assert response.status_code == 200


class CreatePivotTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.pivots.create_pivot"
    endpoint_kwargs = {"name": "allocine"}
    needed_permission = perm_models.Permissions.MANAGE_PROVIDERS

    def test_create_pivot_allocine(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        form = {"venue_id": venue.id, "theater_id": "ABCDEFGHIJKLMNOPQR==", "internal_id": "P12345"}

        response = self.post_to_endpoint(authenticated_client, name="allocine", form=form)
        assert response.status_code == 303

        created = providers_models.AllocinePivot.query.one()
        assert created.venueId == venue.id
        assert created.theaterId == form["theater_id"]
        assert created.internalId == form["internal_id"]

    def test_create_pivot_boost(self, requests_mock, authenticated_client):
        requests_mock.get("http://example.com/boost1/")
        requests_mock.post("http://example.com/boost1/")
        venue_id = offerers_factories.VenueFactory().id
        form = {
            "venue_id": venue_id,
            "cinema_id": "boost cinema 1",
            "cinema_url": "http://example.com/boost1/",
            "username": "boost super user",
            "password": "azerty!123",
        }

        self.post_to_endpoint(authenticated_client, name="boost", form=form)

        created = providers_models.BoostCinemaDetails.query.one()
        assert created.cinemaProviderPivot.venueId == venue_id
        assert created.cinemaProviderPivot.idAtProvider == form["cinema_id"]
        assert created.cinemaUrl == form["cinema_url"]
        assert created.username == form["username"]
        assert created.password == form["password"]

    def test_create_pivot_cgr(self, requests_mock, authenticated_client):
        requests_mock.get("http://example.com/another_web_service", text=soap_definitions.WEB_SERVICE_DEFINITION)
        requests_mock.post(
            "http://example.com/another_web_service", text=fixtures.cgr_response_template([fixtures.FILM_138473])
        )
        venue_id = offerers_factories.VenueFactory().id
        form = {
            "venue_id": venue_id,
            "cinema_id": "idProvider1111",
            "cinema_url": "http://example.com/another_web_service",
            "password": "azerty!123",
        }

        self.post_to_endpoint(authenticated_client, name="cgr", form=form)

        created = providers_models.CGRCinemaDetails.query.one()
        assert created.cinemaProviderPivot.venueId == venue_id
        assert created.cinemaProviderPivot.idAtProvider == form["cinema_id"]
        assert created.cinemaUrl == form["cinema_url"]
        assert created.password == form["password"]

    def test_create_pivot_cineoffice(self, authenticated_client):
        venue_id = offerers_factories.VenueFactory().id
        form = {
            "venue_id": venue_id,
            "cinema_id": "cineoffice cinema 1",
            "account_id": "cineoffice account 1",
            "api_token": "====?azerty!123",
        }

        self.post_to_endpoint(authenticated_client, name="cineoffice", form=form)

        created = providers_models.CDSCinemaDetails.query.one()
        assert created.cinemaProviderPivot.venueId == venue_id
        assert created.cinemaProviderPivot.idAtProvider == form["cinema_id"]
        assert created.accountId == form["account_id"]
        assert created.cinemaApiToken == form["api_token"]


class GetUpdatePivotFormTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.pivots.get_update_pivot_form"
    endpoint_kwargs = {"name": "allocine", "pivot_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PROVIDERS

    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch pivot (1 query)
    # - fetch venue to fill autocomplete (1 query)
    expected_num_queries = 4

    def test_get_update_pivot_form_allocine(self, authenticated_client):
        # given
        allocine_pivot = providers_factories.AllocinePivotFactory()
        pivot_id = allocine_pivot.id

        db.session.expire(allocine_pivot)

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="allocine", pivot_id=pivot_id))
            assert response.status_code == 200

    def test_get_update_pivot_form_boost(self, authenticated_client):
        # given
        # - fetch boost cinema details (1 query)
        # - fetch session (1 query)
        # - fetch user (1 query)
        # - fetch pivot (1 query)
        # - fetch venue for form validate (1 query)
        # - fetch venue to fill autocomplete (1 query)
        expected_num_queries = 6

        boost_pivot = providers_factories.BoostCinemaDetailsFactory(cinemaUrl="http://example.com/boost1")

        db.session.expire(boost_pivot)

        # when
        with assert_num_queries(expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="boost", pivot_id=boost_pivot.id))
            assert response.status_code == 200

    def test_get_update_pivot_form_cgr(self, authenticated_client):
        # given
        # - fetch cgr cinema details (1 query)
        # - fetch session (1 query)
        # - fetch user (1 query)
        # - fetch pivot (1 query)
        # - fetch venue for form validate (1 query)
        # - fetch venue to fill autocomplete (1 query)
        expected_num_queries = 6

        cgr_pivot = providers_factories.CGRCinemaDetailsFactory(cinemaUrl="http://example.com/another_web_service")

        db.session.expire(cgr_pivot)

        # when
        with assert_num_queries(expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="cgr", pivot_id=cgr_pivot.id))
            assert response.status_code == 200

    def test_get_update_pivot_form_cineoffice(self, authenticated_client):
        # given
        # - fetch cineoffice cinema details (1 query)
        # - fetch session (1 query)
        # - fetch user (1 query)
        # - fetch pivot (1 query)
        # - fetch venue for form validate (1 query)
        # - fetch venue to fill autocomplete (1 query)
        expected_num_queries = 6

        cineoffice_pivot = providers_factories.CDSCinemaDetailsFactory()

        db.session.expire(cineoffice_pivot)

        # when
        with assert_num_queries(expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="cineoffice", pivot_id=cineoffice_pivot.id))
            assert response.status_code == 200


class UpdatePivotTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.pivots.update_pivot"
    endpoint_kwargs = {"name": "allocine", "pivot_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PROVIDERS

    def test_update_pivot_allocine(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        pivot_id = providers_factories.AllocinePivotFactory().id

        form = {"venue_id": venue.id, "theater_id": "ABCDEFGHIJKLMNOPQR==", "internal_id": "P12345"}

        response = self.post_to_endpoint(authenticated_client, name="allocine", pivot_id=pivot_id, form=form)
        assert response.status_code == 303

        updated = providers_models.AllocinePivot.query.one()
        assert updated.venueId == venue.id
        assert updated.theaterId == form["theater_id"]
        assert updated.internalId == form["internal_id"]

    def test_update_pivot_boost(self, authenticated_client, requests_mock):
        requests_mock.get("http://example.com/boost1/")
        requests_mock.post("http://example.com/boost1/")
        boost_pivot = providers_factories.BoostCinemaDetailsFactory(cinemaUrl="http://example.com/boost0/")

        form = {
            "cinema_id": "boost 1",
            "cinema_url": "http://example.com/boost1/",
            "username": "super user de boost 1",
            "password": "Azerty!123",
        }

        self.post_to_endpoint(authenticated_client, name="boost", pivot_id=boost_pivot.id, form=form)

        updated = providers_models.BoostCinemaDetails.query.one()
        assert updated.cinemaProviderPivot.idAtProvider == form["cinema_id"]
        assert updated.cinemaUrl == form["cinema_url"]
        assert updated.password == form["password"]
        assert updated.password == form["password"]

    def test_update_pivot_cgr(self, authenticated_client, requests_mock):
        requests_mock.get("http://example.com/another_web_service", text=soap_definitions.WEB_SERVICE_DEFINITION)
        requests_mock.post(
            "http://example.com/another_web_service", text=fixtures.cgr_response_template([fixtures.FILM_138473])
        )
        cgr_pivot = providers_factories.CGRCinemaDetailsFactory()

        form = {
            "cinema_id": "idProvider1000",
            "cinema_url": "http://example.com/another_web_service",
            "password": "Azerty!123",
        }

        self.post_to_endpoint(authenticated_client, name="cgr", pivot_id=cgr_pivot.id, form=form)

        updated = providers_models.CGRCinemaDetails.query.one()
        assert updated.cinemaProviderPivot.idAtProvider == form["cinema_id"]
        assert updated.cinemaUrl == form["cinema_url"]
        assert updated.password == form["password"]

    def test_update_pivot_cineoffice(self, authenticated_client):
        cineoffice_pivot = providers_factories.CDSCinemaDetailsFactory()

        form = {
            "cinema_id": "boost 1",
            "account_id": "account 1er",
            "api_token": "==@/@414324rF!",
        }

        self.post_to_endpoint(authenticated_client, name="cineoffice", pivot_id=cineoffice_pivot.id, form=form)

        updated = providers_models.CDSCinemaDetails.query.one()
        assert updated.cinemaProviderPivot.idAtProvider == form["cinema_id"]
        assert updated.accountId == form["account_id"]
        assert updated.cinemaApiToken == form["api_token"]


class DeleteProviderTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.pivots.delete_pivot"
    endpoint_kwargs = {"name": "cgr", "pivot_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PROVIDERS

    def test_delete_pivot_boost(self, authenticated_client):
        boost_pivot = providers_factories.BoostCinemaDetailsFactory()

        self.post_to_endpoint(authenticated_client, name="boost", pivot_id=boost_pivot.id)

        assert not providers_models.BoostCinemaDetails.query.get(boost_pivot.id)

    def test_delete_pivot_cgr(self, authenticated_client):
        cgr_pivot = providers_factories.CGRCinemaDetailsFactory()

        self.post_to_endpoint(authenticated_client, name="cgr", pivot_id=cgr_pivot.id)

        assert not providers_models.CGRCinemaDetails.query.get(cgr_pivot.id)

    def test_delete_pivot_cineoffice(self, authenticated_client):
        cineoffice_pivot = providers_factories.CDSCinemaDetailsFactory()

        self.post_to_endpoint(authenticated_client, name="cineoffice", pivot_id=cineoffice_pivot.id)

        assert not providers_models.CDSCinemaDetails.query.get(cineoffice_pivot.id)
