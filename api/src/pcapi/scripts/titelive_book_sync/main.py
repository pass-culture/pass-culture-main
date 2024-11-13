import datetime

import sqlalchemy as sa

from pcapi.core.providers.titelive_book_search import TiteliveBookSearch
from pcapi.models import db


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    db.session.execute(sa.text("set session statement_timeout = '400s'"))
    TiteliveBookSearch().synchronize_products(datetime.date(2025, 1, 5), datetime.date(2025, 1, 7))
