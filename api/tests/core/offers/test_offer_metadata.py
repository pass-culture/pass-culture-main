import datetime

import pytest

import pcapi.core.offers.factories as offers_factories
from pcapi.core.categories import subcategories
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers.offer_metadata import get_metadata_from_offer
from pcapi.core.providers.constants import BookFormat


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

    def test_can_have_a_description(self):
        offer = offers_factories.OfferFactory(description="Pass valable partout")

        metadata = get_metadata_from_offer(offer)

        assert metadata["description"] == "Pass valable partout"

    def test_can_have_no_description(self):
        offer = offers_factories.OfferFactory(description=None)

        metadata = get_metadata_from_offer(offer)

        assert "description" not in metadata

    class OfferTest:
        def should_have_an_offer(self):
            offer = offers_factories.OfferFactory()
            offers_factories.StockFactory(offer=offer, price=5.10)

            metadata = get_metadata_from_offer(offer)

            assert metadata["offers"]["@type"] == "AggregateOffer"

        def should_have_a_low_price(self):
            offer = offers_factories.OfferFactory()
            offers_factories.StockFactory(offer=offer, price=5.10)
            offers_factories.StockFactory(offer=offer, price=2)

            metadata = get_metadata_from_offer(offer)

            assert metadata["offers"]["lowPrice"] == "2.00"

        def should_have_a_low_price_when_no_active_stocks(self):
            offer = offers_factories.OfferFactory()
            offers_factories.StockFactory(offer=offer, isSoftDeleted=True, price=5.10)

            metadata = get_metadata_from_offer(offer)

            assert metadata["offers"]["lowPrice"] == "5.10"

        def should_have_a_price_currency(self):
            offer = offers_factories.OfferFactory()
            offers_factories.StockFactory(offer=offer, price=5.10)

            metadata = get_metadata_from_offer(offer)

            assert metadata["offers"]["priceCurrency"] == "EUR"

        def should_be_in_stock_when_offer_has_active_stocks(self):
            offer = offers_factories.OfferFactory()
            offers_factories.StockFactory(offer=offer)

            metadata = get_metadata_from_offer(offer)

            assert metadata["offers"]["availability"] == "https://schema.org/InStock"

        def should_be_out_of_stock_when_offer_has_no_active_stocks(self):
            offer = offers_factories.OfferFactory()
            offers_factories.StockFactory(offer=offer, isSoftDeleted=True)

            metadata = get_metadata_from_offer(offer)

            assert metadata["offers"]["availability"] == "https://schema.org/OutOfStock"

    class GivenAnEventTest:
        def should_describe_an_event(self):
            offer = offers_factories.EventOfferFactory()

            metadata = get_metadata_from_offer(offer)

            assert metadata["@type"] == "Event"

        def should_describe_an_event_for_a_concert(self):
            offer = offers_factories.OfferFactory(subcategoryId=subcategories.CONCERT.id)

            metadata = get_metadata_from_offer(offer)

            assert metadata["@type"] == "Event"

        def should_describe_an_event_for_a_festival(self):
            offer = offers_factories.OfferFactory(subcategoryId=subcategories.FESTIVAL_MUSIQUE.id)

            metadata = get_metadata_from_offer(offer)

            assert metadata["@type"] == "Event"

        def should_define_a_start_date(self):
            stock = offers_factories.EventStockFactory(beginningDatetime=datetime.datetime(2023, 5, 3, 12, 39, 0))

            metadata = get_metadata_from_offer(stock.offer)

            assert metadata["startDate"] == "2023-05-03T12:39"

        def should_define_a_start_date_when_no_active_stocks(self):
            stock = offers_factories.EventStockFactory(
                isSoftDeleted=True, beginningDatetime=datetime.datetime(2023, 5, 3, 12, 39, 0)
            )

            metadata = get_metadata_from_offer(stock.offer)

            assert metadata["startDate"] == "2023-05-03T12:39"

        def should_have_a_location_when_event_is_physical(self):
            offer = offers_factories.EventOfferFactory(
                venue__name="Le Poney qui tousse",
                venue__street="Rue du Poney qui tousse",
                venue__postalCode="75001",
                venue__city="Boulgourville",
                venue__latitude="47.097456",
                venue__longitude="-1.270040",
                url=None,
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

        def should_not_have_a_location_when_event_is_digital(self):
            offer = offers_factories.EventOfferFactory(url="https://digital-offer.com")

            metadata = get_metadata_from_offer(offer)

            assert "location" not in metadata

        def should_have_an_url(self):
            offer = offers_factories.EventOfferFactory(id=72180399)

            offers_factories.StockFactory(offer=offer)

            metadata = get_metadata_from_offer(offer)

            assert metadata["offers"]["url"] == "https://webapp-v2.example.com/offre/72180399"

        def should_have_online_event_attendance_mode(self):
            offer = offers_factories.EventOfferFactory(url="https://passculture.app/offre/72180399")

            metadata = get_metadata_from_offer(offer)

            assert metadata["eventAttendanceMode"] == "OnlineEventAttendanceMode"

        def should_have_offline_event_attendance_mode(self):
            offer = offers_factories.EventOfferFactory()

            metadata = get_metadata_from_offer(offer)

            assert metadata["eventAttendanceMode"] == "OfflineEventAttendanceMode"

        def should_have_valid_from_date(self):
            offer = offers_factories.EventOfferFactory(extraData={"releaseDate": "2000-01-01"})

            metadata = get_metadata_from_offer(offer)

            assert metadata["validFrom"] == "2000-01-01"

        def should_be_sold_out_when_offer_has_no_active_stocks(self):
            offer = offers_factories.EventOfferFactory()
            offers_factories.StockFactory(offer=offer, isSoftDeleted=True)

            metadata = get_metadata_from_offer(offer)

            assert metadata["offers"]["availability"] == "https://schema.org/SoldOut"

        def should_have_offer_location_when_available(self):
            venue = offerers_factories.VenueFactory(
                name="Le Poney qui tousse",
                street="Rue du Poney qui tousse",
                postalCode="75001",
                city="Boulgourville",
                latitude="47.097456",
                longitude="-1.270040",
            )
            address = geography_factories.AddressFactory(
                street="Rue du poney qui respire",
                postalCode="75002",
                city="Paris",
                latitude="47",
                longitude="-1",
            )
            offer_address = offerers_factories.OffererAddressFactory(
                address=address, label="Le grand poney qui respire"
            )
            offer = offers_factories.EventOfferFactory(venue=venue, offererAddress=offer_address)

            metadata = get_metadata_from_offer(offer)

            assert metadata["location"] == {
                "@type": "Place",
                "name": "Le grand poney qui respire",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "Rue du poney qui respire",
                    "postalCode": "75002",
                    "addressLocality": "Paris",
                },
                "geo": {
                    "@type": "GeoCoordinates",
                    "latitude": "47.00000",
                    "longitude": "-1.00000",
                },
            }

    class GivenABookTest:
        @pytest.mark.parametrize(
            "subcategoryId",
            [
                subcategories.LIVRE_PAPIER.id,
                subcategories.LIVRE_AUDIO_PHYSIQUE.id,
                subcategories.TELECHARGEMENT_LIVRE_AUDIO.id,
                subcategories.LIVRE_NUMERIQUE.id,
            ],
        )
        def should_describe_a_book(self, subcategoryId):
            offer = offers_factories.OfferFactory(subcategoryId=subcategoryId)

            metadata = get_metadata_from_offer(offer)

            assert metadata["@type"] == ["Product", "Book"]

        def should_define_an_id_and_url(self):
            offer = offers_factories.OfferFactory(id=12345, subcategoryId=subcategories.LIVRE_PAPIER.id)

            metadata = get_metadata_from_offer(offer)

            assert metadata["@id"] == "https://webapp-v2.example.com/offre/12345"
            assert metadata["url"] == "https://webapp-v2.example.com/offre/12345"

        def should_define_family_friendliness(self):
            stock = offers_factories.StockFactory(offer__subcategoryId=subcategories.LIVRE_PAPIER.id)

            metadata = get_metadata_from_offer(stock.offer)

            assert metadata["isFamilyFriendly"] == True

        def should_not_be_family_friendly_when_book_is_forbidden_for_underage(self):
            offer = offers_factories.OfferFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)

            metadata = get_metadata_from_offer(offer)

            assert metadata["isFamilyFriendly"] == False

        def should_define_an_author(self):
            offer = offers_factories.OfferFactory(
                subcategoryId=subcategories.LIVRE_PAPIER.id, extraData={"author": "John Doe"}
            )

            metadata = get_metadata_from_offer(offer)

            assert metadata["author"] == {"@type": "Person", "name": "John Doe"}

        class WorkExampleTest:
            def should_describe_a_book(self):
                offer = offers_factories.OfferFactory(
                    subcategoryId=subcategories.LIVRE_PAPIER.id,
                )

                metadata = get_metadata_from_offer(offer)

                assert metadata["workExample"]["@type"] == "Book"

            def should_define_an_id(self):
                offer = offers_factories.OfferFactory(
                    id="1234567",
                    subcategoryId=subcategories.LIVRE_PAPIER.id,
                )

                metadata = get_metadata_from_offer(offer)

                assert metadata["workExample"]["@id"] == "https://webapp-v2.example.com/offre/1234567"

            def should_define_a_language(self):
                offer = offers_factories.OfferFactory(
                    subcategoryId=subcategories.LIVRE_PAPIER.id,
                )

                metadata = get_metadata_from_offer(offer)

                assert metadata["workExample"]["inLanguage"] == "fr"

            def should_define_an_isbn(self):
                offer = offers_factories.OfferFactory(subcategoryId=subcategories.LIVRE_PAPIER.id, ean="9782371266124")

                metadata = get_metadata_from_offer(offer)

                assert metadata["gtin13"] == "9782371266124"
                assert metadata["workExample"]["isbn"] == "9782371266124"

            @pytest.mark.parametrize(
                ("subcategoryId", "expectedFormat"),
                [
                    (subcategories.LIVRE_PAPIER.id, "Hardcover"),
                    (subcategories.LIVRE_AUDIO_PHYSIQUE.id, "AudiobookFormat"),
                    (subcategories.TELECHARGEMENT_LIVRE_AUDIO.id, "AudiobookFormat"),
                    (subcategories.LIVRE_NUMERIQUE.id, "EBook"),
                ],
            )
            def should_define_a_book_format(self, subcategoryId, expectedFormat):
                offer = offers_factories.OfferFactory(
                    subcategoryId=subcategoryId,
                )

                metadata = get_metadata_from_offer(offer)

                assert metadata["workExample"]["bookFormat"] == f"https://schema.org/{expectedFormat}"

            def should_define_a_book_format_for_paperback_book(self):
                offer = offers_factories.OfferFactory(
                    subcategoryId=subcategories.LIVRE_PAPIER.id, extraData={"bookFormat": BookFormat.POCHE.name}
                )

                metadata = get_metadata_from_offer(offer)

                assert metadata["workExample"]["bookFormat"] == "https://schema.org/Paperback"

    class GivenAThingTest:
        def should_describe_a_product(self):
            offer = offers_factories.ThingOfferFactory()

            metadata = get_metadata_from_offer(offer)

            assert metadata["@type"] == "Product"
