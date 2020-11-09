from datetime import datetime

from freezegun import freeze_time
import pytest

from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_seen_offer
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.models import SeenOffer
from pcapi.repository import repository
from pcapi.use_cases.save_offer_seen_by_beneficiary import save_seen_offer


class SaveSeenOffersTest:
    @pytest.mark.usefixtures("db_session")
    @freeze_time("2020-04-10 16:50:10")
    def test_should_record_new_seen_offer_when_offer_is_seen_for_the_first_time(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        beneficiary = create_user()
        repository.save(beneficiary, offer)


        # when
        save_seen_offer(beneficiary.id, offer.id)

        # then
        assert SeenOffer.query.count() == 1

        seen_offers = SeenOffer.query.all()
        seen_offer = seen_offers[0]

        assert seen_offer.dateSeen == datetime(2020, 4, 10, 16, 50, 10)

    @pytest.mark.usefixtures("db_session")
    @freeze_time("2020-04-10 16:50:10")
    def test_should_update_date_seen_when_offer_is_seen_for_the_second_time_by_same_user(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        beneficiary = create_user()
        seen_offer = create_seen_offer(offer, beneficiary, datetime(2020, 4, 9, 15, 59, 11))
        repository.save(seen_offer)

        # when
        save_seen_offer(beneficiary.id, offer.id)

        # then
        seen_offer = SeenOffer.query.one()
        assert seen_offer.dateSeen == datetime(2020, 4, 10, 16, 50, 10)
