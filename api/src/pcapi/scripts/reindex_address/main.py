import argparse
import time

from sqlalchemy import text

from pcapi.app import app
from pcapi.models import db


app.app_context().push()


def reindex() -> None:
    engine = db.get_engine(app, bind=None)

    with engine.connect() as conn:
        conn.execute(text("DROP INDEX IF EXISTS ix_complete_unique_address"))
    # Then, create the new index
    try:
        with engine.connect() as conn:
            conn = conn.execution_options(isolation_level="AUTOCOMMIT")
            conn.execute(
                text(
                    """CREATE UNIQUE INDEX CONCURRENTLY ix_complete_unique_address ON address ("banId", "inseeCode", "street", "postalCode", "city", "latitude", "longitude")"""
                )
            )
    except Exception as e:
        print(f"Failed to create index: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reindex address table for the ix_complete_unique_address index")
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    try:
        start = time.time()
        reindex()
    except:
        db.session.rollback()
        raise
    else:
        if args.dry_run:
            db.session.rollback()
        else:
            db.session.commit()
    finally:
        end = time.time()
        print(f"Duration: {end - start}")
