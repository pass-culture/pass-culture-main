import logging

from pcapi import settings
from pcapi.core.offerers import factories as offerers_facotries
from pcapi.core.providers import factories as providers_factories


logger = logging.getLogger(__name__)


def create_offerer_provider(name: str, isActive: bool = True, enabledForPro: bool = True) -> None:
    offerer = offerers_facotries.OffererFactory(name=name)
    provider = providers_factories.ProviderFactory(
        name=name, localClass=None, isActive=isActive, enabledForPro=enabledForPro
    )

    offerers_facotries.ApiKeyFactory(
        offererId=offerer.id,
        prefix=f"{settings.ENV}_{offerer.id}",
        secret=f"clearSecret{offerer.id}",
        providerId=provider.id,
    )

    providers_factories.OffererProviderFactory(
        offerer=offerer,
        provider=provider,
    )


def create_offerer_providers_for_apis() -> None:
    create_offerer_provider("TicketBusters")
    create_offerer_provider("MangaMania")
    create_offerer_provider("VinylVibes")

    create_offerer_provider("Private distributor", isActive=True, enabledForPro=False)
    create_offerer_provider("Malicious RiotRecords", isActive=False, enabledForPro=True)

    logger.info("Create 5 offerer providers")
