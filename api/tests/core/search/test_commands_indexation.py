import pcapi.core.educational.factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
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
def test_partially_index_collective_offers(app):
    _inactive_offer = educational_factories.CollectiveStockFactory(collectiveOffer__isActive=False).collectiveOffer
    _unbookable_offer = educational_factories.CollectiveOfferFactory()
    bookable_offer1 = educational_factories.CollectiveStockFactory().collectiveOffer
    _bookable_offer2 = educational_factories.CollectiveStockFactory().collectiveOffer

    # `get_paginated_active_collective_offer_ids()` returns the first
    # 2 active offers, which are _unbookable_offer and bookable_offer1.
    # Only the latter is indexed.
    expected_to_be_reindexed = {
        bookable_offer1.id,
    }

    # fmt: off
    run_command(
        app,
        "partially_index_collective_offers",
        "--batch-size", 1,
        "--last-page", 2,
    )
    # fmt: on

    assert set(search_testing.search_store["collective-offers"].keys()) == expected_to_be_reindexed


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
