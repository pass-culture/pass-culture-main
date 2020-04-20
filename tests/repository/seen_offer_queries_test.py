from repository import repository
from repository.seen_offer_queries import find_by_offer_id_and_user_id
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue, create_user, create_seen_offer
from tests.model_creators.specific_creators import create_offer_with_event_product


class FindByOfferIdAndUserIdTest:
    @clean_database
    def test_should_return_seen_offer_if_matching_user_id_and_offer_id(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        beneficiary = create_user()
        seen_offer = create_seen_offer(offer, beneficiary)
        repository.save(seen_offer)

        # when
        queried_seen_offer = find_by_offer_id_and_user_id(offer.id, beneficiary.id)

        # then
        assert queried_seen_offer == seen_offer

    @clean_database
    def test_should_return_none_if_unmatching_user_id(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        beneficiary = create_user()
        seen_offer = create_seen_offer(offer, beneficiary)
        repository.save(seen_offer)

        # when
        queried_seen_offer = find_by_offer_id_and_user_id(offer.id, beneficiary.id + 1)

        # then
        assert queried_seen_offer is None

    @clean_database
    def test_should_return_none_if_unmatching_offer_id(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        beneficiary = create_user()
        seen_offer = create_seen_offer(offer, beneficiary)
        repository.save(seen_offer)

        # when
        queried_seen_offer = find_by_offer_id_and_user_id(offer.id +1, beneficiary.id)

        # then
        assert queried_seen_offer is None
