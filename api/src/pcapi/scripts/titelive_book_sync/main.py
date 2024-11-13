import datetime

import sqlalchemy as sa

from pcapi.core.providers.titelive_book_search import TiteliveBookSearch
from pcapi.models import db


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    db.session.execute(sa.text("set session statement_timeout = '500s'"))
    TiteliveBookSearch().synchronize_products(
        from_date=datetime.date(2024, 12, 4), to_date=datetime.date(2025, 1, 22), from_page=1
    )
