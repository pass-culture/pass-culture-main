import pytest

import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.providers.repository import get_provider_enabled_for_pro_by_id


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
