import typing

from sqlalchemy.orm import joinedload
from sqlalchemy.orm import load_only

from pcapi.core.offerers import models
from pcapi.models import db


TagNames = typing.Collection[str]
Ids = typing.Collection[int]

Offerers = typing.Collection[models.Offerer]
OffererTags = typing.Collection[models.OffererTag]
OfferersTagsMappings = typing.Collection[models.OffererTagMapping]


def load_offerers(offerer_ids: Ids) -> Offerers:
    return (
        db.session.query(models.Offerer)
        .filter(models.Offerer.id.in_(offerer_ids))
        .options(joinedload(models.Offerer.tags))
        .options(load_only(models.Offerer.id))
        .all()
    )


def load_tags(tag_names: TagNames) -> OffererTags:
    return db.session.query(models.OffererTag).filter(models.OffererTag.name.in_(tag_names)).all()


def find_offerer_missing_tags(offerer: models.Offerer, tags: OffererTags) -> OfferersTagsMappings:
    offerer_tag_names = {tag.name for tag in offerer.tags}
    tag_names = {tag.name for tag in tags}

    missing_tag_names = tag_names - offerer_tag_names
    missing_offerer_tags = [tag for tag in tags if tag.name in missing_tag_names]

    return [models.OffererTagMapping(offererId=offerer.id, tagId=tag.id) for tag in missing_offerer_tags]


def create_missing_mappings(offerer_ids: Ids, tag_names: TagNames, dry_run: bool = False) -> None:
    """
    Create missing offerers <-> tags mappings. The offerer tags must
    exist, they will not be created by this function.
    """
    offerers = load_offerers(offerer_ids)
    tags = load_tags(tag_names)

    for offerer in offerers:
        missing_offerer_tags_mapping = find_offerer_missing_tags(offerer, tags)
        print(f"offerer: {offerer.name}, found {len(missing_offerer_tags_mapping)} missing tag(s)")

        for mapping in missing_offerer_tags_mapping:
            db.session.add(mapping)

    if not dry_run:
        db.session.commit()
    else:
        db.session.rollback()
