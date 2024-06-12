import random
from unittest import mock

import pytest

from pcapi.core import search
import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories.subcategories_v2 import ALL_SUBCATEGORIES
import pcapi.core.educational.factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import models as offers_models
import pcapi.core.offers.factories as offers_factories
from pcapi.core.providers.titelive_gtl import GTLS
import pcapi.core.search.testing as search_testing
from pcapi.repository import repository

from tests.conftest import clean_database


def run_command(app, command_name, *args):
    runner = app.test_cli_runner()
    args = (command_name, *args)
    return runner.invoke(args=args)


@clean_database
def test_partially_index_offers(app):
    _inactive_offer = offers_factories.StockFactory(offer__isActive=False)
    _unbookable_offer = offers_factories.OfferFactory()
    bookable_offer1 = offers_factories.StockFactory().offer
    _bookable_offer2 = offers_factories.StockFactory().offer

    # `get_paginated_active_offer_ids()` returns the first 2 active
    # offers, which are _unbookable_offer and bookable_offer1. Only
    # the latter is indexed.
    expected_to_be_reindexed = {
        bookable_offer1.id,
    }

    # fmt: off
    run_command(
        app,
        "partially_index_offers",
        "--batch-size", 1,
        "--last-page", 2,
    )
    # fmt: on

    assert set(search_testing.search_store["offers"].keys()) == expected_to_be_reindexed


@clean_database
@mock.patch("pcapi.core.search.async_index_offer_ids")
def test_update_products_booking_count_and_reindex_offers(mocked_async_index_offer_ids, app):
    ean = "1234567890123"
    product = offers_factories.ProductFactory(extraData={"ean": ean})
    offer_with_ean = offers_factories.OfferFactory(extraData={"ean": ean}, product=product)
    offer_with_no_ean = offers_factories.OfferFactory(extraData={})

    bookings_factories.BookingFactory(stock=offers_factories.StockFactory(offer=offer_with_ean))
    bookings_factories.BookingFactory(stock=offers_factories.StockFactory(offer=offer_with_no_ean))

    expected_to_be_reindexed = {offer_with_ean.id}

    rows = [{"id": 1, "ean": ean, "booking_count": 1}]
    with mock.patch("pcapi.connectors.big_query.TestingBackend.run_query") as mock_run_query:
        mock_run_query.return_value = rows
        run_command(app, "update_products_booking_count_and_reindex_offers")

    mocked_async_index_offer_ids.assert_called_once_with(
        expected_to_be_reindexed,
        reason=search.IndexationReason.BOOKING_COUNT_CHANGE,
    )


@clean_database
@mock.patch("pcapi.core.search.async_index_offer_ids")
def test_update_products_booking_count_and_reindex_offers_if_same_ean(mocked_async_index_offer_ids, app):
    ean_1 = "1234567890123"
    ean_2 = "9876543219876"
    product1 = offers_factories.ProductFactory(extraData={"ean": ean_1})
    product2 = offers_factories.ProductFactory(extraData={"ean": ean_2})
    offer_with_ean = offers_factories.OfferFactory(product=product1, extraData={"ean": ean_1})
    offer_not_booked_with_same_ean_in_offer = offers_factories.OfferFactory(extraData={"ean": ean_1}, product=product1)
    offer_with_different_ean = offers_factories.OfferFactory(extraData={"ean": ean_2}, product=product2)

    # 2 offers are booked
    bookings_factories.BookingFactory(stock=offers_factories.StockFactory(offer=offer_with_ean))

    # The 3 other offers are not booked, but bookable : we add stocks
    offers_factories.StockFactory(offer=offer_not_booked_with_same_ean_in_offer)
    offers_factories.StockFactory(offer=offer_with_different_ean)

    expected_to_be_reindexed = {
        offer_with_ean.id,
        offer_not_booked_with_same_ean_in_offer.id,
    }

    rows = [{"id": 1, "ean": ean_1, "booking_count": 1}]
    with mock.patch("pcapi.connectors.big_query.TestingBackend.run_query") as mock_run_query:
        mock_run_query.return_value = rows
        run_command(app, "update_products_booking_count_and_reindex_offers")

    args, kwargs = mocked_async_index_offer_ids.call_args
    assert sorted(args[0]) == sorted(expected_to_be_reindexed)
    assert kwargs == {"reason": search.IndexationReason.BOOKING_COUNT_CHANGE}


@clean_database
def test_partially_index_collective_offer_templates(app):
    _not_indexable_template = educational_factories.CollectiveOfferTemplateFactory(isActive=False)
    indexable_template1 = educational_factories.CollectiveOfferTemplateFactory()
    indexable_template2 = educational_factories.CollectiveOfferTemplateFactory()
    _indexable_template3 = educational_factories.CollectiveOfferTemplateFactory()

    expected_to_be_reindexed = {
        f"T-{indexable_template1.id}",
        f"T-{indexable_template2.id}",
    }
    # fmt: off
    run_command(
        app,
        "partially_index_collective_offer_templates",
        "--batch-size", 1,
        "--last-page", 2,
    )
    # fmt: on

    assert set(search_testing.search_store["collective-offers-templates"].keys()) == expected_to_be_reindexed


@clean_database
def test_partially_index_venues(app):
    _not_indexable_venue = offerers_factories.VenueFactory(isPermanent=False)
    indexable_venue1 = offerers_factories.VenueFactory(isPermanent=True)
    _indexable_venue2 = offerers_factories.VenueFactory(isPermanent=True)
    _indexable_venue3 = offerers_factories.VenueFactory(isPermanent=True)

    expected_to_be_reindexed = {
        indexable_venue1.id,
        # `get_eligible_for_search_venues()` returns at most
        # max-venues (here, 2), and only then filter ou non-eligible
        # venues, which are _not_indexable_venue and indexable_venue1.
        # Only the latter is indexed.
    }

    # fmt: off
    run_command(
        app,
        "partially_index_venues",
        "--max-venues", 2,
    )
    # fmt: on

    assert set(search_testing.search_store["venues"].keys()) == expected_to_be_reindexed


@clean_database
def test_partially_index_venues_removes_non_eligible_venues(app):
    future_not_indexable_venue = offerers_factories.VenueFactory(isPermanent=True)
    indexable_venue1 = offerers_factories.VenueFactory(isPermanent=True)

    expected_to_be_reindexed = {
        future_not_indexable_venue.id,
        indexable_venue1.id,
    }

    # fmt: off
    run_command(
        app,
        "partially_index_venues",
    )
    # fmt: on

    assert set(search_testing.search_store["venues"].keys()) == expected_to_be_reindexed

    ### This is the actual test: the venue is no longer eligible for search ###
    future_not_indexable_venue.isPermanent = False
    repository.save(future_not_indexable_venue)

    expected_to_be_reindexed = {
        indexable_venue1.id,
    }

    # fmt: off
    run_command(
        app,
        "partially_index_venues",
    )
    # fmt: on

    assert set(search_testing.search_store["venues"].keys()) == expected_to_be_reindexed


@pytest.mark.usefixtures("db_session")
class StagingIndexationTest:
    def test_get_offers_for_each_subcategory(self):
        # we limit to 4 subcategories to have a shorter test execution time
        for subcategory in ALL_SUBCATEGORIES[:4]:
            offers_factories.StockFactory.create_batch(
                size=20, offer__subcategoryId=subcategory.id, offer__isActive=True
            )
        offers = search.staging_indexation.get_offers_for_each_subcategory(10)
        assert len(offers) == len(ALL_SUBCATEGORIES[:4]) * 10

    def test_get_offers_with_gtl(self):
        stock_with_gtl = offers_factories.StockFactory.create_batch(
            size=20, offer__isActive=True, offer__extraData={"gtl_id": random.choice(list(GTLS.keys()))}
        )
        offers_factories.StockFactory.create_batch(size=20, offer__isActive=True)

        offer_ids = search.staging_indexation.get_offers_with_gtl(10)

        assert len(offer_ids) == 10
        offer_ids_with_gtl = [stock.offer.id for stock in stock_with_gtl]
        assert all(offer_id in offer_ids_with_gtl for offer_id in offer_ids)

    def test_get_offers_for_each_gtl_level_1(self):
        for gtl_id_prefix in range(1, 14):
            offers_factories.StockFactory.create_batch(
                size=3,
                offer__isActive=True,
                offer__extraData={
                    "gtl_id": random.choice(
                        list(
                            filter(
                                lambda gtl_id, gtl_id_prefix=gtl_id_prefix: gtl_id.startswith(
                                    str(gtl_id_prefix).zfill(2)
                                ),
                                GTLS.keys(),
                            )
                        )
                    )
                },
            )
        offers_factories.StockFactory.create_batch(size=20, offer__isActive=True)

        offer_ids = search.staging_indexation.get_offers_for_each_gtl_level_1(2)
        offers = offers_models.Offer.query.filter(offers_models.Offer.id.in_(offer_ids)).all()

        assert len(offer_ids) == 26

        for gtl_id_prefix in range(1, 14):
            gtl_id_prefix = str(gtl_id_prefix).zfill(2)
            assert (
                len(
                    list(
                        filter(
                            lambda offer, gtl_id_prefix=gtl_id_prefix: offer.extraData.get("gtl_id").startswith(
                                gtl_id_prefix
                            ),
                            offers,
                        )
                    )
                )
                == 2
            )

    def test_get_random_offers(self):
        offers_factories.StockFactory.create_batch(size=20, offer__isActive=True)

        offer_ids = search.staging_indexation.get_random_offers(10, {})

        assert len(offer_ids) == 10

    def test_get_random_offers_exclude(self):
        offers_factories.StockFactory.create_batch(size=5, offer__isActive=True)
        stocks_not_to_reindex = offers_factories.StockFactory.create_batch(size=5, offer__isActive=True)

        offers_not_to_reindex = {stock.offer.id for stock in stocks_not_to_reindex}
        offer_ids = search.staging_indexation.get_random_offers(10, offers_not_to_reindex)

        assert len(offer_ids) == 5
        assert all(offer_id not in offers_not_to_reindex for offer_id in offer_ids)
