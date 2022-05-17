import pytest

import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.models import Provider
from pcapi.core.providers.repository import get_enabled_providers_for_pro
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.providers.repository import get_provider_enabled_for_pro_by_id
from pcapi.core.providers.repository import get_providers_enabled_for_pro_excluding_specific_providers


class GetEnabledProvidersForProTest:
    @pytest.mark.usefixtures("db_session")
    def test_get_enabled_providers_for_pro(self, app):
        # Given
        Provider.query.delete()  # remove automatically added providers
        provider1 = providers_factories.AllocineProviderFactory(localClass="Truc", isActive=True, enabledForPro=True)
        providers_factories.APIProviderFactory(name="NotEnabledAPIProvider", isActive=True, enabledForPro=False)
        providers_factories.APIProviderFactory(name="InactiveAPIProvider", isActive=False, enabledForPro=True)
        providers_factories.APIProviderFactory(name="InactiveAPIProvider2", isActive=False, enabledForPro=False)
        provider2 = providers_factories.APIProviderFactory(name="Provider2", isActive=True, enabledForPro=True)

        # When
        enabled_providers = get_enabled_providers_for_pro()

        # Then
        assert len(enabled_providers) == 2
        assert provider1 in enabled_providers
        assert provider2 in enabled_providers


class GetProvidersEnabledForProExcludingSpecificProviderTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_get_actives_and_enabled_providers_for_pro(self, app):
        # Given
        Provider.query.delete()  # remove automatically added providers
        providers_factories.AllocineProviderFactory(name="Provider1", isActive=True, enabledForPro=True)
        providers_factories.APIProviderFactory(name="NotEnabledAPIProvider", isActive=True, enabledForPro=False)
        providers_factories.APIProviderFactory(name="InactiveAPIProvider", isActive=False, enabledForPro=True)
        provider = providers_factories.APIProviderFactory(name="Provider2", isActive=True, enabledForPro=True)

        # When
        providers = get_providers_enabled_for_pro_excluding_specific_providers(["AllocineStocks"])

        # Then
        assert providers == [provider]


class GetProviderEnabledForProByIdTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_no_provider_when_provider_is_not_active(self):
        provider = providers_factories.ProviderFactory(isActive=False)
        assert get_provider_enabled_for_pro_by_id(provider.id) is None

    @pytest.mark.usefixtures("db_session")
    def test_should_return_no_provider_when_provider_is_not_enabled_for_pro(self):
        provider = providers_factories.ProviderFactory(enabledForPro=False)
        assert get_provider_enabled_for_pro_by_id(provider.id) is None

    @pytest.mark.usefixtures("db_session")
    def test_should_return_provider_when_provider_is_enabled_for_pro_and_active(self):
        provider = providers_factories.ProviderFactory()
        assert get_provider_enabled_for_pro_by_id(provider.id) == provider


@pytest.mark.usefixtures("db_session")
def test_get_provider_by_local_class():
    provider = providers_factories.ProviderFactory(localClass="Dummy")
    assert get_provider_by_local_class("Dummy") == provider
    assert get_provider_by_local_class("Unknown") is None
