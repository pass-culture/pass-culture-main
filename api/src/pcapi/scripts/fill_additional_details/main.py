"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=fill_additional_details \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy as sa
from sqlalchemy import orm as sa_orm

from pcapi.core.educational import models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(apply: bool) -> None:
    max_id = db.session.query(sa.func.max(models.CollectiveStock.id)).scalar()

    query = db.session.query(models.CollectiveStock).options(sa_orm.joinedload(models.CollectiveStock.collectiveOffer))

    batch_size = 10_000
    i = 0
    while i < max_id:
        rows = query.filter(models.CollectiveStock.id >= i, models.CollectiveStock.id < i + batch_size)

        for collective_stock in rows:
            if collective_stock.collectiveOffer.additionalDetails != collective_stock.priceDetail:
                collective_stock.collectiveOffer.additionalDetails = collective_stock.priceDetail

            if collective_stock.servicePrice != collective_stock.price:
                collective_stock.servicePrice = collective_stock.price

        db.session.flush()

        if apply:
            db.session.commit()
        else:
            db.session.rollback()

        print(f"Processed stocks with id {i} through {i + batch_size - 1}")

        i += batch_size


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    main(apply=args.apply)
