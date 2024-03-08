import typing

import sqlalchemy as sa

from pcapi.core.educational.models import CollectiveOffer
from pcapi.models import db


def fetch_collective_offers() -> typing.Sequence[CollectiveOffer]:
    query = CollectiveOffer.query.filter(
        sa.and_(
            sa.or_(sa.func.cardinality(CollectiveOffer.formats) == 0, CollectiveOffer.formats == None),
            CollectiveOffer.subcategoryId != None,
        )
    ).options(sa.orm.load_only(CollectiveOffer.id, CollectiveOffer.formats, CollectiveOffer.subcategoryId))

    return query.all()


def set_formats(offers: typing.Sequence[CollectiveOffer]) -> None:
    for offer in offers:
        offer.formats = offer.get_formats()
        db.session.add(offer)


def run(dry_run: bool = False, out_path: str | None = None) -> typing.Collection[int]:
    offers = fetch_collective_offers()

    try:
        set_formats(offers)
    except Exception:
        db.session.rollback()
        raise

    try:
        if not dry_run:
            db.session.commit()
        else:
            db.session.rollback()
    except Exception:
        db.session.rollback()
        raise

    print(f"{len(offers)} offers updated (dry_run: {dry_run})")

    ids = {offer.id for offer in offers}
    if out_path:
        try:
            with open(out_path, encoding="utf-8", mode="w") as f:
                f.write(",".join({str(x) for x in ids}))
        except Exception:
            print(ids)
            raise

    return ids
