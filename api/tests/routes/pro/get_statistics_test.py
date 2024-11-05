from unittest.mock import patch

import pytest

from pcapi.core import testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories

from tests.connectors.clickhouse import fixtures


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    @patch("pcapi.connectors.clickhouse.testing_backend.TestingBackend.run_query")
    def test_get_statistics_from_one_venue(self, run_query, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue_id = venue.id

        test_client = client.with_session_auth(email=user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select Offerer
        with testing.assert_num_queries(num_queries):
            run_query.return_value = fixtures.YEARLY_AGGREGATED_VENUE_REVENUE
            response = test_client.get(f"/get-statistics/?venue_ids={venue_id}")
            assert response.status_code == 200
        assert response.json == {
            "incomeByYear": {
                "2024": {
                    "expectedRevenue": {"collective": 13.12, "individual": 13.12, "total": 26.24},
                    "revenue": {"collective": 12.12, "individual": 12.12, "total": 24.24},
                }
            }
        }

    @patch("pcapi.connectors.clickhouse.testing_backend.TestingBackend.run_query")
    def test_get_statistics_from_multiple_venues(self, run_query, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue2 = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue_id = venue.id
        venue2_id = venue2.id

        test_client = client.with_session_auth(email=user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select Offerer
        with testing.assert_num_queries(num_queries):
            run_query.return_value = fixtures.YEARLY_AGGREGATED_VENUE_REVENUE
            response = test_client.get(f"/get-statistics/?venue_ids={venue_id}&venue_ids={venue2_id}")
            assert response.status_code == 200
        assert response.json == {
            "incomeByYear": {
                "2024": {
                    "expectedRevenue": {"collective": 13.12, "individual": 13.12, "total": 26.24},
                    "revenue": {"collective": 12.12, "individual": 12.12, "total": 24.24},
                }
            }
        }

    @patch("pcapi.connectors.clickhouse.testing_backend.TestingBackend.run_query")
    def test_get_statistics_multiple_years(self, run_query, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue2 = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue_id = venue.id
        venue2_id = venue2.id

        test_client = client.with_session_auth(email=user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select Offerer
        with testing.assert_num_queries(num_queries):
            run_query.return_value = fixtures.YEARLY_AGGREGATED_VENUE_REVENUE_MULTIPLE_YEARS
            response = test_client.get(f"/get-statistics/?venue_ids={venue_id}&venue_ids={venue2_id}")
            assert response.status_code == 200
        assert response.json == {
            "incomeByYear": {
                "2022": {
                    "expectedRevenue": {"collective": 22.12, "individual": 22.12, "total": 44.24},
                    "revenue": {"collective": 22.12, "individual": 22.12, "total": 44.24},
                },
                "2023": {},
                "2024": {
                    "expectedRevenue": {"collective": 13.12, "individual": 13.12, "total": 26.24},
                    "revenue": {"collective": 12.12, "individual": 12.12, "total": 24.24},
                },
            }
        }

    def test_get_statistics_empty_result(self, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue_id = venue.id

        test_client = client.with_session_auth(email=user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select Offerer
        with testing.assert_num_queries(num_queries):
            response = test_client.get(f"/get-statistics/?venue_ids={venue_id}")
            assert response.status_code == 200
        assert response.json == {"incomeByYear": {}}


@pytest.mark.usefixtures("db_session")
class Returns422Test:
    def test_get_statistics_with_no_venue_id_should_fail(self, client):
        user = users_factories.UserFactory()
        user2 = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user2, offerer=offerer)
        offerers_factories.VenueFactory(managingOfferer=offerer)

        test_client = client.with_session_auth(email=user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        with testing.assert_num_queries(num_queries):
            response = test_client.get(f"/get-statistics/")
            assert response.status_code == 422
        assert response.json["global"] == ["Vous devez préciser au moins un ID de partenaire culturel"]


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_get_statistics_from_not_owned_venue_should_fail(self, client):
        user = users_factories.UserFactory()
        user2 = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user2, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue_id = venue.id

        test_client = client.with_session_auth(email=user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select Offerer
        with testing.assert_num_queries(num_queries):
            response = test_client.get(f"/get-statistics/?venue_ids={venue_id}")
            assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."
        ]
