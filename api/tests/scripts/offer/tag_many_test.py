import pytest

from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.offers import factories
from pcapi.core.testing import assert_num_queries
from pcapi.scripts.offer.tag_many import create_missing_mappings


pytestmark = pytest.mark.usefixtures("db_session")


def test_create_missing_mappings():
    criteria = criteria_factories.CriterionFactory.create_batch(2)
    offers = factories.OfferFactory.create_batch(3)

    criterion_names = {criterion.name for criterion in criteria}
    offer_ids = {offer.id for offer in offers}

    # 1. load offers
    # 2. load criteria (OfferCriterion)
    # 3. insert mappings (OfferCriterionMapping)
    # 4. commit
    with assert_num_queries(4):
        create_missing_mappings(offer_ids, criterion_names, dry_run=False)

    assert all(len(offer.criteria) == 2 for offer in offers)
    assert {criterion.name for offer in offers for criterion in offer.criteria} == criterion_names


def test_create_missing_mappings_when_some_criteria_exists():
    offers = factories.OfferFactory.create_batch(3)
    criteria = criteria_factories.CriterionFactory.create_batch(2)

    # all offers will have one criterion (the same)
    criteria_factories.OfferCriterionFactory(offerId=offers[0].id, criterionId=criteria[0].id)
    criteria_factories.OfferCriterionFactory(offerId=offers[1].id, criterionId=criteria[0].id)
    criteria_factories.OfferCriterionFactory(offerId=offers[2].id, criterionId=criteria[0].id)

    criterion_names = {criterion.name for criterion in criteria}
    offer_ids = {offer.id for offer in offers}

    # 1. load offers
    # 2. load criteria (Criterion)
    # 3. insert mappings (OfferCriterion)
    # 4. commit
    with assert_num_queries(4):
        create_missing_mappings(offer_ids, criterion_names, dry_run=False)

    assert all(len(offer.criteria) == 2 for offer in offers)
    assert {criterion.name for offer in offers for criterion in offer.criteria} == criterion_names


def test_create_missing_mappings_dry_run():
    """
    Test that when dry_run parameter is true no mapping is created
    """
    criteria = criteria_factories.CriterionFactory.create_batch(2)
    offers = factories.OfferFactory.create_batch(3)

    criterion_names = {criterion.name for criterion in criteria}
    offer_ids = {offer.id for offer in offers}

    # 1. load offers
    # 2. load criteria (OfferCriterion)
    # 3. rollback
    with assert_num_queries(3):
        create_missing_mappings(offer_ids, criterion_names, dry_run=True)

    assert all(not offer.criteria for offer in offers)
