from pcapi.core.providers.factories import ProviderFactory
import pcapi.local_providers


def install_local_providers():  # type: ignore [no-untyped-def]
    for class_name in pcapi.local_providers.__all__:
        provider_class = getattr(pcapi.local_providers, class_name)
        ProviderFactory(name=provider_class.name, localClass=class_name)
