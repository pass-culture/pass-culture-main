import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils.clean_accents import clean_accents


def get_venues_by_siret(siret: str) -> list[offerers_models.Venue]:
    venue = (
        offerers_models.Venue.query.filter(
            offerers_models.Venue.siret == siret,
            sa.not_(offerers_models.Venue.isVirtual),
        )
        .options(*_get_common_joinedload_options())
        .one()
    )
    return [venue]


def get_relative_venues_by_siret(siret: str, permanent_only: bool = False) -> list[offerers_models.Venue]:
    aliased_venue = sa_orm.aliased(offerers_models.Venue)
    query = db.session.query(offerers_models.Venue)
    query = query.join(offerers_models.Offerer, offerers_models.Venue.managingOfferer)
    query = query.join(aliased_venue, offerers_models.Offerer.managedVenues)
    query = query.filter(
        # constraint on retrieved venues
        sa.not_(offerers_models.Venue.isVirtual),
        # constraint on searched venue
        sa.not_(aliased_venue.isVirtual),
        aliased_venue.siret == siret,
    )
    if permanent_only:
        query = query.filter(
            offerers_models.Venue.isPermanent,
            aliased_venue.isPermanent,
        )
    query = query.options(*_get_common_joinedload_options())
    # group venues by offerer
    query = query.order_by(offerers_models.Venue.managingOffererId, offerers_models.Venue.name)

    return query.all()


def get_all_venues(page: int | None, per_page: int | None) -> list[offerers_models.Venue]:
    page = 1 if page is None else page
    per_page = 1000 if per_page is None else per_page

    return (
        offerers_models.Venue.query.filter(
            sa.not_(offerers_models.Venue.isVirtual),
        )
        .order_by(offerers_models.Venue.id)
        .offset((page - 1) * per_page)
        .limit(per_page)
        .options(*_get_common_joinedload_options())
        .options(sa_orm.joinedload(offerers_models.Venue.googlePlacesInfo))
        .options(
            sa_orm.joinedload(offerers_models.Venue.collectiveDomains).load_only(
                educational_models.EducationalDomain.id, educational_models.EducationalDomain.name
            )
        )
        .all()
    )


def get_venues_by_name(name: str) -> list[offerers_models.Venue]:
    name = name.replace(" ", "%")
    name = name.replace("-", "%")
    name = clean_accents(name)
    venues = (
        offerers_models.Venue.query.filter(
            sa.or_(
                sa.func.immutable_unaccent(offerers_models.Venue.name).ilike(f"%{name}%"),
                sa.func.immutable_unaccent(offerers_models.Venue.publicName).ilike(f"%{name}%"),
            ),
            sa.not_(offerers_models.Venue.isVirtual),
        )
        .options(*_get_common_joinedload_options())
        .all()
    )
    return venues


def get_relative_venues_by_name(name: str) -> list[offerers_models.Venue]:
    name = name.replace(" ", "%")
    name = name.replace("-", "%")
    name = clean_accents(name)
    aliased_venue = sa_orm.aliased(offerers_models.Venue)

    query = db.session.query(offerers_models.Venue)
    query = query.join(offerers_models.Offerer, offerers_models.Venue.managingOfferer)
    query = query.join(aliased_venue, offerers_models.Offerer.managedVenues)
    query = query.filter(
        # constraint on retrieved venues
        sa.not_(offerers_models.Venue.isVirtual),
        # constraint on searched venue
        sa.not_(aliased_venue.isVirtual),
        sa.or_(
            sa.func.immutable_unaccent(aliased_venue.name).ilike(f"%{name}%"),
            sa.func.immutable_unaccent(aliased_venue.publicName).ilike(f"%{name}%"),
        ),
    )
    query = query.options(*_get_common_joinedload_options())

    # group venues by offerer
    query = query.order_by(offerers_models.Venue.managingOffererId, offerers_models.Venue.name)

    return query.all()


def _get_common_joinedload_options() -> tuple[sa_orm.Load, ...]:
    return (
        sa_orm.joinedload(offerers_models.Venue.contact),
        sa_orm.joinedload(offerers_models.Venue.venueLabel),
        sa_orm.joinedload(offerers_models.Venue.managingOfferer),
        sa_orm.joinedload(offerers_models.Venue.offererAddress).joinedload(offerers_models.OffererAddress.address),
    )
