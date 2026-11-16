from unittest import mock

import pytest
import sqlalchemy.util as sa_util

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models import soft_delete_rewriter


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(autouse=True)
def empty_cache(monkeypatch):
    monkeypatch.setattr(soft_delete_rewriter, "_statements_without_filter", sa_util.LRUCache(1000))


def _query_venues(venue_ids):
    return db.session.query(offerers_models.Venue).filter(offerers_models.Venue.id.in_(venue_ids))


class RewriteStatementTest:
    def test_filters_soft_deleted_venues_on_every_execution(self):
        venue = offerers_factories.VenueFactory()
        deleted_venue = offerers_factories.VenueFactory()
        deleted_venue.isSoftDeleted = True
        db.session.flush()
        venue_ids = [venue.id, deleted_venue.id]
        db.session.expunge_all()

        for _ in range(2):
            assert [v.id for v in _query_venues(venue_ids).all()] == [venue.id]

    def test_skips_rewrite_for_a_known_structure_without_venue(self):
        """The full rewrite is the costly part: it must run once per statement structure, not per execution."""
        user = users_factories.UserFactory()
        other_user = users_factories.UserFactory()
        db.session.query(users_models.User).filter(users_models.User.id == user.id).all()

        with mock.patch.object(soft_delete_rewriter._TrackingRewriter, "rewrite_statement") as rewrite:
            db.session.query(users_models.User).filter(users_models.User.id == other_user.id).all()

        rewrite.assert_not_called()

    def test_does_not_remember_a_structure_rewritten_with_include_deleted(self):
        """`include_deleted` is not part of SQLAlchemy cache keys: remembering it would drop the filter for everyone."""
        venue = offerers_factories.VenueFactory()
        deleted_venue = offerers_factories.VenueFactory()
        deleted_venue.isSoftDeleted = True
        db.session.flush()
        venue_ids = [venue.id, deleted_venue.id]
        db.session.expunge_all()

        with_deleted = _query_venues(venue_ids).execution_options(include_deleted=True).all()
        without_deleted = _query_venues(venue_ids).all()

        assert sorted(v.id for v in with_deleted) == sorted(venue_ids)
        assert [v.id for v in without_deleted] == [venue.id]
