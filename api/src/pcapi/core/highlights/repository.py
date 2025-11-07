import datetime

from pcapi.core.highlights.models import Highlight
from pcapi.models import db


def get_available_highlights() -> list[Highlight]:
    today = datetime.date.today()
    highlight_list = db.session.query(Highlight).filter(Highlight.availability_datespan.contains(today)).all()
    return highlight_list
