import datetime
import decimal

import faker
import pytz

from pcapi.core import search
from pcapi.core.categories import subcategories
from pcapi.core.offerers import generator as offerers_generator
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import constants as offers_constants
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import models as providers_models
from pcapi.models import db
from pcapi.utils import date as date_utils


def _create_cinema_offer(
    venue: offerers_models.Venue,
    offer_name: str,
    price: decimal.Decimal,
    is_duo: bool,
    timezone: str,
    provider: providers_models.Provider | None = None,
) -> offers_models.Offer:
    fake = faker.Faker(["fr-FR"])
    offer_description = fake.paragraph(nb_sentences=30)
    product = offers_factories.ProductFactory.create(
        subcategoryId=subcategories.SEANCE_CINE.id,
        description=offer_description,
        name=offer_name,
        durationMinutes=102,
        set_all_fields=True,
    )
    db.session.add(product)

    # if the venue is linked to a provider and this provider has a ticketing service
    # we link the offer to the ticketing service
    withdrawal_type = None
    if provider and provider.hasTicketingService:
        withdrawal_type = offers_models.WithdrawalTypeEnum.IN_APP

    offer = offers_factories.OfferFactory.create(
        isDuo=is_duo,
        name=offer_name,
        venue=venue,
        subcategoryId=subcategories.SEANCE_CINE.id,
        publicationDatetime=date_utils.get_naive_utc_now() - datetime.timedelta(days=1),
        product=product,
        withdrawalType=withdrawal_type,
        lastProvider=provider,
    )
    db.session.add(offer)
    mediation = offers_factories.MediationFactory.build(offer=offer, credit=fake.name())
    db.session.add(mediation)
    offer_metadata = offers_factories.OfferMetaDataFactory.build(
        videoUrl="https://www.youtube.com/watch?v=bX2Oz6l1Z2s",
        videoDuration=204,
        videoExternalId="bX2Oz6l1Z2s",
        videoThumbnailUrl="https://i.ytimg.com/vi/bX2Oz6l1Z2s/maxresdefault.jpg",
        videoTitle=fake.paragraph(nb_sentences=1),
        offer=offer,
    )
    db.session.add(offer_metadata)
    price_category = offers_factories.PriceCategoryFactory(
        offer=offer, label=offers_constants.DEFAULT_PRICE_LABEL, price=price
    )
    # Create screenings for the next 18 days separated by holes of 4 days
    future_day_delta = (0, 1, 2, 3, 7, 8, 9, 10, 14, 15, 16, 17)
    features = {
        9: (
            offers_constants.LanguageFeatures.VF,
            offers_constants.VideoFeatures.DOLBY_VISION_3D,
            offers_constants.VideoFeatures.LASER,
            offers_constants.SpecialEventFeatures.CINE_DEBAT,
            offers_constants.AudioAccessbilityFeatures.SUBTITLE_CCAP,
            offers_constants.MentalAccessbilityFeatures.RELAX,
            offers_constants.MotorAccessbilityFeatures.PMR,
            offers_constants.VisualAccessbilityFeatures.VISION,
        ),
        15: (
            offers_constants.LanguageFeatures.VO,
            offers_constants.VideoFeatures.IMAX,
            offers_constants.VideoFeatures.SPHERA,
            offers_constants.AudioFeatures.ATMOS,
            offers_constants.SpecialEventFeatures.ATELIER,
            offers_constants.AudioAccessbilityFeatures.STSME,
            offers_constants.MotorAccessbilityFeatures.PMR,
            offers_constants.VisualAccessbilityFeatures.VAST,
        ),
        18: (
            offers_constants.LanguageFeatures.VF,
            offers_constants.VideoFeatures.THREE_D,
            offers_constants.SpecialEventFeatures.CINE_DEBAT,
            offers_constants.AudioAccessbilityFeatures.BOUCLE_MAG,
            offers_constants.MentalAccessbilityFeatures.COGNITIF,
            offers_constants.MotorAccessbilityFeatures.MOBILITE,
            offers_constants.VisualAccessbilityFeatures.AD_GRETA,
        ),
        14: (
            offers_constants.LanguageFeatures.VO,
            offers_constants.VideoFeatures.FOUR_K,
        ),
        19: (
            offers_constants.LanguageFeatures.VF,
            offers_constants.AudioAccessbilityFeatures.AUDIO_HI,
            offers_constants.SpecialEventFeatures.SEANCE_UNIQUE,
        ),
    }

    for daydelta in future_day_delta:
        day = datetime.datetime.now(pytz.timezone(timezone)).replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + datetime.timedelta(days=daydelta)
        for hour in (9, 15, 18) if (daydelta % 2) else (14, 19):
            minute = ((hour - 9) // 3) * 15  # 0, 30, 45 or 15, 45
            beginning_datetime = date_utils.to_naive_utc_datetime(day.replace(hour=hour, minute=minute))
            stock = offers_factories.StockFactory.build(
                offer=offer,
                price=price,
                beginningDatetime=beginning_datetime,
                bookingLimitDatetime=beginning_datetime - datetime.timedelta(minutes=30),
                quantity=None,
                features=features[hour] if (daydelta % 3) else ["VF"],
                priceCategory=price_category,
            )
            db.session.add(stock)
    db.session.add(offer)
    return offer


def _get_or_create_venue_provider(
    venue: offerers_models.Venue,
    provider: providers_models.Provider,
) -> providers_models.VenueProvider:
    venue_provider = (
        db.session.query(providers_models.VenueProvider)
        .filter(
            providers_models.VenueProvider.venueId == venue.id,
            providers_models.VenueProvider.providerId == provider.id,
        )
        .one_or_none()
    )
    if not venue_provider:
        venue_provider = providers_models.VenueProvider(venue=venue, provider=provider)
        db.session.add(venue_provider)

    return venue_provider


def create_offer(
    offer_name: str,
    price: decimal.Decimal,
    subcategory_id: str,
    is_duo: bool,
    timezone: str,
    provider: providers_models.Provider | None = None,
    venue: offerers_models.Venue | None = None,
) -> offers_models.Offer | None:
    # For the moment this function can only generate offers having SEANCE_CINE subcategory
    offer = None
    if subcategory_id == subcategories.SEANCE_CINE.id:
        if not venue:
            venue = offerers_generator.create_venue(offerers_models.Activity.CINEMA, timezone)

        if provider:
            _get_or_create_venue_provider(venue=venue, provider=provider)

        offer = _create_cinema_offer(venue, offer_name, price, is_duo, timezone, provider=provider)

    if offer is not None and venue is not None:
        search.reindex_venue_ids([venue.id])
        search.reindex_offer_ids([offer.id])
    return offer


def deactivate_offer(offer: offers_models.Offer) -> None:
    from pcapi.core.offers import api as offers_api

    query = db.session.query(offers_models.Offer).filter(offers_models.Offer.id.in_([offer.id]))
    offers_api.batch_activate_offers(query, activate=False)
