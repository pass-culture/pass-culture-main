import logging
from unittest import mock

import pydantic.v1 as pydantic_v1
import pytest
import time_machine

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers import repository as providers_repository
from pcapi.core.users import factories as users_factories
from pcapi.scripts.provider_migration import migrate_venue_provider


FAKE_VENUES_TO_MIGRATE_BY_DATE_AND_HOUR = {
    "07/10/24": {
        "10H": {
            "target_provider_id": 12,
            "venues_ids": [1, 3, 4],
            "comment": "Smart comment such as `Y-a pas à dire, les cotelettes c'est savoureux`",
        },
        "12H": {
            "target_provider_id": 14,
            "venues_ids": [2, 5],
            "comment": "Dumb comment such as `J'adore le salsifi`",
        },
    }
}


class GetMigrationDateAndHourKeysTest:
    @pytest.mark.parametrize(
        "utc_datetime,expected_target_date,expected_target_hour",
        [
            ("2024-10-07 18:29", "07/10/24", "21H"),
            ("2024-10-10 12:00", "10/10/24", "15H"),
            ("2024-10-10 11:59", "10/10/24", "14H"),
        ],
    )
    def test_should_return_tuple(self, utc_datetime, expected_target_date, expected_target_hour):
        with time_machine.travel(utc_datetime):
            target_day, target_hour = migrate_venue_provider.get_migration_date_and_hour_keys()
            assert target_day == expected_target_date
            assert target_hour == expected_target_hour


class RetrieveMigrationDataTest:
    @pytest.mark.parametrize(
        "data,target_day,target_hour,expected_logging_message,expected_migration_data",
        [
            ({}, "07/10/24", "10H", "(07/10/24) No venues to migrate today", None),
            (
                {"07/10/24": {"12H": {}}},
                "07/10/24",
                "10H",
                "(07/10/24 - 10H) No venues to migrate at this time of day",
                None,
            ),
            (
                FAKE_VENUES_TO_MIGRATE_BY_DATE_AND_HOUR,
                "07/10/24",
                "10H",
                "(07/10/24 - 10H) 3 venues to migrate to provider #12",
                migrate_venue_provider.MigrationData(
                    target_provider_id=12,
                    venues_ids=[1, 3, 4],
                    comment="Smart comment such as `Y-a pas à dire, les cotelettes c'est savoureux`",
                ),
            ),
        ],
    )
    def test_should_return_logging_message_and_migration_data(
        self, data, target_day, target_hour, expected_logging_message, expected_migration_data
    ):
        logging_message, migration_data = migrate_venue_provider._retrieve_migration_data(
            data,
            target_day=target_day,
            target_hour=target_hour,
        )
        assert logging_message == expected_logging_message
        assert migration_data == expected_migration_data

    def test_should_raise_an_error(self):
        with pytest.raises(pydantic_v1.ValidationError):
            migrate_venue_provider._retrieve_migration_data(
                {
                    "07/10/24": {
                        "10H": {
                            "target_provider_id": "heyyy!",
                            "venues_ids": ["coucou"],
                            "comment": None,
                        },
                    }
                },
                target_day="07/10/24",
                target_hour="10H",
            )


@pytest.mark.usefixtures("db_session")
@mock.patch(
    "pcapi.scripts.provider_migration.migrate_venue_provider.VENUES_TO_MIGRATE_BY_DATE_AND_HOUR",
    FAKE_VENUES_TO_MIGRATE_BY_DATE_AND_HOUR,
)
class ExecuteScheduledVenueProviderMigrationTest:
    @mock.patch("pcapi.scripts.provider_migration.migrate_venue_provider._migrate_venue_providers")
    @pytest.mark.parametrize(
        "target_day,target_hour,expected_logging_message",
        [
            ("06/10/24", "10H", "(06/10/24) No venues to migrate today"),
            ("07/10/24", "11H", "(07/10/24 - 11H) No venues to migrate at this time of day"),
        ],
    )
    def test_should_exit_because_not_data(
        self,
        _mock_migrate_venue_providers,
        caplog,
        target_day,
        target_hour,
        expected_logging_message,
    ):
        with caplog.at_level(logging.INFO):
            migrate_venue_provider.execute_scheduled_venue_provider_migration(target_day, target_hour)
            assert caplog.messages[0] == expected_logging_message
            _mock_migrate_venue_providers.assert_not_called()

    @mock.patch("pcapi.scripts.provider_migration.migrate_venue_provider._migrate_venue_providers")
    def test_should_exit_because_provider_not_found(self, _mock_migrate_venue_providers, caplog):
        with caplog.at_level(logging.ERROR):
            migrate_venue_provider.execute_scheduled_venue_provider_migration("07/10/24", "10H")
            assert caplog.messages[0] == "[❌ MIGRATION ABORTED] No provider was found for id 12"
            _mock_migrate_venue_providers.assert_not_called()

    @mock.patch("pcapi.scripts.provider_migration.migrate_venue_provider._migrate_venue_providers")
    def test_should_exit_because_missing_venues(self, _mock_migrate_venue_providers, caplog):
        providers_factories.PublicApiProviderFactory(id=12)
        offerers_factories.VenueFactory(id=3)
        with caplog.at_level(logging.ERROR):
            migrate_venue_provider.execute_scheduled_venue_provider_migration("07/10/24", "10H")
            assert caplog.messages[0] == "[❌ MIGRATION ABORTED] Some venues don't exist 1, 4"
            _mock_migrate_venue_providers.assert_not_called()

    @mock.patch("pcapi.scripts.provider_migration.migrate_venue_provider._migrate_venue_providers")
    def test_should_call_migrate_venue_provider(self, _mock_migrate_venue_providers, caplog):
        providers_factories.PublicApiProviderFactory(id=12)
        offerers_factories.VenueFactory(id=1)
        offerers_factories.VenueFactory(id=3)
        offerers_factories.VenueFactory(id=4)
        user = users_factories.UserFactory(id=2568200)
        with caplog.at_level(logging.INFO):
            migrate_venue_provider.execute_scheduled_venue_provider_migration("07/10/24", "10H")
            assert caplog.messages[0] == "(07/10/24 - 10H) 3 venues to migrate to provider #12"
            _mock_migrate_venue_providers.assert_called_with(
                provider_id=12,
                venues_ids=[1, 3, 4],
                migration_author=user,
                comment="Smart comment such as `Y-a pas à dire, les cotelettes c'est savoureux`",
            )

    def test_full_process(self, caplog):
        old_provider = providers_factories.ProviderFactory()
        very_old_provider = providers_factories.ProviderFactory()
        provider = providers_factories.PublicApiProviderFactory(id=12)
        providers_factories.OffererProviderFactory(provider=provider)
        venue_1 = offerers_factories.VenueFactory(id=1)
        providers_factories.VenueProviderFactory(venue=venue_1, provider=old_provider)
        providers_factories.VenueProviderFactory(venue=venue_1, provider=very_old_provider)
        venue_3 = offerers_factories.VenueFactory(id=3)
        providers_factories.VenueProviderFactory(venue=venue_3, provider=old_provider)
        venue_4 = offerers_factories.VenueFactory(id=4)
        users_factories.UserFactory(id=2568200)
        with caplog.at_level(logging.INFO):
            migrate_venue_provider.execute_scheduled_venue_provider_migration("07/10/24", "10H")
            # Test on logging messages
            assert caplog.messages[0] == "(07/10/24 - 10H) 3 venues to migrate to provider #12"
            # Venue #1
            assert caplog.messages[1] == f"Handling venue <#1 - {venue_1.name}>"
            assert caplog.messages[2] == f"Deleted VenueProvider for venue {venue_1.id}"
            assert caplog.records[2].extra == {"venue_id": venue_1.id, "provider_id": old_provider.id}
            assert caplog.messages[3] == f"Deleted VenueProvider for venue {venue_1.id}"
            assert caplog.records[3].extra == {"venue_id": venue_1.id, "provider_id": very_old_provider.id}
            assert caplog.messages[4] == f"La synchronisation d'offre a été activée"
            # Venue #3
            assert caplog.messages[5] == f"Handling venue <#3 - {venue_3.name}>"
            assert caplog.records[6].extra == {"venue_id": venue_3.id, "provider_id": old_provider.id}
            assert caplog.messages[6] == f"Deleted VenueProvider for venue {venue_3.id}"
            assert caplog.messages[7] == f"La synchronisation d'offre a été activée"
            # Venue #4
            assert caplog.messages[8] == f"Handling venue <#4 - {venue_4.name}>"
            assert caplog.messages[9] == f"La synchronisation d'offre a été activée"

            # Test on data
            # Old venue_provider should have been removed
            assert not providers_repository.get_venue_provider_by_venue_and_provider_ids(venue_1.id, old_provider.id)
            assert not providers_repository.get_venue_provider_by_venue_and_provider_ids(
                venue_1.id, very_old_provider.id
            )
            assert not providers_repository.get_venue_provider_by_venue_and_provider_ids(venue_3.id, old_provider.id)
            # New venue_provider should have been added
            assert providers_repository.get_venue_provider_by_venue_and_provider_ids(venue_1.id, provider.id).isActive
            assert providers_repository.get_venue_provider_by_venue_and_provider_ids(venue_1.id, provider.id).isActive
            assert providers_repository.get_venue_provider_by_venue_and_provider_ids(venue_3.id, provider.id).isActive
