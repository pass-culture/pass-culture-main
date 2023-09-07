from datetime import datetime
from unittest.mock import patch

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
    pytest.mark.backoffice,
]


class GetPivotsPageTest(GetEndpointHelper):
    endpoint = "backoffice_web.pivots.get_pivots"
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT

    def test_get_pivots_page(self, authenticated_client):
        with assert_num_queries(2):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200


class ListPivotsTest(GetEndpointHelper):
    endpoint = "backoffice_web.pivots.list_pivots"
    endpoint_kwargs = {"name": "allocine"}
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT

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

    def test_list_pivots_ems(self, authenticated_client):
        ems_pivot = providers_factories.EMSCinemaDetailsFactory()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="ems"))
            assert response.status_code == 200

        ems_rows = html_parser.extract_table_rows(response.data)

        assert ems_rows[0]["Id du Lieu"] == str(ems_pivot.cinemaProviderPivot.venue.id)
        assert ems_rows[0]["Lieu"] == ems_pivot.cinemaProviderPivot.venue.name
        assert ems_rows[0]["Identifiant cinéma (EMS)"] == ems_pivot.cinemaProviderPivot.idAtProvider
        assert ems_rows[0]["Dernière synchronisation réussie"] == ems_pivot.last_version_as_isoformat


class GetCreatePivotFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.pivots.get_create_pivot_form"
    endpoint_kwargs = {"name": "allocine"}
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT

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

    @patch("pcapi.routes.backoffice.pivots.contexts.ems.EMSContext.check_if_api_call_is_ok")
    def test_get_create_pivot_form_ems(self, mocked_healthcheck, authenticated_client):
        mocked_healthcheck.return_value = None
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="ems"))
            assert response.status_code == 200


class CreatePivotTest(PostEndpointHelper):
    endpoint = "backoffice_web.pivots.create_pivot"
    endpoint_kwargs = {"name": "allocine"}
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT

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
            "account_id": "cineofficeaccount1",
            "api_token": "====?azerty!123",
        }

        self.post_to_endpoint(authenticated_client, name="cineoffice", form=form)

        created = providers_models.CDSCinemaDetails.query.one()
        assert created.cinemaProviderPivot.venueId == venue_id
        assert created.cinemaProviderPivot.idAtProvider == form["cinema_id"]
        assert created.accountId == form["account_id"]
        assert created.cinemaApiToken == form["api_token"]

    @patch("pcapi.routes.backoffice.pivots.contexts.ems.EMSContext.check_if_api_call_is_ok")
    def test_create_pivot_ems(self, mocked_healthcheck, authenticated_client):
        mocked_healthcheck.return_value = None
        venue_id = offerers_factories.VenueFactory().id
        form = {
            "venue_id": venue_id,
            "cinema_id": "idAtProvider1",
        }

        self.post_to_endpoint(authenticated_client, name="ems", form=form)

        created: providers_models.EMSCinemaDetails = providers_models.EMSCinemaDetails.query.one()
        assert created.cinemaProviderPivot.venueId == venue_id
        assert created.cinemaProviderPivot.idAtProvider == form["cinema_id"]
        assert created.lastVersion == 0

    def test_create_pivot_cineoffice_with_forbidden_characters(self, authenticated_client):
        venue_id = offerers_factories.VenueFactory().id
        form = {
            "venue_id": venue_id,
            "cinema_id": "cineoffice cinema 1",
            "account_id": "cineoffice account with spaces",
            "api_token": "====?azerty!123",
        }

        response = self.post_to_endpoint(authenticated_client, name="cineoffice", form=form)

        created = providers_models.CDSCinemaDetails.query.one_or_none()
        assert created is None

        redirected_response = authenticated_client.get(response.headers["location"])

        assert (
            "Le nom de compte ne peut pas contenir de caractères autres que chiffres, lettres et tirets"
            in html_parser.content_as_text(redirected_response.data)
        )


class GetUpdatePivotFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.pivots.get_update_pivot_form"
    endpoint_kwargs = {"name": "allocine", "pivot_id": 1}
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT

    # - fetch cinema details (1 query)
    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch pivot (1 query)
    # - fetch venue for form validate (1 query)
    # - fetch venue to fill autocomplete (1 query)
    expected_num_queries = 6

    def test_get_update_pivot_form_allocine(self, authenticated_client):
        # given
        # - fetch session (1 query)
        # - fetch user (1 query)
        # - fetch pivot (1 query)
        # - fetch venue to fill autocomplete (1 query)
        allocine_pivot_expected_num_queries = 4

        allocine_pivot = providers_factories.AllocinePivotFactory()
        pivot_id = allocine_pivot.id

        db.session.expire(allocine_pivot)

        # when
        with assert_num_queries(allocine_pivot_expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="allocine", pivot_id=pivot_id))
            assert response.status_code == 200

    def test_get_update_pivot_form_boost(self, authenticated_client):
        # given

        boost_pivot = providers_factories.BoostCinemaDetailsFactory(cinemaUrl="http://example.com/boost1")

        db.session.expire(boost_pivot)

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="boost", pivot_id=boost_pivot.id))
            assert response.status_code == 200

    def test_get_update_pivot_form_cgr(self, authenticated_client):
        # given
        cgr_pivot = providers_factories.CGRCinemaDetailsFactory(cinemaUrl="http://example.com/another_web_service")

        db.session.expire(cgr_pivot)

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="cgr", pivot_id=cgr_pivot.id))
            assert response.status_code == 200

    def test_get_update_pivot_form_cineoffice(self, authenticated_client):
        # given

        cineoffice_pivot = providers_factories.CDSCinemaDetailsFactory()

        db.session.expire(cineoffice_pivot)

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="cineoffice", pivot_id=cineoffice_pivot.id))
            assert response.status_code == 200

    @patch("pcapi.routes.backoffice.pivots.contexts.ems.EMSContext.check_if_api_call_is_ok")
    def test_get_update_pivot_form_ems(self, mocked_healthcheck, authenticated_client):
        ems_pivot = providers_factories.EMSCinemaDetailsFactory()
        db.session.expire(ems_pivot)
        with assert_num_queries(6):
            response = authenticated_client.get(url_for(self.endpoint, name="ems", pivot_id=ems_pivot.id))
            assert response.status_code == 200


class UpdatePivotTest(PostEndpointHelper):
    endpoint = "backoffice_web.pivots.update_pivot"
    endpoint_kwargs = {"name": "allocine", "pivot_id": 1}
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT

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
            "account_id": "account1er",
            "api_token": "==@/@414324rF!",
        }

        self.post_to_endpoint(authenticated_client, name="cineoffice", pivot_id=cineoffice_pivot.id, form=form)

        updated = providers_models.CDSCinemaDetails.query.one()
        assert updated.cinemaProviderPivot.idAtProvider == form["cinema_id"]
        assert updated.accountId == form["account_id"]
        assert updated.cinemaApiToken == form["api_token"]

    @patch("pcapi.routes.backoffice.pivots.contexts.ems.EMSContext.check_if_api_call_is_ok")
    def test_update_pivot_ems(self, mocked_healthcheck, authenticated_client):
        ems_pivot = providers_factories.EMSCinemaDetailsFactory()

        expected_data = {
            "cinema_id": "New cinema id",
            "last_version": "2023-01-01",
        }

        assert ems_pivot.cinemaProviderPivot.idAtProvider != "New cinema id"
        assert ems_pivot.lastVersion == 0

        self.post_to_endpoint(authenticated_client, name="ems", pivot_id=ems_pivot.id, form=expected_data)

        db.session.refresh(ems_pivot)

        assert ems_pivot.cinemaProviderPivot.idAtProvider == "New cinema id"
        assert ems_pivot.lastVersion == int(datetime(2023, 1, 1, 0, 0).timestamp())

    def test_update_pivot_cineoffice_with_forbidden_characters(self, authenticated_client):
        cineoffice_pivot = providers_factories.CDSCinemaDetailsFactory()

        form = {
            "cinema_id": "very unusual id",
            "account_id": "account id with forbidden chars !!",
            "api_token": "==@/@414324rF!",
        }

        response = self.post_to_endpoint(
            authenticated_client, name="cineoffice", pivot_id=cineoffice_pivot.id, form=form
        )

        updated = providers_models.CDSCinemaDetails.query.one()
        assert updated.cinemaProviderPivot.idAtProvider != form["cinema_id"]
        assert updated.accountId != form["account_id"]
        assert updated.cinemaApiToken != form["api_token"]

        redirected_response = authenticated_client.get(response.headers["location"])

        assert (
            "Le nom de compte ne peut pas contenir de caractères autres que chiffres, lettres et tirets"
            in html_parser.content_as_text(redirected_response.data)
        )


class DeleteProviderTest(PostEndpointHelper):
    endpoint = "backoffice_web.pivots.delete_pivot"
    endpoint_kwargs = {"name": "cgr", "pivot_id": 1}
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT

    def test_delete_pivot_allocine(self, authenticated_client):
        allocine_pivot = providers_factories.AllocinePivotFactory()

        self.post_to_endpoint(authenticated_client, name="allocine", pivot_id=allocine_pivot.id)

        db.session.refresh(allocine_pivot)

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

    def test_delete_pivot_ems(self, authenticated_client):
        ems_pivot = providers_factories.EMSCinemaDetailsFactory()

        self.post_to_endpoint(authenticated_client, name="ems", pivot_id=ems_pivot.id)

        assert not providers_models.EMSCinemaDetails.query.get(ems_pivot.id)
