import pytest
from sqlalchemy.exc import IntegrityError

from pcapi.core.criteria import factories


@pytest.mark.usefixtures("db_session")
class VenueCriterionTest:
    def test_unique_venue_criterion(self):
        venue_criterion = factories.VenueCriterionFactory()
        venue = venue_criterion.venue
        criterion = venue_criterion.criterion
        with pytest.raises(IntegrityError):
            factories.VenueCriterionFactory(venue=venue, criterion=criterion)


@pytest.mark.usefixtures("db_session")
class OfferCriterionTest:
    def test_unique_offer_criterion(self):
        offer_criterion = factories.OfferCriterionFactory()
        offer = offer_criterion.offer
        criterion = offer_criterion.criterion
        with pytest.raises(IntegrityError):
            factories.OfferCriterionFactory(offer=offer, criterion=criterion)
