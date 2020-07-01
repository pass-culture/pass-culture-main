import time
from datetime import datetime

import pytz

from models.db import db
from repository import discovery_view_queries
from tests.conftest import clean_database


class CleanTest:
    @clean_database
    def test_should_remove_dead_tuples_in_database(self, app):
        # Given
        discovery_last_vacuum = datetime.now().replace(tzinfo=pytz.utc)
        discovery_view_queries.refresh()

        # When
        discovery_view_queries.clean(app)

        # Then
        time.sleep(1)
        discovery_new_vacuum = db.session.execute("""
          SELECT last_vacuum FROM pg_stat_all_tables WHERE relname = 'discovery_view';
        """).scalar()
        assert discovery_new_vacuum > discovery_last_vacuum
