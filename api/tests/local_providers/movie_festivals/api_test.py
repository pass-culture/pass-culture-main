import datetime
from unittest.mock import patch

import pytest

from pcapi.local_providers.movie_festivals import api


@pytest.mark.features(ENABLE_MOVIE_FESTIVAL_RATE=True)
class ShouldApplyMovieFestivalRateTest:
    @pytest.mark.features(ENABLE_MOVIE_FESTIVAL_RATE=False)
    def should_return_false_because_feature_is_disabled(self):
        assert not api.should_apply_movie_festival_rate(1, datetime.date.today())

    @patch(
        "pcapi.local_providers.movie_festivals.constants.FESTIVAL_START_DATE",
        datetime.date.today() - datetime.timedelta(1),
    )
    @patch(
        "pcapi.local_providers.movie_festivals.constants.FESTIVAL_END_DATE",
        datetime.date.today() + datetime.timedelta(1),
    )
    @patch("pcapi.local_providers.movie_festivals.constants.FESTIVAL_OFFERS_IDS", [1, 45, 67])
    @pytest.mark.parametrize(
        "offer_id,stock_date,expected_result",
        [
            (45, datetime.date.today(), True),
            (42, datetime.date.today(), False),
            (45, datetime.date.today() - datetime.timedelta(2), False),
            (45, datetime.date.today() + datetime.timedelta(2), False),
        ],
    )
    def should_return_true_or_false_according_to_input(self, offer_id, stock_date, expected_result):
        assert api.should_apply_movie_festival_rate(offer_id, stock_date) == expected_result
