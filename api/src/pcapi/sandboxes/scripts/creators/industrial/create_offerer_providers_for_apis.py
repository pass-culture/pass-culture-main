import logging

from pcapi import settings
from pcapi.core.offerers import factories as offerers_facotries
from pcapi.core.providers import factories as providers_factories


logger = logging.getLogger(__name__)

ACTIVE_PROVIDERS = ["TicketBusters", "MangaMania", "VinylVibes"]


def create_offerer_provider(name: str, isActive: bool = True, enabledForPro: bool = True) -> None:
    offerer = offerers_facotries.OffererFactory(name=name)
    provider = providers_factories.ProviderFactory(
        name=name, localClass=None, isActive=isActive, enabledForPro=enabledForPro
    )
    providers_factories.OffererProviderFactory(
        offererId=offerer.id,
        providerId=provider.id,
    )
    offerers_facotries.ApiKeyFactory(
        offerer=offerer, prefix=f"{settings.ENV}_{offerer.id}", secret=f"clearSecret{offerer.id}"
    )


def create_offerer_providers_for_apis() -> None:
    for name in ACTIVE_PROVIDERS:
        create_offerer_provider(name)

    create_offerer_provider("Private distributor", isActive=True, enabledForPro=False)
    create_offerer_provider("Malicious RiotRecords", isActive=False, enabledForPro=True)

    logger.info("Create 5 offerer providers")
