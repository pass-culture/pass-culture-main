from unittest.mock import patch

import pytest

from pcapi.model_creators.generic_creators import create_criterion
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.models import OfferCriterion
from pcapi.repository import repository
from pcapi.scripts.add_criterion_to_goncourt_offers import GONCOURT_ISBNS
from pcapi.scripts.add_criterion_to_goncourt_offers import add_criterion_to_goncourt_offers
from pcapi.scripts.add_criterion_to_goncourt_offers import get_active_offers_matching_isbn


class AddCriterionToGoncourtOffersTest:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.scripts.add_criterion_to_goncourt_offers.OFFER_CRITERION_BATCH_SIZE", 1)
    def should_create_new_offer_criterion_for_matching_offers(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        goncourt_offer1 = create_offer_with_thing_product(venue=venue, id_at_providers="1")
        goncourt_offer1.extraData["isbn"] = "9782072904073"
        goncourt_offer2 = create_offer_with_thing_product(venue=venue, id_at_providers="2")
        goncourt_offer2.extraData["isbn"] = "9782072895098"
        criterion = create_criterion(name="Home_goncourtlyceens")
        repository.save(goncourt_offer1, goncourt_offer2, criterion)

        # When
        add_criterion_to_goncourt_offers()

        # Then
        assert OfferCriterion.query.count() == 2
        assert OfferCriterion.query.filter(OfferCriterion.offerId == goncourt_offer1.id).count() == 1
        assert OfferCriterion.query.filter(OfferCriterion.offerId == goncourt_offer2.id).count() == 1

    class GetActiveOffersMatchingISBNTest:
        @pytest.mark.usefixtures("db_session")
        def should_get_active_offers_linked_to_goncourt_isbn(self, app):
            # Given
            offerer = create_offerer()
            venue = create_venue(offerer=offerer)

            other_offer = create_offer_with_thing_product(venue=venue)
            other_offer.extraData["isbn"] = "123456789"
            active_goncourt_offer = create_offer_with_thing_product(venue=venue, is_active=True, id_at_providers="1")
            active_goncourt_offer.extraData["isbn"] = "9782072904073"
            inactive_goncourt_offer = create_offer_with_thing_product(venue=venue, is_active=False, id_at_providers="2")
            inactive_goncourt_offer.extraData["isbn"] = "9782072904073"
            repository.save(other_offer, active_goncourt_offer, inactive_goncourt_offer)

            # When
            matching_offers = get_active_offers_matching_isbn(GONCOURT_ISBNS)

            # Then
            assert matching_offers == [active_goncourt_offer]
