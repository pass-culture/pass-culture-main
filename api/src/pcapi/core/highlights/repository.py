from pcapi.core.highlights.models import Highlight
from pcapi.models import db
from pcapi.utils.date import get_naive_utc_now


def get_available_highlights() -> list[Highlight]:
    now = get_naive_utc_now()
    highlight_list = db.session.query(Highlight).filter(Highlight.availability_timespan.contains(now)).all()
    return highlight_list
