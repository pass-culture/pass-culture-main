import datetime
import logging
import random

from pcapi import settings
from pcapi.connectors.big_query.queries.offerer_stats import DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE
from pcapi.connectors.big_query.queries.offerer_stats import TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.categories import subcategories
from pcapi.core.educational import factories as educational_factories
from pcapi.core.external_bookings import factories as external_bookings_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers import models as providers_models
from pcapi.core.users import factories as users_factories
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration


logger = logging.getLogger(__name__)


def create_offerer_provider(
    name: str,
    isActive: bool = True,
    enabledForPro: bool = True,
    provider_name: str | None = None,
    with_ticketing_service: bool = False,
) -> tuple[offerers_models.Offerer, providers_models.Provider]:
    offerer = offerers_factories.OffererFactory.create(name=name)
    if provider_name is None:
        provider_name = name
    booking_url = None
    cancel_booking_url = None
    if with_ticketing_service:
        booking_url = settings.EXTERNAL_TICKETING_SERVICE_BOOKING_URL
        cancel_booking_url = settings.EXTERNAL_TICKETING_SERVICE_CANCEL_BOOKING_URL
    provider = providers_factories.PublicApiProviderFactory.create(
        name=provider_name,
        isActive=isActive,
        enabledForPro=enabledForPro,
        bookingExternalUrl=booking_url,
        cancelExternalUrl=cancel_booking_url,
        notificationExternalUrl=settings.EXTERNAL_NOTIFICATION_URL,
        hmacKey="S3cr3tK3y",
    )

    offerers_factories.ApiKeyFactory.create(
        offererId=offerer.id,
        prefix=f"{settings.ENV}_{offerer.id}",
        secret=f"clearSecret{offerer.id}",
        providerId=provider.id,
    )

    providers_factories.OffererProviderFactory.create(
        offerer=offerer,
        provider=provider,
    )
    return offerer, provider


def create_offerer_provider_with_offers(name: str, user_email: str) -> None:
    now = datetime.datetime.utcnow().replace(second=0, microsecond=0)
    in_five_days = now + datetime.timedelta(days=5)
    in_ten_days = now + datetime.timedelta(days=10)
    offerer, provider = create_offerer_provider(name, provider_name="TaylorManager", with_ticketing_service=True)
    user = users_factories.ProFactory.create(
        email=user_email,
        firstName="Pro",
        lastName="Api",
        phoneNumber="+33100000000",
    )
    offerers_factories.UserOffererFactory.create(offerer=offerer, user=user)
    first_venue = offerers_factories.VenueFactory.create(name="Zénith de Lisieux", managingOfferer=offerer)
    second_venue = offerers_factories.VenueFactory.create(name="Olympia de Besançon", managingOfferer=offerer)
    providers_factories.VenueProviderFactory.create(venue=first_venue, provider=provider)
    providers_factories.VenueProviderFactory.create(venue=second_venue, provider=provider)
    offers = []
    for i in range(10):
        offer = offers_factories.EventOfferFactory.create(
            name=f"Taylor à Lisieux {i}",
            venue=first_venue,
            subcategoryId=subcategories.CONCERT.id,
            lastProvider=provider,
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
            isDuo=bool(i % 3),
        )
        price_category = offers_factories.PriceCategoryFactory.create(offer=offer)

        stocks = []
        for _ in range(5):
            stocks.append(
                offers_factories.EventStockFactory.create(
                    offer=offer,
                    beginningDatetime=in_ten_days + datetime.timedelta(days=random.randint(0, 10)),
                    priceCategory=price_category,
                )
            )

        for _ in range(15):
            stock = random.choice(stocks)
            booking = bookings_factories.BookingFactory.create(
                quantity=random.randint(1, 2 if stock.offer.isDuo else 1),
                stock=stock,
                dateCreated=now
                + datetime.timedelta(
                    days=random.randint(0, 10), hours=random.randint(0, 23), minutes=random.randint(0, 59)
                ),
            )
            external_bookings_factories.ExternalBookingFactory.create(booking=booking)

        offers.append(offer)

    daily_views = []

    # For testing purpoes, we want the number of views per day to be the day of the month
    # Ex: 1st day of the month, 1 view, 2nd day of the month, 2 views, etc.
    number_of_views = 0
    for i in range(90):
        date = now - datetime.timedelta(days=i)
        number_of_views += date.day
        daily_views.append(offerers_models.OffererViewsModel(eventDate=date, numberOfViews=number_of_views))

    offerers_factories.OffererStatsFactory.create(
        offerer=offerer,
        syncDate=datetime.datetime.utcnow(),
        table=DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE,
        jsonData=offerers_models.OffererStatsData(daily_views=daily_views),
    )

    today = datetime.datetime.today()

    total_views_last_30_days = sum((today - datetime.timedelta(days=i)).day for i in range(90))

    top_offer = offers[0]
    offerers_factories.OffererStatsFactory.create(
        offerer=offerer,
        syncDate=datetime.datetime.utcnow(),
        table=TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE,
        jsonData=offerers_models.OffererStatsData(
            top_offers=[offerers_models.TopOffersData(offerId=top_offer.id, numberOfViews=today.day)],
            total_views_last_30_days=total_views_last_30_days,
        ),
    )
    offers_factories.HeadlineOfferFactory.create(offer=top_offer)

    offers_factories.EventStockFactory.create(
        offer__name="Taylor à Besançon !",
        offer__venue=second_venue,
        offer__subcategoryId=subcategories.CONCERT.id,
        offer__lastProvider=provider,
        beginningDatetime=in_five_days + datetime.timedelta(days=3),
        offer__withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
    )
    educational_factories.CollectiveStockFactory.create(
        collectiveOffer__name="Taylor à l'école",
        collectiveOffer__venue=first_venue,
        collectiveOffer__provider=provider,
        startDatetime=in_five_days,
    )
    educational_factories.CollectiveStockFactory.create(
        collectiveOffer__name="Taylor au lycée",
        collectiveOffer__venue=second_venue,
        collectiveOffer__provider=provider,
        startDatetime=in_five_days,
    )


@log_func_duration
def create_offerer_providers_for_apis() -> None:
    create_offerer_provider("TicketBusters")
    create_offerer_provider("MangaMania")
    create_offerer_provider("VinylVibes")
    create_offerer_provider_with_offers("Structure avec lieux synchronisés billetterie", "api@example.com")

    create_offerer_provider("Private distributor", isActive=True, enabledForPro=False)
    create_offerer_provider("Malicious RiotRecords", isActive=False, enabledForPro=True)

    logger.info("Create 5 offerer providers")
