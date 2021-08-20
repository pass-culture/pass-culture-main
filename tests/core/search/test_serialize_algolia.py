from datetime import datetime
from datetime import timedelta
from decimal import Decimal

from freezegun import freeze_time
import pytest

from pcapi.core.categories import subcategories
from pcapi.core.search.backends.algolia import AlgoliaBackend
from pcapi.model_creators.generic_creators import create_criterion
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize


# FIXME (dbaty, 2021-06-21): I question the usefulness of these 600 lines of tests.


class BuildObjectTest:
    @pytest.mark.usefixtures("db_session")
    @freeze_time("2020-10-15 09:00:00")
    def test_should_return_algolia_object_with_required_information(self, app):
        # Given
        in_four_days = datetime.utcnow() + timedelta(days=4)
        three_days_ago = datetime.utcnow() + timedelta(days=-3)
        offerer = create_offerer(name="Offerer name", idx=1)
        venue = create_venue(
            offerer=offerer,
            city="Paris",
            idx=2,
            latitude=48.8638689,
            longitude=2.3380198,
            name="Venue name",
            public_name="Venue public name",
        )
        offer = create_offer_with_event_product(
            venue=venue,
            description="Un lit sous une rivière",
            withdrawal_details="A emporter sur place",
            idx=3,
            is_active=True,
            event_name="Event name",
            event_subcategory_id=subcategories.EVENEMENT_MUSIQUE.id,
            thumb_count=1,
            date_created=datetime(2020, 1, 1, 10, 0, 0),
            ranking_weight=3,
        )
        stock1 = create_stock(
            beginning_datetime=in_four_days,
            date_created=datetime(2020, 12, 5, 11, 0, 0),
            offer=offer,
            price=10,
            quantity=10,
        )
        stock2 = create_stock(
            beginning_datetime=in_four_days,
            date_created=datetime(2020, 12, 11, 8, 0, 0),
            offer=offer,
            price=20,
            quantity=10,
        )
        stock3 = create_stock(
            beginning_datetime=in_four_days,
            date_created=datetime(2020, 12, 1, 11, 0, 0),
            offer=offer,
            price=0,
            quantity=10,
        )
        stock4 = create_stock(
            beginning_datetime=in_four_days,
            date_created=datetime(2020, 12, 4, 7, 0, 0),
            is_soft_deleted=True,
            offer=offer,
            price=0,
            quantity=10,
        )
        stock5 = create_stock(
            beginning_datetime=three_days_ago,
            date_created=datetime(2020, 12, 7, 14, 0, 0),
            offer=offer,
            price=0,
            quantity=10,
        )
        repository.save(stock1, stock2, stock3, stock4, stock5)
        humanized_product_id = humanize(offer.product.id)

        # When
        result = AlgoliaBackend.serialize_offer(offer)

        # Then
        assert result == {
            "objectID": 3,
            "offer": {
                "author": None,
                "category": "MUSIQUE",
                "dateCreated": 1577872800.0,
                "dates": [1603098000.0, 1603098000.0, 1603098000.0],
                "description": "Un lit sous une rivière",
                "withdrawalDetails": "A emporter sur place",
                "id": "AM",
                "pk": 3,
                "isbn": None,
                "isDuo": False,
                "isEducational": False,
                "isDigital": False,
                "isEvent": True,
                "isThing": False,
                "label": "Concert ou festival",
                "name": "Event name",
                "musicSubType": None,
                "musicType": None,
                "performer": None,
                "prices": [Decimal("0.00"), Decimal("10.00"), Decimal("20.00")],
                "priceMin": Decimal("0.00"),
                "priceMax": Decimal("20.00"),
                "rankingWeight": 3,
                "searchGroup": subcategories.SearchGroupChoices.MUSIQUE.value,
                "showSubType": None,
                "showType": None,
                "speaker": None,
                "stageDirector": None,
                "stocksDateCreated": [1606820400.0, 1607166000.0, 1607673600.0],
                "thumbUrl": f"http://localhost/storage/thumbs/products/{humanized_product_id}",
                "tags": [],
                "times": [32400],
                "type": "Écouter",
                "visa": None,
            },
            "offerer": {
                "name": "Offerer name",
            },
            "venue": {
                "city": "Paris",
                "departementCode": "93",
                "name": "Venue name",
                "publicName": "Venue public name",
            },
            "_geoloc": {"lat": 48.86387, "lng": 2.33802},
        }

    @pytest.mark.usefixtures("db_session")
    def test_should_return_an_author_when_exists(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        offer.extraData = {"author": "MEFA"}
        stock = create_stock(offer=offer)
        repository.save(stock)

        # When
        result = AlgoliaBackend.serialize_offer(offer)

        # Then
        assert result["offer"]["author"] == "MEFA"

    @pytest.mark.usefixtures("db_session")
    def test_should_return_a_stage_director_when_exists(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        offer.extraData = {"stageDirector": "MEFA"}
        stock = create_stock(offer=offer)
        repository.save(stock)

        # When
        result = AlgoliaBackend.serialize_offer(offer)

        # Then
        assert result["offer"]["stageDirector"] == "MEFA"

    @pytest.mark.usefixtures("db_session")
    def test_should_return_a_visa_when_exists(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        offer.extraData = {"visa": "123456"}
        stock = create_stock(offer=offer)
        repository.save(stock)

        # When
        result = AlgoliaBackend.serialize_offer(offer)

        # Then
        assert result["offer"]["visa"] == "123456"
        assert result["offer"]["isbn"] == "123456"

    @pytest.mark.usefixtures("db_session")
    def test_should_return_an_isbn_when_exists(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        offer.extraData = {"isbn": "123456987", "visa": "123654"}
        stock = create_stock(offer=offer)
        repository.save(stock)

        # When
        result = AlgoliaBackend.serialize_offer(offer)

        # Then
        assert result["offer"]["isbn"] == "123456987"
        assert result["offer"]["visa"] == "123654"

    @pytest.mark.usefixtures("db_session")
    def test_should_return_a_speaker_when_exists(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        offer.extraData = {"speaker": "MEFA"}
        stock = create_stock(offer=offer)
        repository.save(stock)

        # When
        result = AlgoliaBackend.serialize_offer(offer)

        # Then
        assert result["offer"]["speaker"] == "MEFA"

    @pytest.mark.usefixtures("db_session")
    def test_should_return_a_performer_when_exists(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        offer.extraData = {"performer": "MEFA"}
        stock = create_stock(offer=offer)
        repository.save(stock)

        # When
        result = AlgoliaBackend.serialize_offer(offer)

        # Then
        assert result["offer"]["performer"] == "MEFA"

    @pytest.mark.usefixtures("db_session")
    def test_should_return_a_show_type_when_exists(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        offer.extraData = {"showType": "dance"}
        stock = create_stock(offer=offer)
        repository.save(stock)

        # When
        result = AlgoliaBackend.serialize_offer(offer)

        # Then
        assert result["offer"]["showType"] == "dance"

    @pytest.mark.usefixtures("db_session")
    def test_should_return_a_show_sub_type_when_exists(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        offer.extraData = {"showSubType": "urbaine"}
        stock = create_stock(offer=offer)
        repository.save(stock)

        # When
        result = AlgoliaBackend.serialize_offer(offer)

        # Then
        assert result["offer"]["showSubType"] == "urbaine"

    @pytest.mark.usefixtures("db_session")
    def test_should_return_a_music_type_when_exists(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        offer.extraData = {"musicType": "jazz"}
        stock = create_stock(offer=offer)
        repository.save(stock)

        # When
        result = AlgoliaBackend.serialize_offer(offer)

        # Then
        assert result["offer"]["musicType"] == "jazz"

    @pytest.mark.usefixtures("db_session")
    def test_should_return_a_music_sub_type_when_exists(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        offer.extraData = {"musicSubType": "fusion"}
        stock = create_stock(offer=offer)
        repository.save(stock)

        # When
        result = AlgoliaBackend.serialize_offer(offer)

        # Then
        assert result["offer"]["musicSubType"] == "fusion"

    @pytest.mark.usefixtures("db_session")
    def test_should_return_the_first_stock_price(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        stock1 = create_stock(offer=offer, price=7)
        stock2 = create_stock(offer=offer, price=5)
        stock3 = create_stock(offer=offer, price=10.3)
        repository.save(stock1, stock2, stock3)

        # When
        result = AlgoliaBackend.serialize_offer(offer)

        # Then
        assert result["offer"]["prices"] == [Decimal("5.00"), Decimal("7.00"), Decimal("10.30")]

    @pytest.mark.usefixtures("db_session")
    def test_should_return_default_coordinates_when_one_coordinate_is_missing(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer, latitude=None, longitude=12.13)
        offer = create_offer_with_thing_product(venue=venue)
        stock = create_stock(offer=offer)
        repository.save(stock)

        # When
        result = AlgoliaBackend.serialize_offer(offer)

        # Then
        assert result["_geoloc"]["lat"] == 47.158459
        assert result["_geoloc"]["lng"] == 2.409289

    @freeze_time("2020-10-15 09:00:00")
    @pytest.mark.usefixtures("db_session")
    def test_should_return_event_beginning_datetimes_as_timestamp_sorted_from_oldest_to_newest_when_event(self, app):
        # Given
        in_three_days = datetime.utcnow() + timedelta(days=3)
        in_four_days = datetime.utcnow() + timedelta(days=4)
        in_five_days = datetime.utcnow() + timedelta(days=5)
        in_ten_days = datetime.utcnow() + timedelta(days=10)
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_event_product(venue=venue)
        stock1 = create_stock(beginning_datetime=in_four_days, offer=offer)
        stock2 = create_stock(beginning_datetime=in_three_days, offer=offer)
        stock3 = create_stock(beginning_datetime=in_ten_days, offer=offer)
        stock4 = create_stock(beginning_datetime=in_five_days, offer=offer)
        repository.save(stock1, stock2, stock3, stock4)

        # When
        result = AlgoliaBackend.serialize_offer(offer)

        # Then
        assert result["offer"]["dates"] == [1603011600.0, 1603098000.0, 1603184400.0, 1603616400.0]

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_event_beginning_datetimes_as_timestamp_when_thing(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        stock1 = create_stock(offer=offer)
        stock2 = create_stock(offer=offer)
        repository.save(stock1, stock2)

        # When
        result = AlgoliaBackend.serialize_offer(offer)

        # Then
        assert result["offer"]["dates"] == []

    @freeze_time("2020-10-15 18:30:00")
    @pytest.mark.usefixtures("db_session")
    def test_should_return_event_beginning_times_in_seconds(self, app):
        # Given
        in_three_days_at_eighteen_thirty = datetime.utcnow() + timedelta(days=3)
        in_four_days_at_eighteen_thirty = datetime.utcnow() + timedelta(days=4)
        in_five_days_at_twenty_one_thirty = datetime.utcnow() + timedelta(days=5, hours=3, seconds=18)
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_event_product(venue=venue)
        stock1 = create_stock(beginning_datetime=in_three_days_at_eighteen_thirty, offer=offer)
        stock2 = create_stock(beginning_datetime=in_five_days_at_twenty_one_thirty, offer=offer)
        stock3 = create_stock(beginning_datetime=in_four_days_at_eighteen_thirty, offer=offer)
        repository.save(stock1, stock2, stock3)

        # When
        result = AlgoliaBackend.serialize_offer(offer)

        # Then
        eighteen_thirty_in_seconds = 66600
        twenty_one_thirty_in_seconds = 77418
        assert sorted(result["offer"]["times"]) == sorted([eighteen_thirty_in_seconds, twenty_one_thirty_in_seconds])

    @pytest.mark.usefixtures("db_session")
    def test_should_default_coordinates_when_offer_is_numeric(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer, latitude=None, longitude=None)
        offer = create_offer_with_thing_product(venue=venue, is_digital=True)
        stock = create_stock(offer=offer)
        repository.save(stock)

        # When
        result = AlgoliaBackend.serialize_offer(offer)

        # Then
        assert result["_geoloc"]["lat"] == 47.158459
        assert result["_geoloc"]["lng"] == 2.409289

    @pytest.mark.usefixtures("db_session")
    @freeze_time("2020-10-15 09:00:00")
    def test_should_return_algolia_object_with_one_tag_when_one_criterion(self, app):
        # Given
        in_four_days = datetime.utcnow() + timedelta(days=4)
        offerer = create_offerer(name="Offerer name", idx=1)
        venue = create_venue(
            offerer=offerer,
            city="Paris",
            idx=2,
            latitude=48.8638689,
            longitude=2.3380198,
            name="Venue name",
            public_name="Venue public name",
        )
        criterion = create_criterion(description="Ma super offre", name="Mon tag associé", score_delta=0)
        offer = create_offer_with_event_product(
            venue=venue,
            description="Un lit sous une rivière",
            withdrawal_details="A emporter sur place",
            idx=3,
            is_active=True,
            event_name="Event name",
            event_subcategory_id=subcategories.EVENEMENT_MUSIQUE.id,
            thumb_count=1,
            date_created=datetime(2020, 1, 1, 10, 0, 0),
            criteria=[criterion],
        )
        stock1 = create_stock(
            beginning_datetime=in_four_days,
            date_created=datetime(2020, 12, 5, 11, 0, 0),
            offer=offer,
            price=10,
            quantity=10,
        )
        repository.save(stock1)
        humanized_product_id = humanize(offer.product.id)

        # When
        result = AlgoliaBackend.serialize_offer(offer)

        # Then
        assert result == {
            "objectID": 3,
            "offer": {
                "author": None,
                "category": "MUSIQUE",
                "dateCreated": 1577872800.0,
                "dates": [1603098000.0],
                "description": "Un lit sous une rivière",
                "withdrawalDetails": "A emporter sur place",
                "id": "AM",
                "pk": 3,
                "isbn": None,
                "isDuo": False,
                "isEducational": False,
                "isDigital": False,
                "isEvent": True,
                "isThing": False,
                "label": "Concert ou festival",
                "name": "Event name",
                "musicSubType": None,
                "musicType": None,
                "performer": None,
                "prices": [Decimal("10.00")],
                "priceMin": Decimal("10.00"),
                "priceMax": Decimal("10.00"),
                "rankingWeight": None,
                "searchGroup": subcategories.SearchGroupChoices.MUSIQUE.value,
                "showSubType": None,
                "showType": None,
                "speaker": None,
                "stageDirector": None,
                "stocksDateCreated": [1607166000.0],
                "thumbUrl": f"http://localhost/storage/thumbs/products/{humanized_product_id}",
                "tags": ["Mon tag associé"],
                "times": [32400],
                "type": "Écouter",
                "visa": None,
            },
            "offerer": {
                "name": "Offerer name",
            },
            "venue": {
                "city": "Paris",
                "departementCode": "93",
                "name": "Venue name",
                "publicName": "Venue public name",
            },
            "_geoloc": {"lat": 48.86387, "lng": 2.33802},
        }

    @pytest.mark.usefixtures("db_session")
    @freeze_time("2020-10-15 09:00:00")
    def test_should_return_algolia_object_with_two_tags_when_two_criterion(self, app):
        # Given
        in_four_days = datetime.utcnow() + timedelta(days=4)
        offerer = create_offerer(name="Offerer name", idx=1)
        venue = create_venue(
            offerer=offerer,
            city="Paris",
            idx=2,
            latitude=48.8638689,
            longitude=2.3380198,
            name="Venue name",
            public_name="Venue public name",
        )
        criterion1 = create_criterion(description="Ma super offre", name="Mon tag associé", score_delta=0)
        criterion2 = create_criterion(description="Avengers", name="Iron Man mon super héros", score_delta=0)
        offer = create_offer_with_event_product(
            venue=venue,
            description="Un lit sous une rivière",
            withdrawal_details="A emporter sur place",
            idx=3,
            is_active=True,
            event_name="Event name",
            event_subcategory_id=subcategories.EVENEMENT_MUSIQUE.id,
            thumb_count=1,
            date_created=datetime(2020, 1, 1, 10, 0, 0),
            criteria=[criterion1, criterion2],
        )
        stock1 = create_stock(
            beginning_datetime=in_four_days,
            date_created=datetime(2020, 12, 5, 11, 0, 0),
            offer=offer,
            price=10,
            quantity=10,
        )
        repository.save(stock1)
        humanized_product_id = humanize(offer.product.id)

        # When
        result = AlgoliaBackend.serialize_offer(offer)

        # Then
        result["offer"]["tags"] = set(result["offer"]["tags"])
        assert result == {
            "objectID": 3,
            "offer": {
                "author": None,
                "category": "MUSIQUE",
                "dateCreated": 1577872800.0,
                "dates": [1603098000.0],
                "description": "Un lit sous une rivière",
                "withdrawalDetails": "A emporter sur place",
                "id": "AM",
                "pk": 3,
                "isbn": None,
                "isDuo": False,
                "isEducational": False,
                "isDigital": False,
                "isEvent": True,
                "isThing": False,
                "label": "Concert ou festival",
                "name": "Event name",
                "musicSubType": None,
                "musicType": None,
                "performer": None,
                "prices": [Decimal("10.00")],
                "priceMin": Decimal("10.00"),
                "priceMax": Decimal("10.00"),
                "rankingWeight": None,
                "searchGroup": subcategories.SearchGroupChoices.MUSIQUE.value,
                "showSubType": None,
                "showType": None,
                "speaker": None,
                "stageDirector": None,
                "stocksDateCreated": [1607166000.0],
                "thumbUrl": f"http://localhost/storage/thumbs/products/{humanized_product_id}",
                "tags": {"Mon tag associé", "Iron Man mon super héros"},
                "times": [32400],
                "type": "Écouter",
                "visa": None,
            },
            "offerer": {
                "name": "Offerer name",
            },
            "venue": {
                "city": "Paris",
                "departementCode": "93",
                "name": "Venue name",
                "publicName": "Venue public name",
            },
            "_geoloc": {"lat": 48.86387, "lng": 2.33802},
        }
