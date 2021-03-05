from unittest import mock

import pytest

import pcapi.core.offers.factories as offers_factories
from pcapi.scripts.add_criterion_to_offers import add_criterion_to_offers


@pytest.mark.usefixtures("db_session")
class AddCriterionToOffersTest:
    @mock.patch("pcapi.connectors.redis.add_offer_id")
    def test_add_criterion(self, mocked_add_offer_id):
        # Given
        isbn = "2-221-00164-8"
        offer1 = offers_factories.OfferFactory(extraData={"isbn": "2221001648"})
        offer2 = offers_factories.OfferFactory(extraData={"isbn": "2221001648"})
        inactive_offer = offers_factories.OfferFactory(extraData={"isbn": "2221001648"}, isActive=False)
        unmatched_offer = offers_factories.OfferFactory()
        criterion1 = offers_factories.CriterionFactory(name="Pretty good books")
        criterion2 = offers_factories.CriterionFactory(name="Other pretty good books")

        # When
        is_successful = add_criterion_to_offers([criterion1, criterion2], isbn=isbn)

        # Then
        assert is_successful is True
        assert offer1.criteria == [criterion1, criterion2]
        assert offer2.criteria == [criterion1, criterion2]
        assert not inactive_offer.criteria
        assert not unmatched_offer.criteria
        # fmt: off
        reindexed_offer_ids = {
            mocked_add_offer_id.call_args_list[i][1]["offer_id"]
            for i in range(mocked_add_offer_id.call_count)
        }
        # fmt: on
        assert reindexed_offer_ids == {offer1.id, offer2.id}

    @mock.patch("pcapi.connectors.redis.add_offer_id")
    def test_add_criterion_when_no_offers_is_found(self, mocked_add_offer_id):
        # Given
        isbn = "2-221-00164-8"
        offers_factories.OfferFactory(extraData={"isbn": "2221001647"})
        criterion = offers_factories.CriterionFactory(name="Pretty good books")

        # When
        is_successful = add_criterion_to_offers([criterion], isbn=isbn)

        # Then
        assert is_successful is False
