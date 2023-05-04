import datetime

import pytest

from pcapi.core.categories import subcategories_v2
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.offer_metadata import get_metadata_from_offer


pytestmark = pytest.mark.usefixtures("db_session")


class OfferMetadataTest:
    def should_always_have_a_context(self):
        offer = offers_factories.OfferFactory()

        metadata = get_metadata_from_offer(offer)

        assert metadata["@context"] == "https://schema.org"

    def should_always_have_a_name(self):
        offer = offers_factories.OfferFactory(
            name="Naheulbeuk Tome 1",
        )

        metadata = get_metadata_from_offer(offer)

        assert metadata["name"] == "Naheulbeuk Tome 1"

    def should_can_have_an_image(self):
        offer = offers_factories.OfferFactory()
        offers_factories.MediationFactory(id=111, offer=offer, thumbCount=1)

        metadata = get_metadata_from_offer(offer)

        assert metadata["image"] == "http://localhost/storage/thumbs/mediations/N4"

    def should_can_have_no_image(self):
        offer = offers_factories.OfferFactory()

        metadata = get_metadata_from_offer(offer)

        assert "image" not in metadata

    class GivenAnEventTest:
        def should_describe_an_event(self):
            offer = offers_factories.EventOfferFactory()

            metadata = get_metadata_from_offer(offer)

            assert metadata["@type"] == "Event"

        def should_describe_an_event_for_a_concert(self):
            offer = offers_factories.OfferFactory(product__subcategoryId=subcategories_v2.CONCERT.id)

            metadata = get_metadata_from_offer(offer)

            assert metadata["@type"] == "Event"

        def should_describe_an_event_for_a_festival(self):
            offer = offers_factories.OfferFactory(product__subcategoryId=subcategories_v2.FESTIVAL_MUSIQUE.id)

            metadata = get_metadata_from_offer(offer)

            assert metadata["@type"] == "Event"

        def should_define_a_start_date(self):
            stock = offers_factories.EventStockFactory(beginningDatetime=datetime.datetime(2023, 5, 3, 12, 39, 0))

            metadata = get_metadata_from_offer(stock.offer)

            assert metadata["startDate"] == "2023-05-03T12:39"

        def should_have_a_location(self):
            offer = offers_factories.EventOfferFactory(
                venue__name="Le Poney qui tousse",
                venue__address="Rue du Poney qui tousse",
                venue__postalCode="75001",
                venue__city="Boulgourville",
                venue__latitude="47.097456",
                venue__longitude="-1.270040",
            )

            metadata = get_metadata_from_offer(offer)

            assert metadata["location"] == {
                "@type": "Place",
                "name": "Le Poney qui tousse",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "Rue du Poney qui tousse",
                    "postalCode": "75001",
                    "addressLocality": "Boulgourville",
                },
                "geo": {
                    "@type": "GeoCoordinates",
                    "latitude": "47.09746",
                    "longitude": "-1.27004",
                },
            }

    class GivenAThingTest:
        def should_describe_a_product(self):
            offer = offers_factories.ThingOfferFactory()

            metadata = get_metadata_from_offer(offer)

            assert metadata["@type"] == "Product"
