import pytest

from pcapi.core.offerers import factories
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.scripts.offerer.tag_many import create_missing_mappings


def test_create_missing_mappings():
    tags = factories.OffererTagFactory.create_batch(2)
    offerers = factories.OffererFactory.create_batch(3)

    tag_names = {tag.name for tag in tags}
    offerer_ids = {offerer.id for offerer in offerers}

    with assert_no_duplicated_queries():
        create_missing_mappings(offerer_ids, tag_names, dry_run=False)

    assert all(len(offerer.tags) == 2 for offerer in offerers)
    assert {tag.name for offerer in offerers for tag in offerer.tags} == tag_names


def test_create_missing_mappings_when_some_tags_exists():
    offerers = factories.OffererFactory.create_batch(3)
    tags = factories.OffererTagFactory.create_batch(2)

    # all offerers will have one tag (the same)
    factories.OffererTagMappingFactory(offererId=offerers[0].id, tagId=tags[0].id)
    factories.OffererTagMappingFactory(offererId=offerers[1].id, tagId=tags[0].id)
    factories.OffererTagMappingFactory(offererId=offerers[2].id, tagId=tags[0].id)

    tag_names = {tag.name for tag in tags}
    offerer_ids = {offerer.id for offerer in offerers}

    with assert_no_duplicated_queries():
        create_missing_mappings(offerer_ids, tag_names, dry_run=False)

    assert all(len(offerer.tags) == 2 for offerer in offerers)
    assert {tag.name for offerer in offerers for tag in offerer.tags} == tag_names


def test_create_missing_mappings_dry_run():
    """
    Test that when dry_run parameter is true no mapping is created
    """
    tags = factories.OffererTagFactory.create_batch(2)
    offerers = factories.OffererFactory.create_batch(3)

    tag_names = {tag.name for tag in tags}
    offerer_ids = {offerer.id for offerer in offerers}

    with assert_no_duplicated_queries():
        create_missing_mappings(offerer_ids, tag_names, dry_run=True)

    assert all(not offerer.tags for offerer in offerers)
