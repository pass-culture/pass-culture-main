import datetime

import pytest

import pcapi.core.highlights.factories as highlights_factories
from pcapi.utils import db as db_utils


pytestmark = pytest.mark.usefixtures("db_session")


class HighlightModelTest:
    def test_is_available(self):
        today = datetime.date.today()
        available_highlight = highlights_factories.HighlightFactory(
            availability_datespan=db_utils.make_inclusive_daterange(
                start=today - datetime.timedelta(days=10), end=today
            ),
        )
        assert available_highlight.is_available
        unavailable_highlight = highlights_factories.HighlightFactory(
            availability_datespan=db_utils.make_inclusive_daterange(
                start=today - datetime.timedelta(days=10), end=today - datetime.timedelta(days=8)
            )
        )
        assert not unavailable_highlight.is_available
