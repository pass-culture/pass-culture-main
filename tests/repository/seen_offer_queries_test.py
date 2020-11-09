from datetime import datetime

from freezegun import freeze_time
import pytest

from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_seen_offer
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.models import SeenOffer
from pcapi.repository import repository
from pcapi.repository.seen_offer_queries import find_by_offer_id_and_user_id
from pcapi.repository.seen_offer_queries import remove_old_seen_offers


class FindByOfferIdAndUserIdTest:
    @pytest.mark.usefixtures("db_session")
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

    @pytest.mark.usefixtures("db_session")
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

    @pytest.mark.usefixtures("db_session")
    def test_should_return_none_if_unmatching_offer_id(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        beneficiary = create_user()
        seen_offer = create_seen_offer(offer, beneficiary)
        repository.save(seen_offer)

        # when
        queried_seen_offer = find_by_offer_id_and_user_id(offer.id + 1, beneficiary.id)

        # then
        assert queried_seen_offer is None


class RemoveOldSeenOffersTest:
    @pytest.mark.usefixtures("db_session")
    @freeze_time("2020-5-5 16:22:00")
    def test_should_remove_seen_offers_after_one_month(self, app):
        # given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer_1 = create_offer_with_thing_product(venue)
        offer_2 = create_offer_with_thing_product(venue)

        seen_offer_1 = create_seen_offer(offer_1, user, date_seen=datetime(2020, 4, 1, 16, 23, 0))
        seen_offer_2 = create_seen_offer(offer_2, user, date_seen=datetime(2020, 4, 5, 16, 23, 0))
        repository.save(seen_offer_1, seen_offer_2)

        # when
        remove_old_seen_offers()

        # then
        assert SeenOffer.query.count() == 1
        seen_offer = SeenOffer.query.one()
        assert seen_offer.dateSeen == seen_offer_2.dateSeen
