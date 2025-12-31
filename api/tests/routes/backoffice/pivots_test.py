import logging
from datetime import datetime
from unittest.mock import patch

import pytest
from flask import url_for

from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers import models as providers_models
from pcapi.core.providers import repository as providers_repository
from pcapi.core.providers.clients import cds_client
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.utils.crypto import decrypt

from tests.connectors.cgr import soap_definitions
from tests.local_providers.cinema_providers.cgr import fixtures

from .helpers import button as button_helpers
from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class GetPivotsTest(GetEndpointHelper):
    endpoint = "backoffice_web.pivots.get_pivots"
    needed_permission = perm_models.Permissions.READ_TECH_PARTNERS

    def test_get_pivots_page(self, authenticated_client):
        with assert_num_queries(1):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200


class ListPivotsTest(GetEndpointHelper):
    endpoint = "backoffice_web.pivots.list_pivots"
    endpoint_kwargs = {"name": "allocine"}
    needed_permission = perm_models.Permissions.READ_TECH_PARTNERS

    # - fetch session + user (1 query)
    # - fetch a single pivot with joinedload (1 query)
    expected_num_queries = 2

    def test_list_pivots_allocine(self, authenticated_client):
        allocine_pivot = providers_factories.AllocinePivotFactory()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="allocine"))
            assert response.status_code == 200

        allocine_rows = html_parser.extract_table_rows(response.data)
        assert allocine_rows[0]["Id du partenaire culturel"] == str(allocine_pivot.venue.id)
        assert allocine_rows[0]["Partenaire culturel"] == allocine_pivot.venue.name
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
        providers_factories.AllocinePivotFactory(
            venue__id=10, venue__name="Cinéma Edison", theaterId="ABCDEFGHIJKLMNOPQR==", internalId="P01891"
        )
        providers_factories.AllocinePivotFactory(
            venue__id=11, venue__name="Cinéma Lumière", theaterId="BCDEFGHIJKLMNOPQRS==", internalId="P01895"
        )
        providers_factories.AllocinePivotFactory(
            venue__id=12, venue__name="Chez les Frères Lumière", theaterId="CDEFGHIJKLMNOPQRST==", internalId="P18950"
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="allocine", q=query_string))
            assert response.status_code == 200

        allocine_rows = html_parser.extract_table_rows(response.data)
        assert {row["Partenaire culturel"] for row in allocine_rows} == expected_venues

    def test_list_pivots_boost(self, authenticated_client):
        boost_pivot = providers_factories.BoostCinemaDetailsFactory()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="boost"))
            assert response.status_code == 200

        boost_rows = html_parser.extract_table_rows(response.data)
        assert boost_rows[0]["Id du partenaire culturel"] == str(boost_pivot.cinemaProviderPivot.venue.id)
        assert boost_rows[0]["Partenaire culturel"] == boost_pivot.cinemaProviderPivot.venue.name
        assert boost_rows[0]["Identifiant cinéma (Boost)"] == boost_pivot.cinemaProviderPivot.idAtProvider
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

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="boost", q=query_string))
            assert response.status_code == 200

        cgr_rows = html_parser.extract_table_rows(response.data)
        assert {row["Partenaire culturel"] for row in cgr_rows} == expected_venues

    def test_list_pivots_cgr(self, authenticated_client):
        cgr_pivot = providers_factories.CGRCinemaDetailsFactory()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="cgr"))
            assert response.status_code == 200

        cgr_rows = html_parser.extract_table_rows(response.data)
        assert cgr_rows[0]["Id du partenaire culturel"] == str(cgr_pivot.cinemaProviderPivot.venue.id)
        assert cgr_rows[0]["Partenaire culturel"] == cgr_pivot.cinemaProviderPivot.venue.name
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

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="cgr", q=query_string))
            assert response.status_code == 200

        cgr_rows = html_parser.extract_table_rows(response.data)
        assert {row["Partenaire culturel"] for row in cgr_rows} == expected_venues

    def test_list_pivots_cineoffice(self, authenticated_client):
        cineoffice_pivot = providers_factories.CDSCinemaDetailsFactory()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="cineoffice"))
            assert response.status_code == 200

        cineoffice_rows = html_parser.extract_table_rows(response.data)
        assert cineoffice_rows[0]["Id du partenaire culturel"] == str(cineoffice_pivot.cinemaProviderPivot.venue.id)
        assert cineoffice_rows[0]["Partenaire culturel"] == cineoffice_pivot.cinemaProviderPivot.venue.name
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

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="cineoffice", q=query_string))
            assert response.status_code == 200

        cgr_rows = html_parser.extract_table_rows(response.data)
        assert {row["Partenaire culturel"] for row in cgr_rows} == expected_venues

    def test_list_pivots_ems(self, authenticated_client):
        ems_pivot = providers_factories.EMSCinemaDetailsFactory()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="ems"))
            assert response.status_code == 200

        ems_rows = html_parser.extract_table_rows(response.data)

        assert ems_rows[0]["Id du partenaire culturel"] == str(ems_pivot.cinemaProviderPivot.venue.id)
        assert ems_rows[0]["Partenaire culturel"] == ems_pivot.cinemaProviderPivot.venue.name
        assert ems_rows[0]["Identifiant cinéma (EMS)"] == ems_pivot.cinemaProviderPivot.idAtProvider
        assert ems_rows[0]["Dernière synchronisation réussie"] == ems_pivot.last_version_as_isoformat


class CreatePivotsButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.MANAGE_TECH_PARTNERS
    button_label = "Créer un pivot"

    @property
    def path(self):
        return url_for("backoffice_web.pivots.list_pivots", name="allocine")


class GetCreatePivotFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.pivots.get_create_pivot_form"
    endpoint_kwargs = {"name": "allocine"}
    needed_permission = perm_models.Permissions.MANAGE_TECH_PARTNERS

    # - fetch session + user (1 query)
    expected_num_queries = 1

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
    needed_permission = perm_models.Permissions.MANAGE_TECH_PARTNERS

    def test_create_pivot_allocine(self, authenticated_client, legit_user):
        venue = offerers_factories.VenueFactory()
        form = {"venue_id": venue.id, "theater_id": "ABCDEFGHIJKLMNOPQR==", "internal_id": "P12345"}

        response = self.post_to_endpoint(authenticated_client, name="allocine", form=form)
        assert response.status_code == 303

        created = db.session.query(providers_models.AllocinePivot).one()
        assert created.venueId == venue.id
        assert created.theaterId == form["theater_id"]
        assert created.internalId == form["internal_id"]
        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.PIVOT_CREATED
        assert action.authorUser == legit_user
        assert action.venueId == venue.id
        assert action.extraData["cinema_id"] == "ABCDEFGHIJKLMNOPQR=="
        assert action.extraData["pivot_name"] == "allocine"

    def test_create_pivot_boost(self, requests_mock, authenticated_client, legit_user):
        requests_mock.get("http://example.com/boost1/")
        requests_mock.post(
            "http://example.com/boost1/api/vendors/login",
            json={
                "code": 1,
                "message": "",
                "token": "toto",
            },
        )
        venue_id = offerers_factories.VenueFactory().id
        form = {
            "venue_id": venue_id,
            "cinema_id": "boost cinema 1",
            "cinema_url": "http://example.com/boost1/",
        }

        response = self.post_to_endpoint(authenticated_client, name="boost", form=form, follow_redirects=True)
        assert response.status_code == 200

        created = db.session.query(providers_models.BoostCinemaDetails).one()
        assert created.cinemaProviderPivot.venueId == venue_id
        assert created.cinemaProviderPivot.idAtProvider == form["cinema_id"]
        assert created.cinemaUrl == form["cinema_url"]
        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.PIVOT_CREATED
        assert action.authorUser == legit_user
        assert action.venueId == venue_id
        assert action.extraData["cinema_id"] == "boost cinema 1"
        assert action.extraData["pivot_name"] == "boost"

    def test_create_pivot_cgr(self, requests_mock, authenticated_client, legit_user):
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

        created = db.session.query(providers_models.CGRCinemaDetails).one()
        assert created.cinemaProviderPivot.venueId == venue_id
        assert created.cinemaProviderPivot.idAtProvider == form["cinema_id"]
        assert created.cinemaUrl == form["cinema_url"]
        assert decrypt(created.password) == form["password"]
        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.PIVOT_CREATED
        assert action.authorUser == legit_user
        assert action.venueId == venue_id
        assert action.extraData["cinema_id"] == "idProvider1111"
        assert action.extraData["pivot_name"] == "cgr"

    def test_create_pivot_cineoffice(self, authenticated_client, legit_user):
        venue_id = offerers_factories.VenueFactory().id
        form = {
            "venue_id": venue_id,
            "cinema_id": "cineoffice cinema 1",
            "account_id": "cineofficeaccount1",
            "api_token": "====?azerty!123",
        }

        self.post_to_endpoint(authenticated_client, name="cineoffice", form=form)

        created = db.session.query(providers_models.CDSCinemaDetails).one()
        assert created.cinemaProviderPivot.venueId == venue_id
        assert created.cinemaProviderPivot.idAtProvider == form["cinema_id"]
        assert created.accountId == form["account_id"]
        assert created.cinemaApiToken == form["api_token"]
        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.PIVOT_CREATED
        assert action.authorUser == legit_user
        assert action.venueId == venue_id
        assert action.extraData["cinema_id"] == "cineoffice cinema 1"
        assert action.extraData["pivot_name"] == "cineoffice"

    @patch("pcapi.routes.backoffice.pivots.contexts.ems.EMSContext.check_if_api_call_is_ok")
    def test_create_pivot_ems(self, mocked_healthcheck, authenticated_client, legit_user):
        mocked_healthcheck.return_value = None
        venue_id = offerers_factories.VenueFactory().id
        form = {
            "venue_id": venue_id,
            "cinema_id": "idAtProvider1",
        }

        self.post_to_endpoint(authenticated_client, name="ems", form=form)

        created: providers_models.EMSCinemaDetails = db.session.query(providers_models.EMSCinemaDetails).one()
        assert created.cinemaProviderPivot.venueId == venue_id
        assert created.cinemaProviderPivot.idAtProvider == form["cinema_id"]
        assert created.lastVersion == 0
        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.PIVOT_CREATED
        assert action.authorUser == legit_user
        assert action.venueId == venue_id
        assert action.extraData["cinema_id"] == "idAtProvider1"
        assert action.extraData["pivot_name"] == "ems"

    def test_create_pivot_cineoffice_with_forbidden_characters(self, authenticated_client):
        venue_id = offerers_factories.VenueFactory().id
        form = {
            "venue_id": venue_id,
            "cinema_id": "cineoffice cinema 1",
            "account_id": "cineoffice account with spaces",
            "api_token": "====?azerty!123",
        }

        response = self.post_to_endpoint(authenticated_client, name="cineoffice", form=form)

        created = db.session.query(providers_models.CDSCinemaDetails).one_or_none()
        assert created is None

        redirected_response = authenticated_client.get(response.headers["location"])

        assert (
            "Le nom de compte ne peut pas contenir de caractères autres que chiffres, lettres et tirets"
            in html_parser.content_as_text(redirected_response.data)
        )

    @patch(
        "pcapi.routes.backoffice.pivots.contexts.cineoffice.CineofficeContext.check_if_api_call_is_ok",
        side_effect=cds_client.CineDigitalServiceAPIException("Test"),
    )
    def test_create_pivot_with_external_booking_exception(self, mock_check_if_api_call_is_ok, authenticated_client):
        venue_id = offerers_factories.VenueFactory().id
        form = {
            "venue_id": venue_id,
            "cinema_id": "cineoffice cinema 1",
            "account_id": "cineofficeaccount1",
            "api_token": "====?azerty!123",
        }

        response = self.post_to_endpoint(authenticated_client, name="cineoffice", form=form, follow_redirects=True)

        mock_check_if_api_call_is_ok.assert_called_once()
        assert db.session.query(providers_models.CDSCinemaDetails).count() == 0
        assert html_parser.extract_alert(response.data) == "Une erreur s'est produite : Test"


class GetUpdatePivotFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.pivots.get_update_pivot_form"
    endpoint_kwargs = {"name": "allocine", "pivot_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_TECH_PARTNERS

    # - fetch session + user (1 query)
    # - fetch cinema details (1 query)
    # - fetch pivot (1 query)
    # - fetch venue for form validate (1 query)
    # - fetch venue to fill autocomplete (1 query)
    expected_num_queries = 5

    def test_get_update_pivot_form_allocine(self, authenticated_client):
        # - fetch session + user (1 query)
        # - fetch pivot (1 query)
        # - fetch venue to fill autocomplete (1 query)
        allocine_pivot_expected_num_queries = 3

        allocine_pivot = providers_factories.AllocinePivotFactory()
        pivot_id = allocine_pivot.id

        db.session.expire(allocine_pivot)

        with assert_num_queries(allocine_pivot_expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="allocine", pivot_id=pivot_id))
            assert response.status_code == 200

    def test_get_update_pivot_form_boost(self, authenticated_client):
        boost_pivot = providers_factories.BoostCinemaDetailsFactory(cinemaUrl="http://example.com/boost1")
        boost_pivot_id = boost_pivot.id

        db.session.expire(boost_pivot)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="boost", pivot_id=boost_pivot_id))
            assert response.status_code == 200

    def test_get_update_pivot_form_cgr(self, authenticated_client):
        cgr_pivot = providers_factories.CGRCinemaDetailsFactory(cinemaUrl="http://example.com/another_web_service")
        cgr_pivot_id = cgr_pivot.id

        db.session.expire(cgr_pivot)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="cgr", pivot_id=cgr_pivot_id))
            assert response.status_code == 200

    def test_get_update_pivot_form_cineoffice(self, authenticated_client):
        cineoffice_pivot = providers_factories.CDSCinemaDetailsFactory()
        cineoffice_pivot_id = cineoffice_pivot.id

        db.session.expire(cineoffice_pivot)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="cineoffice", pivot_id=cineoffice_pivot_id))
            assert response.status_code == 200

    @patch("pcapi.routes.backoffice.pivots.contexts.ems.EMSContext.check_if_api_call_is_ok")
    def test_get_update_pivot_form_ems(self, mocked_healthcheck, authenticated_client):
        ems_pivot = providers_factories.EMSCinemaDetailsFactory()
        ems_pivot_id = ems_pivot.id
        db.session.expire(ems_pivot)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, name="ems", pivot_id=ems_pivot_id))
            assert response.status_code == 200


class UpdatePivotTest(PostEndpointHelper):
    endpoint = "backoffice_web.pivots.update_pivot"
    endpoint_kwargs = {"name": "allocine", "pivot_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_TECH_PARTNERS

    def test_update_pivot_allocine(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        pivot_id = providers_factories.AllocinePivotFactory().id

        form = {"venue_id": venue.id, "theater_id": "ABCDEFGHIJKLMNOPQR==", "internal_id": "P12345"}

        response = self.post_to_endpoint(
            authenticated_client, name="allocine", pivot_id=pivot_id, form=form, follow_redirects=True
        )
        assert response.status_code == 200  # after redirect

        assert html_parser.extract_alert(response.data) == "Le pivot a été mis à jour"

        updated = db.session.query(providers_models.AllocinePivot).one()
        assert updated.venueId == venue.id
        assert updated.theaterId == form["theater_id"]
        assert updated.internalId == form["internal_id"]

    def test_update_pivot_boost(self, authenticated_client, requests_mock):
        requests_mock.get("http://example.com/boost1/", json={"key": "value"})
        requests_mock.post(
            "http://example.com/boost1/api/vendors/login?ignore_device=True",
            json={"code": 200, "message": "Login successful", "token": "new-token"},
        )
        boost_pivot = providers_factories.BoostCinemaDetailsFactory(cinemaUrl="http://example.com/boost0/")

        form = {
            "venue_id": str(boost_pivot.cinemaProviderPivot.venue.id),
            "cinema_id": "boost 1",
            "cinema_url": "http://example.com/boost1/",
        }

        response = self.post_to_endpoint(
            authenticated_client, name="boost", pivot_id=boost_pivot.id, form=form, follow_redirects=True
        )
        assert response.status_code == 200  # after redirect

        assert html_parser.extract_alerts(response.data) == ["Connexion à l'API OK.", "Le pivot a été mis à jour"]

        updated = db.session.query(providers_models.BoostCinemaDetails).one()
        assert updated.cinemaProviderPivot.idAtProvider == form["cinema_id"]
        assert updated.cinemaUrl == form["cinema_url"]

    def test_update_pivot_cgr(self, authenticated_client, requests_mock):
        requests_mock.get("http://example.com/another_web_service", text=soap_definitions.WEB_SERVICE_DEFINITION)
        requests_mock.post(
            "http://example.com/another_web_service", text=fixtures.cgr_response_template([fixtures.FILM_138473])
        )
        cgr_pivot = providers_factories.CGRCinemaDetailsFactory()

        form = {
            "venue_id": str(cgr_pivot.cinemaProviderPivot.venue.id),
            "cinema_id": "idProvider1000",
            "cinema_url": "http://example.com/another_web_service",
            "password": "Azerty!123",
        }

        response = self.post_to_endpoint(
            authenticated_client, name="cgr", pivot_id=cgr_pivot.id, form=form, follow_redirects=True
        )
        assert response.status_code == 200  # after redirect

        assert html_parser.extract_alerts(response.data) == ["Connexion à l'API CGR OK.", "Le pivot a été mis à jour"]

        updated = db.session.query(providers_models.CGRCinemaDetails).one()
        assert updated.cinemaProviderPivot.idAtProvider == form["cinema_id"]
        assert updated.cinemaUrl == form["cinema_url"]
        assert decrypt(updated.password) == form["password"]

    def test_update_pivot_cineoffice(self, authenticated_client, requests_mock):
        cineoffice_pivot = providers_factories.CDSCinemaDetailsFactory()
        requests_mock.get("https://account1er.test_cds_url/vad/rating?api_token===@/@414324rF!", json={"key": "value"})

        form = {
            "venue_id": str(cineoffice_pivot.cinemaProviderPivot.venue.id),
            "cinema_id": "cineoffice 1",
            "account_id": "account1er",
            "api_token": "==@/@414324rF!",
        }

        response = self.post_to_endpoint(
            authenticated_client, name="cineoffice", pivot_id=cineoffice_pivot.id, form=form, follow_redirects=True
        )
        assert response.status_code == 200  # after redirect

        assert html_parser.extract_alerts(response.data) == ["Connexion à l'API OK.", "Le pivot a été mis à jour"]

        updated = db.session.query(providers_models.CDSCinemaDetails).one()
        assert updated.cinemaProviderPivot.idAtProvider == form["cinema_id"]
        assert updated.accountId == form["account_id"]
        assert updated.cinemaApiToken == form["api_token"]

    @patch("pcapi.routes.backoffice.pivots.contexts.ems.EMSContext.check_if_api_call_is_ok")
    def test_update_pivot_ems(self, mocked_healthcheck, authenticated_client):
        ems_pivot = providers_factories.EMSCinemaDetailsFactory()

        expected_data = {
            "venue_id": str(ems_pivot.cinemaProviderPivot.venue.id),
            "cinema_id": "New cinema id",
            "last_version": "2023-01-01",
        }

        assert ems_pivot.cinemaProviderPivot.idAtProvider != "New cinema id"
        assert ems_pivot.lastVersion == 0

        response = self.post_to_endpoint(
            authenticated_client, name="ems", pivot_id=ems_pivot.id, form=expected_data, follow_redirects=True
        )
        assert response.status_code == 200  # after redirect

        assert html_parser.extract_alert(response.data) == "Le pivot a été mis à jour"

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
            authenticated_client, name="cineoffice", pivot_id=cineoffice_pivot.id, form=form, follow_redirects=True
        )

        updated = db.session.query(providers_models.CDSCinemaDetails).one()
        assert updated.cinemaProviderPivot.idAtProvider != form["cinema_id"]
        assert updated.accountId != form["account_id"]
        assert updated.cinemaApiToken != form["api_token"]

        assert (
            "Le nom de compte ne peut pas contenir de caractères autres que chiffres, lettres et tirets"
            in html_parser.content_as_text(response.data)
        )


class DeleteProviderTest(PostEndpointHelper):
    endpoint = "backoffice_web.pivots.delete_pivot"
    endpoint_kwargs = {"name": "cgr", "pivot_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_TECH_PARTNERS

    def test_delete_pivot_allocine(self, authenticated_client):
        allocine_venue_provider = providers_factories.AllocineVenueProviderFactory(isActive=False)
        allocine_pivot = providers_factories.AllocinePivotFactory(internalId=allocine_venue_provider.internalId)

        self.post_to_endpoint(authenticated_client, name="allocine", pivot_id=allocine_pivot.id)

        assert (
            not db.session.query(providers_models.AllocineVenueProvider)
            .filter_by(id=allocine_venue_provider.id)
            .first()
        )
        assert not db.session.query(providers_models.AllocinePivot).filter_by(id=allocine_pivot.id).first()

    def test_delete_pivot_boost_with_logout_error(self, authenticated_client, caplog):
        boost_pivot = providers_factories.BoostCinemaDetailsFactory()
        cinema_url = boost_pivot.cinemaUrl

        with caplog.at_level(logging.ERROR):
            self.post_to_endpoint(authenticated_client, name="boost", pivot_id=boost_pivot.id)

        assert not db.session.query(providers_models.BoostCinemaDetails).filter_by(id=boost_pivot.id).first()
        assert len(caplog.records) == 1
        assert caplog.records[0].message == "Unexpected error from Boost logout API"
        assert caplog.records[0].cinema_url == cinema_url

    def test_delete_pivot_boost_with_success_logout(self, authenticated_client, requests_mock):
        boost_pivot = providers_factories.BoostCinemaDetailsFactory()
        requests_mock.post(f"{boost_pivot.cinemaUrl}api/vendors/logout", json={"code": 200, "message": "string"})

        self.post_to_endpoint(authenticated_client, name="boost", pivot_id=boost_pivot.id)

        assert not db.session.query(providers_models.BoostCinemaDetails).filter_by(id=boost_pivot.id).first()

    def test_delete_pivot_cgr(self, authenticated_client):
        cgr_pivot = providers_factories.CGRCinemaDetailsFactory()

        self.post_to_endpoint(authenticated_client, name="cgr", pivot_id=cgr_pivot.id)

        assert not db.session.query(providers_models.CGRCinemaDetails).filter_by(id=cgr_pivot.id).first()

    def test_delete_pivot_cineoffice(self, authenticated_client):
        cineoffice_pivot = providers_factories.CDSCinemaDetailsFactory()

        self.post_to_endpoint(authenticated_client, name="cineoffice", pivot_id=cineoffice_pivot.id)

        assert not db.session.query(providers_models.CDSCinemaDetails).filter_by(id=cineoffice_pivot.id).first()

    def test_delete_pivot_ems(self, authenticated_client):
        ems_pivot = providers_factories.EMSCinemaDetailsFactory()

        self.post_to_endpoint(authenticated_client, name="ems", pivot_id=ems_pivot.id)

        assert not db.session.query(providers_models.EMSCinemaDetails).filter_by(id=ems_pivot.id).first()

    def test_delete_pivot_history_action(self, authenticated_client, legit_user):
        venue = offerers_factories.VenueFactory()
        cgr_provider = providers_repository.get_provider_by_local_class("CGRStocks")
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue,
            provider=cgr_provider,
            idAtProvider="idProvider1010",
        )
        cgr_pivot = providers_factories.CGRCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)

        response = self.post_to_endpoint(authenticated_client, name="cgr", pivot_id=cgr_pivot.id)
        assert response.status_code == 303
        assert not db.session.query(providers_models.CGRCinemaDetails).filter_by(id=cgr_pivot.id).first()
        action = db.session.query(history_models.ActionHistory).one()
        assert action.comment == "Pivot CGR"
        assert action.venueId == venue.id
        assert action.actionType == history_models.ActionType.PIVOT_DELETED
        assert action.authorUser == legit_user

    def test_delete_pivot_with_venue_provider(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        cgr_provider = providers_repository.get_provider_by_local_class("CGRStocks")
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue,
            provider=cgr_provider,
            idAtProvider="idProvider1010",
        )
        cgr_pivot = providers_factories.CGRCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)
        venue_provider = providers_factories.VenueProviderFactory(provider=cgr_provider, venue=venue)
        response = self.post_to_endpoint(authenticated_client, follow_redirects=True, name="cgr", pivot_id=cgr_pivot.id)
        assert response.status_code == 200
        assert db.session.query(providers_models.CGRCinemaDetails).filter_by(id=cgr_pivot.id).one()
        assert db.session.query(providers_models.VenueProvider).filter_by(id=venue_provider.id).one()
        assert html_parser.extract_alert(response.data) == (
            "Le pivot ne peut pas être supprimé si la synchronisation de ce cinéma est active. "
            "Supprimez la synchronisation et vous pourrez supprimer le pivot."
        )
