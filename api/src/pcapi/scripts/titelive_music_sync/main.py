import argparse
import datetime

import sqlalchemy as sa

from pcapi.core.providers.titelive_music_search import TiteliveMusicSearch
from pcapi.models import db


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-page", type=int, default=1)
    args = parser.parse_args()

    db.session.execute(sa.text("set session statement_timeout = '400s'"))
    TiteliveMusicSearch().synchronize_products(datetime.date(2024, 10, 15), args.from_page)
