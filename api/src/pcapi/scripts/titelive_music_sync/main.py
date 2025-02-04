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
    parser.add_argument("--from-date", type=str, default="2024-10-15")
    args = parser.parse_args()

    from_date = datetime.datetime.strptime(args.from_date, "%Y-%m-%d").date()

    db.session.execute(sa.text("set session statement_timeout = '400s'"))
    TiteliveMusicSearch().synchronize_products(from_date, None, args.from_page)
