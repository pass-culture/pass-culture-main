import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.model_creators.generic_creators import create_provider
from pcapi.repository import repository
from pcapi.repository.provider_queries import get_enabled_providers_for_pro
from pcapi.repository.provider_queries import get_provider_by_local_class
from pcapi.repository.provider_queries import get_provider_enabled_for_pro_by_id
from pcapi.repository.provider_queries import get_providers_enabled_for_pro_excluding_specific_provider


class GetEnabledProvidersForProTest:
    @pytest.mark.usefixtures("db_session")
    def test_get_enabled_providers_for_pro(self, app):
        # Given
        offerers_factories.ProviderFactory(name="NotEnabledProvider", isActive=True, enabledForPro=False)
        offerers_factories.ProviderFactory(name="InactiveProvider", isActive=False, enabledForPro=True)
        offerers_factories.ProviderFactory(name="InactiveProvider2", isActive=False, enabledForPro=False)
        provider1 = offerers_factories.ProviderFactory(name="Provider1", isActive=True, enabledForPro=True)

        offerers_factories.APIProviderFactory(name="NotEnabledAPIProvider", isActive=True, enabledForPro=False)
        offerers_factories.APIProviderFactory(name="InactiveAPIProvider", isActive=False, enabledForPro=True)
        offerers_factories.APIProviderFactory(name="InactiveAPIProvider2", isActive=False, enabledForPro=False)
        provider2 = offerers_factories.APIProviderFactory(name="Provider2", isActive=True, enabledForPro=True)

        # When
        enabled_providers = get_enabled_providers_for_pro()

        # Then
        assert enabled_providers == [provider1, provider2]


class GetProvidersEnabledForProExcludingSpecificProviderTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_get_actives_and_enabled_providers_for_pro(self, app):
        # Given
        offerers_factories.ProviderFactory(
            name="AllocineProvider", localClass="AllocineStocks", isActive=True, enabledForPro=True
        )
        offerers_factories.ProviderFactory(name="NotEnabledProvider", isActive=True, enabledForPro=False)
        offerers_factories.ProviderFactory(name="InactiveProvider", isActive=False, enabledForPro=True)
        provider1 = offerers_factories.ProviderFactory(name="Provider1", isActive=True, enabledForPro=True)

        offerers_factories.APIProviderFactory(name="NotEnabledAPIProvider", isActive=True, enabledForPro=False)
        offerers_factories.APIProviderFactory(name="InactiveAPIProvider", isActive=False, enabledForPro=True)
        provider2 = offerers_factories.APIProviderFactory(name="Provider2", isActive=True, enabledForPro=True)

        # When
        providers = get_providers_enabled_for_pro_excluding_specific_provider("AllocineStocks")

        # Then
        assert providers == [provider1, provider2]


class GetProviderEnabledForProByIdTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_no_provider_when_provider_is_not_active(self, app):
        # Given
        provider = create_provider(local_class="OpenAgenda", is_active=False, is_enable_for_pro=True)
        repository.save(provider)

        # When
        provider = get_provider_enabled_for_pro_by_id(provider.id)

        # Then
        assert provider is None

    @pytest.mark.usefixtures("db_session")
    def test_should_return_no_provider_when_provider_is_not_enabled_for_pro(self, app):
        # Given
        provider = create_provider(local_class="OpenAgenda", is_active=True, is_enable_for_pro=False)
        repository.save(provider)

        # When
        provider = get_provider_enabled_for_pro_by_id(provider.id)

        # Then
        assert provider is None

    @pytest.mark.usefixtures("db_session")
    def test_should_return_provider_when_provider_is_enabled_for_pro_and_active(self, app):
        # Given
        existing_provider = create_provider(local_class="OpenAgenda", is_active=True, is_enable_for_pro=True)
        repository.save(existing_provider)

        # When
        provider = get_provider_enabled_for_pro_by_id(existing_provider.id)

        # Then
        assert provider == existing_provider


class GetProviderByLocalClassTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_provider_matching_local_class(self, app):
        # Given
        existing_provider = create_provider(local_class="OpenAgenda", is_active=True, is_enable_for_pro=True)
        repository.save(existing_provider)

        # When
        provider = get_provider_by_local_class("OpenAgenda")

        # Then
        assert provider == existing_provider

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_provider_when_no_local_class_matches(self, app):
        # When
        provider = get_provider_by_local_class("NonExistingProvider")

        # Then
        assert provider is None
