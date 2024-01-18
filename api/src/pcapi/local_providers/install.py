import pcapi.core.providers.constants as providers_constants
import pcapi.core.providers.factories as providers_factories
import pcapi.local_providers


def install_local_providers() -> None:
    for class_name in pcapi.local_providers.__all__:
        provider_class = getattr(pcapi.local_providers, class_name)
        providers_factories.ProviderFactory(
            name=provider_class.name,
            localClass=class_name,
        )
    providers_factories.ProviderFactory(
        name="Pass Culture API Stocks",
        localClass=providers_constants.PASS_CULTURE_STOCKS_FAKE_CLASS_NAME,
        enabledForPro=False,
    )
    providers_factories.ProviderFactory(
        name="EMS",
        localClass=providers_constants.EMS_STOCKS_FAKE_CLASS_NAME,
    )
    providers_factories.ProviderFactory(
        name=providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME,
        enabledForPro=False,
    )
    providers_factories.ProviderFactory(
        name=providers_constants.ALLOCINE_PRODUCTS_PROVIDER_NAME,
        enabledForPro=False,
        localClass=None,
    )
