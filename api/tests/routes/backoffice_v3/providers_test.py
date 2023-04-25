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


class GetProvidersPageTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.providers.get_providers"
    needed_permission = perm_models.Permissions.MANAGE_PROVIDERS

    def test_get_providers_page(self, authenticated_client):
        with assert_num_queries(2):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200


class ListProvidersTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.providers.list_providers"
    endpoint_kwargs = {"name": "allocine"}
    needed_permission = perm_models.Permissions.MANAGE_PROVIDERS

    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch a single provider with joinedload (1 query)
    expected_num_queries = 3

    def test_list_providers_allocine(self, authenticated_client):
        # given
        allocine_provider = providers_factories.AllocinePivotFactory()

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="allocine"))
            assert response.status_code == 200

        # then
        allocine_rows = html_parser.extract_table_rows(response.data)
        assert allocine_rows[0]["Id du Lieu"] == str(allocine_provider.venue.id)
        assert allocine_rows[0]["Lieu"] == allocine_provider.venue.name
        assert allocine_rows[0]["Identifiant cinéma (Allociné)"] == allocine_provider.theaterId
        assert allocine_rows[0]["Identifiant interne Allociné"] == allocine_provider.internalId

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
    def test_filter_providers_allocine(self, authenticated_client, query_string, expected_venues):
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

    def test_list_providers_boost(self, authenticated_client):
        # given
        boost_provider = providers_factories.BoostCinemaDetailsFactory()

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="boost"))
            assert response.status_code == 200

        # then
        boost_rows = html_parser.extract_table_rows(response.data)
        assert boost_rows[0]["Id du Lieu"] == str(boost_provider.cinemaProviderPivot.venue.id)
        assert boost_rows[0]["Lieu"] == boost_provider.cinemaProviderPivot.venue.name
        assert boost_rows[0]["Identifiant cinéma (Boost)"] == boost_provider.cinemaProviderPivot.idAtProvider
        assert boost_rows[0]["Nom de l'utilisateur (Boost)"] == boost_provider.username
        assert boost_rows[0]["Mot de passe (Boost)"] == boost_provider.password
        assert boost_rows[0]["URL du cinéma (Boost)"] == boost_provider.cinemaUrl

    @pytest.mark.skip(reason="TODO PC-21791")
    def test_filter_providers_boost(self, authenticated_client, query_string, expected_venues):
        pass  # TODO PC-21791

    def test_list_providers_cgr(self, authenticated_client):
        # given
        cgr_provider = providers_factories.CGRCinemaDetailsFactory()

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="cgr"))
            assert response.status_code == 200

        # then
        cgr_rows = html_parser.extract_table_rows(response.data)
        assert cgr_rows[0]["Id du Lieu"] == str(cgr_provider.cinemaProviderPivot.venue.id)
        assert cgr_rows[0]["Lieu"] == cgr_provider.cinemaProviderPivot.venue.name
        assert cgr_rows[0]["Identifiant cinéma (CGR)"] == cgr_provider.cinemaProviderPivot.idAtProvider
        assert cgr_rows[0]["URL du cinéma (CGR)"] == cgr_provider.cinemaUrl

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
    def test_filter_providers_cgr(self, authenticated_client, query_string, expected_venues):
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

    def test_list_providers_cineoffice(self, authenticated_client):
        # given
        cineoffice_provider = providers_factories.CDSCinemaDetailsFactory()

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="cineoffice"))
            assert response.status_code == 200

        # then
        cineoffice_rows = html_parser.extract_table_rows(response.data)
        assert cineoffice_rows[0]["Id du Lieu"] == str(cineoffice_provider.cinemaProviderPivot.venue.id)
        assert cineoffice_rows[0]["Lieu"] == cineoffice_provider.cinemaProviderPivot.venue.name
        assert cineoffice_rows[0]["Identifiant cinéma (CDS)"] == cineoffice_provider.cinemaProviderPivot.idAtProvider
        assert cineoffice_rows[0]["Nom de l'utilisateur (CDS)"] == cineoffice_provider.accountId
        assert cineoffice_rows[0]["Clé API (CDS)"] == cineoffice_provider.cinemaApiToken

    @pytest.mark.skip(reason="TODO PC-21792")
    def test_filter_providers_cineoffice(self, authenticated_client, query_string, expected_venues):
        pass  # TODO PC-21792


class GetCreateProviderFormTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.providers.get_create_provider_form"
    endpoint_kwargs = {"name": "allocine"}
    needed_permission = perm_models.Permissions.MANAGE_PROVIDERS

    # - fetch session (1 query)
    # - fetch user (1 query)
    expected_num_queries = 2

    def test_get_create_provider_form_allocine(self, authenticated_client):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="allocine"))
            assert response.status_code == 200

    def test_get_create_provider_form_boost(self, authenticated_client):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="boost"))
            assert response.status_code == 200

    def test_get_create_provider_form_cgr(self, authenticated_client):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="cgr"))
            assert response.status_code == 200

    def test_get_create_provider_form_cineoffice(self, authenticated_client):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="cineoffice"))
            assert response.status_code == 200


class CreateProviderTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.providers.create_provider"
    endpoint_kwargs = {"name": "allocine"}
    needed_permission = perm_models.Permissions.MANAGE_PROVIDERS

    def test_create_provider_allocine(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        form = {"venue_id": venue.id, "theater_id": "ABCDEFGHIJKLMNOPQR==", "internal_id": "P12345"}

        response = self.post_to_endpoint(authenticated_client, name="allocine", form=form)
        assert response.status_code == 303

        created = providers_models.AllocinePivot.query.one()
        assert created.venueId == venue.id
        assert created.theaterId == form["theater_id"]
        assert created.internalId == form["internal_id"]

    @pytest.mark.skip(reason="TODO PC-21791")
    def test_create_provider_boost(self, authenticated_client):
        pass  # TODO PC-21791

    def test_create_provider_cgr(self, requests_mock, authenticated_client):
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

    @pytest.mark.skip(reason="TODO PC-21792")
    def test_create_provider_cineoffice(self, authenticated_client):
        pass  # TODO PC-21792


class GetUpdateProviderFormTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.providers.get_update_provider_form"
    endpoint_kwargs = {"name": "allocine", "provider_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PROVIDERS

    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch provider (1 query)
    # - fetch venue to fill autocomplete (1 query)
    expected_num_queries = 4

    def test_get_update_provider_form_allocine(self, authenticated_client):
        # given
        allocine_provider = providers_factories.AllocinePivotFactory()
        provider_id = allocine_provider.id

        db.session.expire(allocine_provider)

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="allocine", provider_id=provider_id))
            assert response.status_code == 200

    @pytest.mark.skip(reason="TODO PC-21791")
    def test_get_update_provider_form_boost(self, authenticated_client):
        pass  # TODO PC-21791

    def test_get_update_provider_form_cgr(self, authenticated_client):
        # given
        # - fetch cgr cinema details (1 query)
        # - fetch session (1 query)
        # - fetch user (1 query)
        # - fetch provider (1 query)
        # - fetch venue for form validate (1 query)
        # - fetch venue to fill autocomplete (1 query)
        expected_num_queries = 6

        cgr_provider = providers_factories.CGRCinemaDetailsFactory(cinemaUrl="http://example.com/another_web_service")

        db.session.expire(cgr_provider)

        # when
        with assert_num_queries(expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="cgr", provider_id=cgr_provider.id))
            assert response.status_code == 200

    @pytest.mark.skip(reason="TODO PC-21792")
    def test_get_update_provider_form_cineoffice(self, authenticated_client):
        pass  # TODO PC-21792


class UpdateProviderTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.providers.update_provider"
    endpoint_kwargs = {"name": "allocine", "provider_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PROVIDERS

    def test_update_provider_allocine(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        provider_id = providers_factories.AllocinePivotFactory().id

        form = {"venue_id": venue.id, "theater_id": "ABCDEFGHIJKLMNOPQR==", "internal_id": "P12345"}

        response = self.post_to_endpoint(authenticated_client, name="allocine", provider_id=provider_id, form=form)
        assert response.status_code == 303

        updated = providers_models.AllocinePivot.query.one()
        assert updated.venueId == venue.id
        assert updated.theaterId == form["theater_id"]
        assert updated.internalId == form["internal_id"]

    @pytest.mark.skip(reason="TODO PC-21791")
    def test_update_provider_boost(self, authenticated_client):
        pass  # TODO PC-21791

    def test_update_provider_cgr(self, authenticated_client, requests_mock):
        requests_mock.get("http://example.com/another_web_service", text=soap_definitions.WEB_SERVICE_DEFINITION)
        requests_mock.post(
            "http://example.com/another_web_service", text=fixtures.cgr_response_template([fixtures.FILM_138473])
        )
        cgr_provider = providers_factories.CGRCinemaDetailsFactory()

        form = {
            "cinema_id": "idProvider1000",
            "cinema_url": "http://example.com/another_web_service",
            "password": "Azerty!123",
        }

        self.post_to_endpoint(authenticated_client, name="cgr", provider_id=cgr_provider.id, form=form)

        updated = providers_models.CGRCinemaDetails.query.one()
        assert updated.cinemaProviderPivot.idAtProvider == form["cinema_id"]
        assert updated.cinemaUrl == form["cinema_url"]
        assert updated.password == form["password"]

    @pytest.mark.skip(reason="TODO PC-21792")
    def test_update_provider_cineoffice(self, authenticated_client):
        pass  # TODO PC-21792


class DeleteProviderTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.providers.delete_provider"
    endpoint_kwargs = {"name": "cgr", "provider_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PROVIDERS

    @pytest.mark.skip(reason="TODO PC-21791")
    def test_delete_provider_boost(self, authenticated_client):
        pass  # TODO PC-21791

    def test_delete_provider_cgr(self, authenticated_client):
        cgr_provider = providers_factories.CGRCinemaDetailsFactory()

        self.post_to_endpoint(authenticated_client, name="cgr", provider_id=cgr_provider.id)

        assert not providers_models.CGRCinemaDetails.query.get(cgr_provider.id)

    @pytest.mark.skip(reason="TODO PC-21792")
    def test_delete_provider_cineoffice(self, authenticated_client):
        pass  # TODO PC-21792
