from pcapi.core.providers.models import Provider
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.repository import repository


def activate_provider(provider_classname: str) -> Provider:
    provider = get_provider_by_local_class(provider_classname)
    provider.isActive = True
    provider.enabledForPro = True
    repository.save(provider)
    return provider
