import pytest
import sqlalchemy.orm as sa_orm

from pcapi.core.criteria import models as criteria_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


def test_nested_query_with_soft_deleted_venues():
    regular_venue = offerers_factories.VenueFactory()
    soft_deleted_venue = offerers_factories.VenueFactory()
    soft_deleted_venue.isSoftDeleted = True
    db.session.add(soft_deleted_venue)

    # Query with a joinedinload to traverse a FK relationship
    base_query = db.session.query(offerers_models.Venue).options(
        sa_orm.load_only(offerers_models.Venue.id),
        sa_orm.joinedload(offerers_models.Venue.managingOfferer).load_only(offerers_models.Offerer.name),
    )

    assert base_query.all() == [regular_venue]
    assert base_query.limit(101).all() == [regular_venue]
    assert base_query.execution_options(include_deleted=True).all() == [regular_venue, soft_deleted_venue]
    assert base_query.execution_options(include_deleted=True).limit(101).all() == [regular_venue, soft_deleted_venue]

    # Query with a selectinload to traverse a many to many relationship
    base_query = db.session.query(offerers_models.Venue).options(
        sa_orm.load_only(
            offerers_models.Venue.id,
        ),
        sa_orm.selectinload(offerers_models.Venue.criteria).load_only(criteria_models.Criterion.name),
    )

    assert base_query.all() == [regular_venue]
    assert base_query.limit(101).all() == [regular_venue]
    assert base_query.execution_options(include_deleted=True).all() == [regular_venue, soft_deleted_venue]
    assert base_query.execution_options(include_deleted=True).limit(101).all() == [regular_venue, soft_deleted_venue]

    # Query with a joinedload to traverse a many to many relationship
    base_query = db.session.query(offerers_models.Venue).options(
        sa_orm.load_only(
            offerers_models.Venue.id,
        ),
        sa_orm.joinedload(offerers_models.Venue.criteria).load_only(criteria_models.Criterion.name),
    )

    assert base_query.all() == [regular_venue]
    assert base_query.limit(101).all() == [regular_venue]
    assert base_query.execution_options(include_deleted=True).all() == [regular_venue, soft_deleted_venue]
    assert base_query.execution_options(include_deleted=True).limit(101).all() == [regular_venue, soft_deleted_venue]
