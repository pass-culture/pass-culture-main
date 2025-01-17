import datetime

from pcapi.models import db
from pcapi.models.feature import FeatureToggle

from . import constants


def should_apply_movie_festival_rate(offer_id: int, stock_date: datetime.date) -> bool:
    with (
        db.session.no_autoflush
    ):  # otherwise in tests, due to the `pytest.mark.features(ENABLE_MOVIE_FESTIVAL_RATE=True)`,
        # the FF check triggers a flush on an invalid stock
        return (
            FeatureToggle.ENABLE_MOVIE_FESTIVAL_RATE.is_active()
            and offer_id in constants.FESTIVAL_OFFERS_IDS
            and (constants.FESTIVAL_START_DATE <= stock_date <= constants.FESTIVAL_END_DATE)
        )
