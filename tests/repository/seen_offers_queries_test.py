from datetime import datetime

from models.seen_offers import SeenOffers
from repository import repository
from repository.seen_offers_queries import update_seen_offers
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue, create_user
from tests.model_creators.specific_creators import create_offer_with_event_product
from utils.human_ids import humanize


class UpdateSeenOffersTest:
    @clean_database
    def test_should_record_new_seen_offer_when_offer_is_seen_for_the_first_time(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        beneficiary = create_user(email='email1@example.com')
        repository.save(beneficiary, offer)

        seen_offers = [
            {"id": 'AB',
             "userId": humanize(beneficiary.id),
             "offerId": humanize(offer.id),
             "dateSeen": "2020-04-10T16:50:10.0Z"}
        ]

        # when
        update_seen_offers(seen_offers)

        # then
        assert SeenOffers.query.count() == 1
        seen_offer_db = SeenOffers.query.first()
        assert seen_offer_db.user == beneficiary
        assert seen_offer_db.offer == offer
        assert seen_offer_db.dateSeen == datetime(2020, 4, 10, 16, 50, 10)

    @clean_database
    def test_should_record_new_seen_offer_when_other_offer_is_seen_for_the_first_time(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer_1 = create_offer_with_event_product(venue)
        offer_2 = create_offer_with_event_product(venue)
        beneficiary = create_user(email='email1@example.com')
        repository.save(beneficiary, offer_1, offer_2)

        seen_offer = SeenOffers()
        seen_offer.id = 123
        seen_offer.user = beneficiary
        seen_offer.offer = offer_1
        seen_offer.dateSeen = datetime(2020, 4, 9, 15, 59, 11)
        repository.save(seen_offer)

        seen_offers = [
            {"id": 'AC',
             "userId": humanize(beneficiary.id),
             "offerId": humanize(offer_2.id),
             "dateSeen": "2020-04-10T16:50:10.0Z"}
        ]

        # when
        update_seen_offers(seen_offers)

        # then
        assert SeenOffers.query.count() == 2

        seen_offers_db = SeenOffers.query.all()
        first_seen_offer_db = seen_offers_db[0]
        second_seen_offers_db = seen_offers_db[1]

        assert first_seen_offer_db.offer == offer_1
        assert second_seen_offers_db.offer == offer_2

    @clean_database
    def test_should_update_dateSeen_when_offer_is_seen_for_the_second_time_by_same_user(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        beneficiary = create_user()
        repository.save(beneficiary, offer)

        seen_offer = SeenOffers()
        seen_offer.user = beneficiary
        seen_offer.offer = offer
        seen_offer.dateSeen = datetime(2020, 4, 9, 15, 59, 11)
        repository.save(seen_offer)

        seen_offers = [
            {"id": humanize(seen_offer.id), "userId": humanize(beneficiary.id),
             "offerId": humanize(offer.id),
             "dateSeen": "2020-04-10T16:50:10.0Z"}
        ]

        # when
        update_seen_offers(seen_offers)

        # then
        seen_offer_db = SeenOffers.query.first()
        assert seen_offer_db.dateSeen == datetime(2020, 4, 10, 16, 50, 10)

