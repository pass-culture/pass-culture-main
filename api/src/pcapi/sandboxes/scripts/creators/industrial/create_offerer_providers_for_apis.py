import datetime
import logging
import typing

from pcapi import settings
from pcapi.core.categories import subcategories
from pcapi.core.educational import factories as educational_factories
from pcapi.core.offerers import factories as offerers_facotries
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers import models as providers_models


logger = logging.getLogger(__name__)


def create_offerer_provider(
    name: str, isActive: bool = True, enabledForPro: bool = True
) -> typing.Tuple[offerers_models.Offerer, providers_models.Provider]:
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
    return offerer, provider


def create_offerer_provider_with_offers(name: str) -> None:
    in_five_days = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(days=5)
    offerer, provider = create_offerer_provider(name)
    first_venue = offerers_facotries.VenueFactory(name="Zénith de Lisieux", managingOfferer=offerer)
    second_venue = offerers_facotries.VenueFactory(name="Olympia de Besançon", managingOfferer=offerer)
    providers_factories.VenueProviderFactory(venue=first_venue, provider=provider)
    providers_factories.VenueProviderFactory(venue=second_venue, provider=provider)
    first_offer = offers_factories.EventOfferFactory(
        name="Taylor à Besançon !",
        venue=first_venue,
        subcategoryId=subcategories.CONCERT.id,
        lastProvider=provider,
    )
    offers_factories.EventStockFactory(
        offer=first_offer,
        beginningDatetime=in_five_days,
    )
    offers_factories.EventStockFactory(
        offer=first_offer,
        beginningDatetime=in_five_days + datetime.timedelta(days=1),
    )
    offers_factories.EventStockFactory(
        offer__name="Taylor à Lisieux !",
        offer__venue=second_venue,
        offer__subcategoryId=subcategories.CONCERT.id,
        offer__lastProvider=provider,
        beginningDatetime=in_five_days + datetime.timedelta(days=3),
    )
    educational_factories.CollectiveStockFactory(
        collectiveOffer__name="Taylor à l'école",
        collectiveOffer__venue=first_venue,
        collectiveOffer__provider=provider,
        beginningDatetime=in_five_days,
    )
    educational_factories.CollectiveStockFactory(
        collectiveOffer__name="Taylor au lycée",
        collectiveOffer__venue=second_venue,
        collectiveOffer__provider=provider,
        beginningDatetime=in_five_days,
    )


def create_offerer_providers_for_apis() -> None:
    create_offerer_provider("TicketBusters")
    create_offerer_provider("MangaMania")
    create_offerer_provider("VinylVibes")
    create_offerer_provider_with_offers("TaylorManager")

    create_offerer_provider("Private distributor", isActive=True, enabledForPro=False)
    create_offerer_provider("Malicious RiotRecords", isActive=False, enabledForPro=True)

    logger.info("Create 5 offerer providers")
