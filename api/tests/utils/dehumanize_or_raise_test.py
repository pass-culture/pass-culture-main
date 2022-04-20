import pytest

from pcapi.utils.human_ids import dehumanize_or_raise
from pcapi.utils.human_ids import humanize


class DehumanizeOrRaiseTest:
    def test_ok(self):
        assert 0 == dehumanize_or_raise(humanize(0))
        assert 13 == dehumanize_or_raise(humanize(13))
        assert 487569635892585 == dehumanize_or_raise(humanize(487569635892585))

    def test_none(self):
        with pytest.raises(ValueError):
            dehumanize_or_raise(None)
