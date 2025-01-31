import pytest

from pcapi.core.providers import factories as providers_factories
from pcapi.scripts.provider_clean_old_integration_data.main import clean_old_provider_data


@pytest.mark.usefixtures("db_session")
def test_clean_old_provider_data():
    provider_1 = providers_factories.ProviderFactory(name="Old Provider that should be deprecated")
    provider_already_deprecated = providers_factories.ProviderFactory(name="[DÉPRÉCIÉ] Old Provider")
    provider_3 = providers_factories.ProviderFactory()

    clean_old_provider_data([provider_1.id, provider_already_deprecated.id])

    # should be deprecated
    assert provider_1.name == "[DÉPRÉCIÉ] Old Provider that should be deprecated"
    assert not provider_1.enabledForPro
    assert not provider_1.isActive

    assert provider_already_deprecated.name == "[DÉPRÉCIÉ] Old Provider"
    assert not provider_already_deprecated.enabledForPro
    assert not provider_already_deprecated.isActive

    # should stay the same
    assert provider_3.enabledForPro
    assert provider_3.isActive
