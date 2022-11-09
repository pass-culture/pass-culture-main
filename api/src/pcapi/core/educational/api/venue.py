from operator import or_

import sqlalchemy as sa

from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils.clean_accents import clean_accents


def get_venues_by_siret(siret: str) -> list[offerers_models.Venue]:
    venue = (
        offerers_models.Venue.query.filter(
            offerers_models.Venue.siret == siret,
            offerers_models.Venue.isVirtual == False,
        )
        .options(sa.orm.joinedload(offerers_models.Venue.contact))
        .options(sa.orm.joinedload(offerers_models.Venue.venueLabel))
        .options(sa.orm.joinedload(offerers_models.Venue.managingOfferer))
        .one()
    )
    return [venue]


def get_relative_venues_by_siret(siret: str, permanent_only: bool = False) -> list[offerers_models.Venue]:
    aliased_venue = sa.orm.aliased(offerers_models.Venue)
    query = db.session.query(offerers_models.Venue)
    query = query.join(offerers_models.Offerer, offerers_models.Venue.managingOfferer)
    query = query.join(aliased_venue, offerers_models.Offerer.managedVenues)
    query = query.filter(
        # constraint on retrieved venues
        offerers_models.Venue.isVirtual == False,
        # constraint on searched venue
        aliased_venue.isVirtual == False,
        aliased_venue.siret == siret,
    )
    if permanent_only:
        query = query.filter(
            offerers_models.Venue.isPermanent == True,
            aliased_venue.isPermanent == True,
        )
    query = query.options(sa.orm.joinedload(offerers_models.Venue.contact))
    query = query.options(sa.orm.joinedload(offerers_models.Venue.venueLabel))
    query = query.options(sa.orm.joinedload(offerers_models.Venue.managingOfferer))
    # group venues by offerer
    query = query.order_by(offerers_models.Venue.managingOffererId, offerers_models.Venue.name)

    return query.all()


def get_all_venues(page: int | None, per_page: int | None) -> list[offerers_models.Venue]:
    page = 1 if page is None else page
    per_page = 1000 if per_page is None else per_page

    return (
        offerers_models.Venue.query.filter(
            offerers_models.Venue.isVirtual == False,
        )
        .order_by(offerers_models.Venue.id)
        .offset((page - 1) * per_page)
        .limit(per_page)
        .options(sa.orm.joinedload(offerers_models.Venue.contact))
        .options(sa.orm.joinedload(offerers_models.Venue.venueLabel))
        .options(sa.orm.joinedload(offerers_models.Venue.managingOfferer))
        .all()
    )


def get_venues_by_name(name: str) -> list[offerers_models.Venue]:
    name = name.replace(" ", "%")
    name = name.replace("-", "%")
    name = clean_accents(name)
    venues = (
        offerers_models.Venue.query.filter(
            or_(
                sa.func.unaccent(offerers_models.Venue.name).ilike(f"%{name}%"),
                sa.func.unaccent(offerers_models.Venue.publicName).ilike(f"%{name}%"),
            ),
            offerers_models.Venue.isVirtual == False,
        )
        .options(sa.orm.joinedload(offerers_models.Venue.contact))
        .options(sa.orm.joinedload(offerers_models.Venue.venueLabel))
        .options(sa.orm.joinedload(offerers_models.Venue.managingOfferer))
        .all()
    )
    return venues


def get_relative_venues_by_name(name: str) -> list[offerers_models.Venue]:
    name = name.replace(" ", "%")
    name = name.replace("-", "%")
    name = clean_accents(name)
    aliased_venue = sa.orm.aliased(offerers_models.Venue)

    query = db.session.query(offerers_models.Venue)
    query = query.join(offerers_models.Offerer, offerers_models.Venue.managingOfferer)
    query = query.join(aliased_venue, offerers_models.Offerer.managedVenues)
    query = query.filter(
        # constraint on retrieved venues
        offerers_models.Venue.isVirtual == False,
        # constraint on searched venue
        aliased_venue.isVirtual == False,
        or_(
            sa.func.unaccent(aliased_venue.name).ilike(f"%{name}%"),
            sa.func.unaccent(aliased_venue.publicName).ilike(f"%{name}%"),
        ),
    )
    query = query.options(sa.orm.joinedload(offerers_models.Venue.contact))
    query = query.options(sa.orm.joinedload(offerers_models.Venue.venueLabel))
    query = query.options(sa.orm.joinedload(offerers_models.Venue.managingOfferer))

    # group venues by offerer
    query = query.order_by(offerers_models.Venue.managingOffererId, offerers_models.Venue.name)

    return query.all()
