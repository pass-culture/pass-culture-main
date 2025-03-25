import argparse
import logging

from pcapi.app import app
from pcapi.models import db
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_mediations import clean_industrial_mediations_bucket


logger = logging.getLogger(__name__)

if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    clean_industrial_mediations_bucket()

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
