from datetime import datetime

from algolia.domain.eligibility import EligibilityRules
from repository import repository
import pytest
from model_creators.generic_creators import create_offerer, create_venue, create_stock
from model_creators.specific_creators import create_offer_with_event_product, create_offer_with_thing_product


class NameHasChangedTest:
    def test_should_return_true_when_name_has_changed(self):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_event_product(event_name='super offre', venue=venue)
        offer_details = {'name': 'ancienne super offre'}

        # When
        name_has_changed = EligibilityRules.NAME_HAS_CHANGED.value.apply(offer=offer, offer_details=offer_details)

        # Then
        assert name_has_changed

    def test_should_return_false_when_name_has_not_changed(self):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_event_product(event_name='super offre', venue=venue)
        offer_details = {'name': 'super offre'}

        # When
        name_has_changed = EligibilityRules.NAME_HAS_CHANGED.value.apply(offer=offer, offer_details=offer_details)

        # Then
        assert not name_has_changed


class DatesHaveChangedTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_false_when_offer_is_not_an_event(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(thing_name='super offre', venue=venue)
        stock = create_stock(offer=offer, price=10)
        repository.save(stock)
        offer_details = {'dates': []}

        # When
        dates_have_changed = EligibilityRules.DATES_HAVE_CHANGED.value.apply(offer=offer,
                                                                             offer_details=offer_details)

        # Then
        assert not dates_have_changed

    @pytest.mark.usefixtures("db_session")
    def test_should_return_true_when_dates_have_changed(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_event_product(event_name='super offre', venue=venue)
        stock = create_stock(beginning_datetime=datetime(2020, 1, 1), offer=offer, price=10)
        repository.save(stock)
        offer_details = {'dates': [1486290387]}

        # When
        dates_have_changed = EligibilityRules.DATES_HAVE_CHANGED.value.apply(offer=offer,
                                                                             offer_details=offer_details)

        # Then
        assert dates_have_changed

    @pytest.mark.usefixtures("db_session")
    def test_should_false_when_dates_have_not_changed(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_event_product(event_name='super offre', venue=venue)
        stock = create_stock(beginning_datetime=datetime(2020, 1, 1), offer=offer, price=10)
        repository.save(stock)
        offer_details = {'dates': [1577836800]}

        # When
        dates_have_changed = EligibilityRules.DATES_HAVE_CHANGED.value.apply(offer=offer,
                                                                             offer_details=offer_details)

        # Then
        assert not dates_have_changed


class PricesHaveChangedTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_false_when_prices_have_not_changed(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(thing_name='super offre', venue=venue)
        stock = create_stock(offer=offer, price=10)
        repository.save(stock)
        offer_details = {'prices': [10]}

        # When
        prices_have_changed = EligibilityRules.PRICES_HAVE_CHANGED.value.apply(offer=offer,
                                                                               offer_details=offer_details)

        # Then
        assert not prices_have_changed

    @pytest.mark.usefixtures("db_session")
    def test_should_return_true_when_prices_have_changed(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_event_product(event_name='super offre', venue=venue)
        stock = create_stock(beginning_datetime=datetime(2020, 1, 1), offer=offer, price=12)
        repository.save(stock)
        offer_details = {'prices': [10]}

        # When
        prices_have_changed = EligibilityRules.PRICES_HAVE_CHANGED.value.apply(offer=offer,
                                                                               offer_details=offer_details)

        # Then
        assert prices_have_changed
