import datetime
import decimal

import faker
import sqlalchemy as sa

from pcapi.connectors.acceslibre import ExpectedFieldsEnum as acceslibre_enum
from pcapi.core import search
from pcapi.core.categories import subcategories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.search import models as search_models
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils import siren as siren_utils
from pcapi.utils.date import timespan_str_to_numrange


def _create_offerer() -> offerers_models.Offerer:
    fake = faker.Faker(["fr-FR"])
    max_siren = db.session.scalar(
        sa.select(
            sa.func.max(
                sa.cast(sa.func.substr(offerers_models.Offerer.siren, 1, siren_utils.SIREN_LENGTH - 1), sa.Integer)
            )
        ).filter(offerers_models.Offerer.siren.notlike("NC%"))
    )

    new_siren = siren_utils.complete_siren_or_siret(f"{(max_siren or 0) + 1:0>8}")
    offerer = offerers_factories.OffererFactory.build(siren=new_siren, name=f"Structure TEST - {fake.company()}")
    db.session.add(offerer)
    return offerer


def _get_price_category_label(venue: offerers_models.Venue) -> offers_models.PriceCategoryLabel:
    label = (
        db.session.query(offers_models.PriceCategoryLabel)
        .filter(offers_models.PriceCategoryLabel.venueId == venue.id)
        .filter(offers_models.PriceCategoryLabel.label == "Tarif unique")
        .first()
    )
    return label or offers_factories.PriceCategoryLabelFactory.create(venue=venue)


def _create_cinema_offer(venue: offerers_models.Venue, offer_name: str, price: decimal.Decimal) -> offers_models.Offer:
    fake = faker.Faker(["fr-FR"])
    offer_description = fake.paragraph(nb_sentences=30)
    product = offers_factories.ProductFactory.create(
        subcategoryId=subcategories.SEANCE_CINE.id,
        description=offer_description,
        name=offer_name,
        durationMinutes=102,
    )
    db.session.add(product)
    offer = offers_factories.OfferFactory.build(
        name=offer_name,
        description=offer_description,
        venue=venue,
        subcategoryId=subcategories.SEANCE_CINE.id,
        publicationDatetime=date_utils.get_naive_utc_now() - datetime.timedelta(days=1),
        product=product,
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
    price_category_label = _get_price_category_label(venue)
    price_category = offers_factories.PriceCategoryFactory(
        offer=offer, priceCategoryLabel=price_category_label, price=price
    )

    for daydelta in range(0, 20, 4):
        day = datetime.date.today() + datetime.timedelta(days=daydelta)
        for hour in (9, 15, 18):
            beginning_datetime = datetime.datetime.combine(day, datetime.time(hour=hour))
            stock = offers_factories.StockFactory.build(
                offer=offer,
                price=price,
                beginningDatetime=beginning_datetime,
                bookingLimitDatetime=beginning_datetime - datetime.timedelta(minutes=30),
                quantity=None,
                features=["VF"],
                priceCategory=price_category,
            )
            db.session.add(stock)
    db.session.add(offer)
    return offer


def _create_venue(offerer: offerers_models.Offerer, activity: offerers_models.Activity) -> offerers_models.Venue:
    fake = faker.Faker(["fr-FR"])
    venue = offerers_factories.VenueFactory.create(
        activity=activity,
        managingOfferer=offerer,
        name=offerer.name,
        venueTypeCode=offerers_models.VenueTypeCode.MOVIE,
        offererAddress__address__street=fake.street_address(),
        offererAddress__address__postalCode=fake.postcode(),
        withdrawalDetails=fake.paragraph(nb_sentences=6),
        description=fake.paragraph(nb_sentences=20),
    )
    db.session.add(venue)
    accessibility_provider = offerers_factories.AccessibilityProviderFactory.build(
        venue=venue,
        externalAccessibilityData={
            "access_modality": [acceslibre_enum.EXTERIOR_ONE_LEVEL.value, acceslibre_enum.ENTRANCE_PRM.value],
            "audio_description": [acceslibre_enum.AUDIODESCRIPTION_PERMANENT_SMARTPHONE.value],
            "deaf_and_hard_of_hearing_amenities": [
                acceslibre_enum.DEAF_AND_HARD_OF_HEARING_FIXED_INDUCTION_LOOP.value,
                acceslibre_enum.DEAF_AND_HARD_OF_HEARING_PORTABLE_INDUCTION_LOOP.value,
                acceslibre_enum.DEAF_AND_HARD_OF_HEARING_SIGN_LANGUAGE.value,
                acceslibre_enum.DEAF_AND_HARD_OF_HEARING_CUED_SPEECH.value,
                acceslibre_enum.DEAF_AND_HARD_OF_HEARING_SUBTITLE.value,
                acceslibre_enum.DEAF_AND_HARD_OF_HEARING_OTHER.value,
            ],
            "facilities": [acceslibre_enum.FACILITIES_ADAPTED.value],
            "sound_beacon": [acceslibre_enum.SOUND_BEACON.value],
            "trained_personnel": [acceslibre_enum.PERSONNEL_TRAINED.value],
            "transport_modality": [acceslibre_enum.PARKING_ADAPTED.value],
        },
    )
    db.session.add(accessibility_provider)
    opening_hours1 = offerers_factories.OpeningHoursFactory.build(
        weekday=offerers_models.Weekday.MONDAY,
        timespan=timespan_str_to_numrange([("10:00", "21:00")]),
        venue=venue,
    )
    opening_hours2 = offerers_factories.OpeningHoursFactory.build(
        weekday=offerers_models.Weekday.TUESDAY,
        timespan=timespan_str_to_numrange([("10:00", "13:00"), ("15:00", "21:00")]),
        venue=venue,
    )
    opening_hours3 = offerers_factories.OpeningHoursFactory.build(
        weekday=offerers_models.Weekday.WEDNESDAY,
        timespan=timespan_str_to_numrange([("10:00", "21:00")]),
        venue=venue,
    )
    opening_hours4 = offerers_factories.OpeningHoursFactory.build(
        weekday=offerers_models.Weekday.THURSDAY,
        timespan=timespan_str_to_numrange([("10:00", "13:00"), ("15:00", "21:00")]),
        venue=venue,
    )
    opening_hours5 = offerers_factories.OpeningHoursFactory.build(
        weekday=offerers_models.Weekday.FRIDAY,
        timespan=timespan_str_to_numrange([("10:00", "12:00"), ("13:30", "21:00")]),
        venue=venue,
    )
    opening_hours6 = offerers_factories.OpeningHoursFactory.build(
        weekday=offerers_models.Weekday.SUNDAY,
        timespan=timespan_str_to_numrange([("9:00", "21:00")]),
        venue=venue,
    )
    opening_hours7 = offerers_factories.OpeningHoursFactory.build(
        weekday=offerers_models.Weekday.SATURDAY,
        timespan=timespan_str_to_numrange([("9:00", "12:00"), ("13:30", "20:30")]),
        venue=venue,
    )
    db.session.add_all(
        [opening_hours1, opening_hours2, opening_hours3, opening_hours4, opening_hours5, opening_hours6, opening_hours7]
    )
    return venue


def create_offer(offer_name: str, price: decimal.Decimal, subcategory_id: str) -> offers_models.Offer | None:
    # For the moment this function can only generate offers having SEANCE_CINE subcategory
    offerer = _create_offerer()
    offer = None
    venue = None
    if subcategory_id == subcategories.SEANCE_CINE.id:
        venue = _create_venue(offerer, offerers_models.Activity.CINEMA)
        offer = _create_cinema_offer(venue, offer_name, price)

    if offer is not None and venue is not None:
        search.async_index_venue_ids([venue.id], search_models.IndexationReason.VENUE_CREATION)
        search.async_index_offer_ids([offer.id], search_models.IndexationReason.OFFER_CREATION)
    return offer


def deactivate_offer(offer: offers_models.Offer) -> None:
    from pcapi.core.offers import api as offers_api

    query = db.session.query(offers_models.Offer).filter(offers_models.Offer.id.in_([offer.id]))
    offers_api.batch_update_offers(query, activate=False)
