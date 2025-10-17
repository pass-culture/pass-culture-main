import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.educational.factories as educational_factories
import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.scripts.resurect_venue.main as resurect_venue
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


def test_read_input_file():
    file_data = [
        {
            "": "",
            "Batch number": "0",
            "jsonPayload.extra.collective_offer_ids": "",
            "jsonPayload.extra.collective_offer_playlist_ids": "",
            "jsonPayload.extra.collective_offer_template_ids": "",
            "jsonPayload.extra.destination_venue_id": "",
            "jsonPayload.extra.offer_ids": "",
            "jsonPayload.extra.offers_type": "",
            "jsonPayload.extra.origin_venue_id": "",
            "jsonPayload.message": "Starting to move offers from venue (origin): 120 to venue (destination): 220",
            "jsonPayload.module": "pcapi.scripts.move_offer.move_batch_offer",
            "jsonPayload.technical_message_id": "",
            "timestamp": "2025-01-01T01:00:00.000000000Z",
            "trace": "projects/passculture-metier-prod/traces/644c4036e9d24b2f96b57d731ffc4927",
        },
        {
            "": "",
            "Batch number": "0",
            "jsonPayload.extra.collective_offer_ids": "",
            "jsonPayload.extra.collective_offer_playlist_ids": "",
            "jsonPayload.extra.collective_offer_template_ids": "",
            "jsonPayload.extra.destination_venue_id": "",
            "jsonPayload.extra.offer_ids": "",
            "jsonPayload.extra.offers_type": "",
            "jsonPayload.extra.origin_venue_id": "",
            "jsonPayload.message": "Updated 4 bookings for offer 986",
            "jsonPayload.module": "pcapi.core.offers.api",
            "jsonPayload.technical_message_id": "",
            "timestamp": "2025-01-01T01:00:00.000000000Z",
            "trace": "projects/passculture-metier-prod/traces/644c4036e9d24b2f96b57d731ffc4927",
        },
        {
            "": "",
            "Batch number": "0",
            "jsonPayload.extra.collective_offer_ids": "",
            "jsonPayload.extra.collective_offer_playlist_ids": "",
            "jsonPayload.extra.collective_offer_template_ids": "",
            "jsonPayload.extra.destination_venue_id": "",
            "jsonPayload.extra.offer_ids": "",
            "jsonPayload.extra.offers_type": "",
            "jsonPayload.extra.origin_venue_id": "",
            "jsonPayload.message": "Updated 1 bookings for offer 385",
            "jsonPayload.module": "pcapi.core.offers.api",
            "jsonPayload.technical_message_id": "",
            "timestamp": "2025-01-01T01:00:00.000000000Z",
            "trace": "projects/passculture-metier-prod/traces/644c4036e9d24b2f96b57d731ffc4927",
        },
        {
            "": "",
            "Batch number": "0",
            "jsonPayload.extra.collective_offer_ids": "",
            "jsonPayload.extra.collective_offer_playlist_ids": "",
            "jsonPayload.extra.collective_offer_template_ids": "",
            "jsonPayload.extra.destination_venue_id": "220",
            "jsonPayload.extra.offer_ids": "[986,385]",
            "jsonPayload.extra.offers_type": "individual",
            "jsonPayload.extra.origin_venue_id": "120",
            "jsonPayload.message": "Individual offers' venue has changed",
            "jsonPayload.module": "pcapi.scripts.move_offer.move_batch_offer",
            "jsonPayload.technical_message_id": "offer.move",
            "timestamp": "2025-01-01T01:00:00.000000000Z",
            "trace": "projects/passculture-metier-prod/traces/644c4036e9d24b2f96b57d731ffc4927",
        },
        {
            "": "",
            "Batch number": "0",
            "jsonPayload.extra.collective_offer_ids": "[711,712]",
            "jsonPayload.extra.collective_offer_playlist_ids": "",
            "jsonPayload.extra.collective_offer_template_ids": "",
            "jsonPayload.extra.destination_venue_id": "220",
            "jsonPayload.extra.offer_ids": "",
            "jsonPayload.extra.offers_type": "collective",
            "jsonPayload.extra.origin_venue_id": "120",
            "jsonPayload.message": "Collective offers' venue has changed",
            "jsonPayload.module": "pcapi.scripts.move_offer.move_batch_offer",
            "jsonPayload.technical_message_id": "collective_offer.move",
            "timestamp": "2025-01-01T01:00:00.000000000Z",
            "trace": "projects/passculture-metier-prod/traces/644c4036e9d24b2f96b57d731ffc4927",
        },
        {
            "": "",
            "Batch number": "0",
            "jsonPayload.extra.collective_offer_ids": "",
            "jsonPayload.extra.collective_offer_playlist_ids": "",
            "jsonPayload.extra.collective_offer_template_ids": "[834,855]",
            "jsonPayload.extra.destination_venue_id": "220",
            "jsonPayload.extra.offer_ids": "",
            "jsonPayload.extra.offers_type": "collective",
            "jsonPayload.extra.origin_venue_id": "120",
            "jsonPayload.message": "Collective offer templates' venue has changed",
            "jsonPayload.module": "pcapi.scripts.move_offer.move_batch_offer",
            "jsonPayload.technical_message_id": "collective_offer_template.move",
            "timestamp": "2025-01-01T01:00:00.000000000Z",
            "trace": "projects/passculture-metier-prod/traces/644c4036e9d24b2f96b57d731ffc4927",
        },
        {
            "": "",
            "Batch number": "0",
            "jsonPayload.extra.collective_offer_ids": "",
            "jsonPayload.extra.collective_offer_playlist_ids": "[911,975]",
            "jsonPayload.extra.collective_offer_template_ids": "",
            "jsonPayload.extra.destination_venue_id": "220",
            "jsonPayload.extra.offer_ids": "",
            "jsonPayload.extra.offers_type": "collective",
            "jsonPayload.extra.origin_venue_id": "120",
            "jsonPayload.message": "Collective offer playlists' venue has changed",
            "jsonPayload.module": "pcapi.scripts.move_offer.move_batch_offer",
            "jsonPayload.technical_message_id": "collective_offer_playlist.move",
            "timestamp": "2025-01-01T01:00:00.000000000Z",
            "trace": "projects/passculture-metier-prod/traces/644c4036e9d24b2f96b57d731ffc4927",
        },
        {
            "": "",
            "Batch number": "0",
            "jsonPayload.extra.collective_offer_ids": "",
            "jsonPayload.extra.collective_offer_playlist_ids": "",
            "jsonPayload.extra.collective_offer_template_ids": "",
            "jsonPayload.extra.destination_venue_id": "",
            "jsonPayload.extra.offer_ids": "",
            "jsonPayload.extra.offers_type": "",
            "jsonPayload.extra.origin_venue_id": "",
            "jsonPayload.message": "Transfer done for venue 120 to venue 220",
            "jsonPayload.module": "pcapi.scripts.move_offer.move_batch_offer",
            "jsonPayload.technical_message_id": "",
            "timestamp": "2025-01-01T01:00:00.000000000Z",
            "trace": "projects/passculture-metier-prod/traces/644c4036e9d24b2f96b57d731ffc4927",
        },
        {
            "": "",
            "Batch number": "0",
            "jsonPayload.extra.collective_offer_ids": "",
            "jsonPayload.extra.collective_offer_playlist_ids": "",
            "jsonPayload.extra.collective_offer_template_ids": "",
            "jsonPayload.extra.destination_venue_id": "",
            "jsonPayload.extra.offer_ids": "",
            "jsonPayload.extra.offers_type": "",
            "jsonPayload.extra.origin_venue_id": "",
            "jsonPayload.message": "Starting to move offers from venue (origin): 550 to venue (destination): 220",
            "jsonPayload.module": "pcapi.scripts.move_offer.move_batch_offer",
            "jsonPayload.technical_message_id": "",
            "timestamp": "2025-01-01T01:00:00.000000000Z",
            "trace": "projects/passculture-metier-prod/traces/644c4036e9d24b2f96b57d731ffc4927",
        },
        {
            "": "",
            "Batch number": "0",
            "jsonPayload.extra.collective_offer_ids": "",
            "jsonPayload.extra.collective_offer_playlist_ids": "",
            "jsonPayload.extra.collective_offer_template_ids": "",
            "jsonPayload.extra.destination_venue_id": "",
            "jsonPayload.extra.offer_ids": "",
            "jsonPayload.extra.offers_type": "",
            "jsonPayload.extra.origin_venue_id": "",
            "jsonPayload.message": "Updated 12 bookings for offer 226790724",
            "jsonPayload.module": "pcapi.core.offers.api",
            "jsonPayload.technical_message_id": "",
            "timestamp": "2025-01-01T01:00:00.000000000Z",
            "trace": "projects/passculture-metier-prod/traces/644c4036e9d24b2f96b57d731ffc4927",
        },
        {
            "": "",
            "Batch number": "0",
            "jsonPayload.extra.collective_offer_ids": "",
            "jsonPayload.extra.collective_offer_playlist_ids": "",
            "jsonPayload.extra.collective_offer_template_ids": "",
            "jsonPayload.extra.destination_venue_id": "220",
            "jsonPayload.extra.offer_ids": "[226790724]",
            "jsonPayload.extra.offers_type": "individual",
            "jsonPayload.extra.origin_venue_id": "550",
            "jsonPayload.message": "Individual offers' venue has changed",
            "jsonPayload.module": "pcapi.scripts.move_offer.move_batch_offer",
            "jsonPayload.technical_message_id": "offer.move",
            "timestamp": "2025-01-01T01:00:00.000000000Z",
            "trace": "projects/passculture-metier-prod/traces/644c4036e9d24b2f96b57d731ffc4927",
        },
        {
            "": "",
            "Batch number": "0",
            "jsonPayload.extra.collective_offer_ids": "[]",
            "jsonPayload.extra.collective_offer_playlist_ids": "",
            "jsonPayload.extra.collective_offer_template_ids": "",
            "jsonPayload.extra.destination_venue_id": "220",
            "jsonPayload.extra.offer_ids": "",
            "jsonPayload.extra.offers_type": "collective",
            "jsonPayload.extra.origin_venue_id": "550",
            "jsonPayload.message": "Collective offers' venue has changed",
            "jsonPayload.module": "pcapi.scripts.move_offer.move_batch_offer",
            "jsonPayload.technical_message_id": "collective_offer.move",
            "timestamp": "2025-01-01T01:00:00.000000000Z",
            "trace": "projects/passculture-metier-prod/traces/644c4036e9d24b2f96b57d731ffc4927",
        },
        {
            "": "",
            "Batch number": "0",
            "jsonPayload.extra.collective_offer_ids": "",
            "jsonPayload.extra.collective_offer_playlist_ids": "",
            "jsonPayload.extra.collective_offer_template_ids": "[]",
            "jsonPayload.extra.destination_venue_id": "220",
            "jsonPayload.extra.offer_ids": "",
            "jsonPayload.extra.offers_type": "collective",
            "jsonPayload.extra.origin_venue_id": "550",
            "jsonPayload.message": "Collective offer templates' venue has changed",
            "jsonPayload.module": "pcapi.scripts.move_offer.move_batch_offer",
            "jsonPayload.technical_message_id": "collective_offer_template.move",
            "timestamp": "2025-01-01T01:00:00.000000000Z",
            "trace": "projects/passculture-metier-prod/traces/644c4036e9d24b2f96b57d731ffc4927",
        },
        {
            "": "",
            "Batch number": "0",
            "jsonPayload.extra.collective_offer_ids": "",
            "jsonPayload.extra.collective_offer_playlist_ids": "[]",
            "jsonPayload.extra.collective_offer_template_ids": "",
            "jsonPayload.extra.destination_venue_id": "220",
            "jsonPayload.extra.offer_ids": "",
            "jsonPayload.extra.offers_type": "collective",
            "jsonPayload.extra.origin_venue_id": "550",
            "jsonPayload.message": "Collective offer playlists' venue has changed",
            "jsonPayload.module": "pcapi.scripts.move_offer.move_batch_offer",
            "jsonPayload.technical_message_id": "collective_offer_playlist.move",
            "timestamp": "2025-01-01T01:00:00.000000000Z",
            "trace": "projects/passculture-metier-prod/traces/644c4036e9d24b2f96b57d731ffc4927",
        },
        {
            "": "",
            "Batch number": "0",
            "jsonPayload.extra.collective_offer_ids": "",
            "jsonPayload.extra.collective_offer_playlist_ids": "",
            "jsonPayload.extra.collective_offer_template_ids": "",
            "jsonPayload.extra.destination_venue_id": "",
            "jsonPayload.extra.offer_ids": "",
            "jsonPayload.extra.offers_type": "",
            "jsonPayload.extra.origin_venue_id": "",
            "jsonPayload.message": "Transfer done for venue 550 to venue 220",
            "jsonPayload.module": "pcapi.scripts.move_offer.move_batch_offer",
            "jsonPayload.technical_message_id": "",
            "timestamp": "2025-01-01T01:00:00.000000000Z",
            "trace": "projects/passculture-metier-prod/traces/644c4036e9d24b2f96b57d731ffc4927",
        },
    ]
    results = resurect_venue.get_objects_to_move(file_data, 120)
    assert results.offers == [986, 385]
    assert results.collective_offers == [711, 712]
    assert results.collective_offer_templates == [834, 855]


@pytest.mark.features(VENUE_REGULARIZATION=True)
def test_resurect_venue():
    origin_venue = offerers_factories.VenueFactory(siret=None, comment="bwaaaa", pricing_point="self")
    destination_venue = offerers_factories.VenueFactory(
        siret=None, comment="bwaaaa2", managingOfferer=origin_venue.managingOfferer, pricing_point=origin_venue
    )
    origin_venue_id = origin_venue.id
    destination_venue_id = destination_venue.id

    # offer - and their bookings - 1 and 3 are moved back, offer 2 is left unchanged
    offer1 = offers_factories.OfferFactory(venue=origin_venue)
    offer2 = offers_factories.OfferFactory(venue=origin_venue)
    offer3 = offers_factories.OfferFactory(venue=origin_venue)
    unchanged_booking = bookings_factories.UsedBookingFactory(stock__offer=offer2)
    booking = bookings_factories.UsedBookingFactory(stock__offer=offer3)
    reimbursed_booking = bookings_factories.ReimbursedBookingFactory(stock__offer=offer3)

    collective_offer1 = educational_factories.CollectiveOfferFactory(venue=origin_venue)
    collective_offer2 = educational_factories.CollectiveOfferFactory(venue=origin_venue)
    collective_offer3 = educational_factories.CollectiveOfferFactory(venue=origin_venue)
    unchanged_collective_booking = educational_factories.UsedCollectiveBookingFactory(
        collectiveStock__collectiveOffer=collective_offer2
    )
    collective_booking = educational_factories.UsedCollectiveBookingFactory(
        collectiveStock__collectiveOffer=collective_offer3
    )

    collective_offer_template1 = educational_factories.CollectiveOfferTemplateFactory(venue=origin_venue)
    collective_offer_template2 = educational_factories.CollectiveOfferTemplateFactory(venue=origin_venue)
    collective_offer_template3 = educational_factories.CollectiveOfferTemplateFactory(venue=origin_venue)

    # Add a price category label that should be moved but only exists on the origin venue
    price_category1 = offers_factories.PriceCategoryFactory(
        offer=offer1,
        priceCategoryLabel__venue=origin_venue,
        priceCategoryLabel__label="Price Cat 1",
    )
    assert price_category1.priceCategoryLabel.venueId == origin_venue_id

    price_category2 = offers_factories.PriceCategoryFactory(
        offer=offer2,
        priceCategoryLabel__venue=origin_venue,
        priceCategoryLabel__label="Price Cat 2",
    )
    assert price_category2.priceCategoryLabel.venueId == origin_venue_id

    # Add a price category label that exists on both venues
    origin_price_category_label3 = offers_factories.PriceCategoryLabelFactory(venue=origin_venue, label="Price Cat 3")
    offers_factories.PriceCategoryLabelFactory(venue=destination_venue, label="Price Cat 3")
    price_category3 = offers_factories.PriceCategoryFactory(
        offer=offer3, priceCategoryLabel=origin_price_category_label3
    )
    assert price_category3.priceCategoryLabel.venueId == origin_venue_id

    # Finance incidents
    unchanged_individual_incident = finance_factories.IndividualBookingFinanceIncidentFactory(
        booking=unchanged_booking, incident__venue=origin_venue
    )
    individual_incident = finance_factories.IndividualBookingFinanceIncidentFactory(
        booking=booking, incident__venue=origin_venue
    )
    unchanged_collective_incident = finance_factories.CollectiveBookingFinanceIncidentFactory(
        collectiveBooking=unchanged_collective_booking, incident__venue=origin_venue
    )
    individual_incident = finance_factories.CollectiveBookingFinanceIncidentFactory(
        collectiveBooking=collective_booking, incident__venue=origin_venue
    )

    # Add pricing data
    individual_finance_event1 = finance_factories.UsedBookingFinanceEventFactory(
        status=finance_models.FinanceEventStatus.PRICED,
        booking=unchanged_booking,
    )
    individual_pricing1 = finance_factories.PricingFactory(event=individual_finance_event1, booking=unchanged_booking)
    individual_finance_event2 = finance_factories.UsedBookingFinanceEventFactory(
        status=finance_models.FinanceEventStatus.PRICED,
        booking=booking,
    )
    individual_pricing2 = finance_factories.PricingFactory(event=individual_finance_event2, booking=booking)
    collective_finance_event1 = finance_factories.UsedCollectiveBookingFinanceEventFactory(
        status=finance_models.FinanceEventStatus.PRICED,
        collectiveBooking=unchanged_collective_booking,
    )
    collective_pricing1 = finance_factories.PricingFactory(
        event=collective_finance_event1, collectiveBooking=unchanged_collective_booking
    )
    collective_finance_event2 = finance_factories.UsedCollectiveBookingFinanceEventFactory(
        status=finance_models.FinanceEventStatus.PRICED,
        collectiveBooking=collective_booking,
    )
    collective_pricing2 = finance_factories.PricingFactory(
        event=collective_finance_event2, collectiveBooking=collective_booking
    )

    # We can't soft delete the venue earlier because factories would fail to find it
    destination_venue.isSoftDeleted = True
    db.session.add(destination_venue)
    db.session.flush()

    db.session.flush()
    resurect_venue.resurrect_venue(
        dry_run=False,
        origin_id=origin_venue_id,
        destination_id=destination_venue_id,
        objects_to_move=resurect_venue.ObjectsToMove(
            offers=[offer1.id, offer3.id],
            collective_offers=[collective_offer1.id, collective_offer3.id],
            collective_offer_templates=[collective_offer_template1.id, collective_offer_template3.id],
        ),
    )

    assert not destination_venue.isSoftDeleted

    assert offer1.venueId == destination_venue_id
    assert offer2.venueId == origin_venue_id
    assert offer3.venueId == destination_venue_id
    assert unchanged_booking.venueId == origin_venue_id
    assert booking.venueId == destination_venue_id
    assert reimbursed_booking.venueId == destination_venue_id

    assert collective_offer1.venueId == destination_venue_id
    assert collective_offer2.venueId == origin_venue_id
    assert collective_offer3.venueId == destination_venue_id

    assert collective_offer_template1.venueId == destination_venue_id
    assert collective_offer_template2.venueId == origin_venue_id
    assert collective_offer_template3.venueId == destination_venue_id

    assert price_category1.priceCategoryLabel.venueId == destination_venue_id
    assert price_category2.priceCategoryLabel.venueId == origin_venue_id
    assert price_category3.priceCategoryLabel.venueId == destination_venue_id

    assert unchanged_individual_incident.incident.venueId == origin_venue_id
    assert individual_incident.incident.venueId == destination_venue_id
    assert unchanged_collective_incident.incident.venueId == origin_venue_id
    assert individual_incident.incident.venueId == destination_venue_id

    assert individual_pricing1.event.venueId == origin_venue_id
    assert individual_pricing2.event.venueId == origin_venue_id
    assert collective_pricing1.event.venueId == origin_venue_id
    assert collective_pricing2.event.venueId == origin_venue_id
