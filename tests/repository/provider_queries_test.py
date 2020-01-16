from repository.repository import Repository
from repository.provider_queries import get_enabled_providers_for_pro, \
    get_providers_enabled_for_pro_excluding_specific_provider, \
    get_provider_enabled_for_pro_by_id, get_provider_by_local_class
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_provider


class GetEnabledProvidersForProTest:
    @clean_database
    def test_get_enabled_providers_for_pro(self, app):
        # Given
        provider1 = create_provider(local_class='OpenAgenda', is_active=False, is_enable_for_pro=False)
        provider2 = create_provider(local_class='TiteLive', is_active=True, is_enable_for_pro=True)
        Repository.save(provider1, provider2)

        # When
        enabled_providers = get_enabled_providers_for_pro()

        # Then
        assert enabled_providers == [provider2]


class GetProvidersEnabledForProExcludingSpecificProviderTest:
    @clean_database
    def test_should_get_actives_and_enabled_providers_for_pro(self, app):
        # Given
        provider1 = create_provider(local_class='OpenAgenda', is_active=False, is_enable_for_pro=False)
        provider2 = create_provider(local_class='TiteLive', is_active=True, is_enable_for_pro=True)
        Repository.save(provider1, provider2)

        # When
        providers = get_providers_enabled_for_pro_excluding_specific_provider('AllocineStocks')

        # Then
        assert providers == [provider2]

    @clean_database
    def test_should_return_all_providers_actives_and_enabled_for_pro_except_excluded_provider(self, app):
        # Given
        provider1 = create_provider(local_class='OpenAgenda', is_active=True, is_enable_for_pro=True)
        provider2 = create_provider(local_class='TiteLive', is_active=True, is_enable_for_pro=True)
        Repository.save(provider1, provider2)

        # When
        providers = get_providers_enabled_for_pro_excluding_specific_provider('OpenAgenda')

        # Then
        assert providers == [provider2]


class GetProviderEnabledForProByIdTest:
    @clean_database
    def test_should_return_no_provider_when_provider_is_not_active(self, app):
        # Given
        provider = create_provider(local_class='OpenAgenda', is_active=False, is_enable_for_pro=True)
        Repository.save(provider)

        # When
        provider = get_provider_enabled_for_pro_by_id(provider.id)

        # Then
        assert provider is None

    @clean_database
    def test_should_return_no_provider_when_provider_is_not_enabled_for_pro(self, app):
        # Given
        provider = create_provider(local_class='OpenAgenda', is_active=True, is_enable_for_pro=False)
        Repository.save(provider)

        # When
        provider = get_provider_enabled_for_pro_by_id(provider.id)

        # Then
        assert provider is None

    @clean_database
    def test_should_return_provider_when_provider_is_enabled_for_pro_and_active(self, app):
        # Given
        existing_provider = create_provider(local_class='OpenAgenda', is_active=True, is_enable_for_pro=True)
        Repository.save(existing_provider)

        # When
        provider = get_provider_enabled_for_pro_by_id(existing_provider.id)

        # Then
        assert provider == existing_provider


class GetProviderByLocalClassTest:
    @clean_database
    def test_should_return_provider_matching_local_class(self, app):
        # Given
        existing_provider = create_provider(local_class='OpenAgenda', is_active=True, is_enable_for_pro=True)
        Repository.save(existing_provider)

        # When
        provider = get_provider_by_local_class('OpenAgenda')

        # Then
        assert provider == existing_provider

    @clean_database
    def test_should_not_return_provider_when_no_local_class_matches(self, app):
        # When
        provider = get_provider_by_local_class('NonExistingProvider')

        # Then
        assert provider is None
