import datetime
import logging
import random
import typing

from pcapi import settings
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.categories import subcategories
from pcapi.core.educational import factories as educational_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers import models as providers_models
from pcapi.core.users import factories as users_factories


logger = logging.getLogger(__name__)


def create_offerer_provider(
    name: str, isActive: bool = True, enabledForPro: bool = True, provider_name: str = None
) -> typing.Tuple[offerers_models.Offerer, providers_models.Provider]:
    offerer = offerers_factories.OffererFactory(name=name)
    if provider_name is None:
        provider_name = name
    provider = providers_factories.ProviderFactory(
        name=provider_name, localClass=None, isActive=isActive, enabledForPro=enabledForPro
    )

    offerers_factories.ApiKeyFactory(
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


def create_offerer_provider_with_offers(name: str, user_email: str) -> None:
    now = datetime.datetime.utcnow().replace(second=0, microsecond=0)
    in_five_days = now + datetime.timedelta(days=5)
    in_ten_days = now + datetime.timedelta(days=10)
    offerer, provider = create_offerer_provider(name, provider_name="TaylorManager")
    user = users_factories.ProFactory(
        email=user_email,
        firstName="taylor",
        lastName="young",
        phoneNumber="+33100000000",
    )
    offerers_factories.UserOffererFactory(offerer=offerer, user=user)
    first_venue = offerers_factories.VenueFactory(name="Zénith de Lisieux", managingOfferer=offerer)
    second_venue = offerers_factories.VenueFactory(name="Olympia de Besançon", managingOfferer=offerer)
    providers_factories.VenueProviderFactory(venue=first_venue, provider=provider)
    providers_factories.VenueProviderFactory(venue=second_venue, provider=provider)
    offers = []
    for i in range(10):
        offer = offers_factories.EventOfferFactory(
            name=f"Taylor à Lisieux {i}",
            venue=first_venue,
            subcategoryId=subcategories.CONCERT.id,
            lastProvider=provider,
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
        )
        price_category = offers_factories.PriceCategoryFactory(offer=offer)

        stocks = []
        for _ in range(5):
            stocks.append(
                offers_factories.EventStockFactory(
                    offer=offer,
                    beginningDatetime=in_ten_days + datetime.timedelta(days=random.randint(0, 10)),
                    priceCategory=price_category,
                )
            )

        for _ in range(15):
            bookings_factories.BookingFactory(
                quantity=random.randint(1, 2),
                stock=random.choice(stocks),
                dateCreated=now
                + datetime.timedelta(
                    days=random.randint(0, 10), hours=random.randint(0, 23), minutes=random.randint(0, 59)
                ),
            )

        offers.append(offer)

    offers_factories.EventStockFactory(
        offer__name="Taylor à Besançon !",
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
    create_offerer_provider_with_offers("Structure avec lieux synchronisés billetterie", "taylor@example.com")

    create_offerer_provider("Private distributor", isActive=True, enabledForPro=False)
    create_offerer_provider("Malicious RiotRecords", isActive=False, enabledForPro=True)

    logger.info("Create 5 offerer providers")
