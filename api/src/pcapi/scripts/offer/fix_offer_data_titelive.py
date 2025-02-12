import datetime
import logging
import statistics
import time

import click
import pytz

from pcapi.flask_app import app
from pcapi.models import db
from pcapi.utils.blueprint import Blueprint


BATCH_SIZE = 1_000

logger = logging.getLogger(__name__)
blueprint = Blueprint(__name__, __name__)


def _get_eta(end_id: int, current: int, elapsed_per_batch: list) -> str:
    left_to_do = end_id - current
    eta = left_to_do / BATCH_SIZE * statistics.mean(elapsed_per_batch)
    eta = datetime.datetime.utcnow() + datetime.timedelta(seconds=eta)
    eta = eta.astimezone(pytz.timezone("Europe/Paris"))
    eta = eta.strftime("%d/%m/%Y %H:%M:%S")
    return eta


def _fix_offers(start_id: int, end_id: int) -> None:
    elapsed_per_batch = []
    logger.info("[fix_offer_data_titelive] BATCH_SIZE : %d", BATCH_SIZE)
    for i in range(start_id, end_id, BATCH_SIZE):
        start_time = time.perf_counter()
        db.session.execute(
            """
            UPDATE offer
            SET "jsonData" = jsonb_set(
            jsonb_set(
                jsonb_set(
                    offer."jsonData",
                    '{code_clil}',
                    to_jsonb(product."jsonData"->>'code_clil'),
                    true
                ),
                '{csr_id}',
                to_jsonb(product."jsonData"->>'csr_id'),
                true
            ),
            '{gtl_id}',
            to_jsonb(product."jsonData"->>'gtl_id'),
            true
        )
            FROM product
            WHERE product.id between :start and :end
            AND offer."productId" = product.id
            AND product."jsonData"->>'gtl_id' is not null
            AND product."jsonData"->>'gtl_id' != ''
            AND (offer."jsonData"->>'csr_id' is null OR offer."jsonData"->>'csr_id' = '' OR offer."jsonData"->>'code_clil' is null OR offer."jsonData"->>'code_clil' = '' OR offer."jsonData"->>'gtl_id' is null OR offer."jsonData"->>'gtl_id' = '')
            AND ((product."jsonData"->>'csr_id' is not null AND product."jsonData"->>'csr_id' != '') OR (product."jsonData"->>'code_clil' is not null AND product."jsonData"->>'code_clil' != ''))
            """,
            params={"start": i, "end": i + BATCH_SIZE},
        )
        db.session.commit()
        elapsed_per_batch.append(int(time.perf_counter() - start_time))
        eta = _get_eta(end_id, start_id, elapsed_per_batch)

        logger.info("[fix_offer_data_titelive] BATCH : id from %d | eta = %s", i, eta)


@blueprint.cli.command("fix_offer_data_titelive")
@click.argument("start", type=int, required=True)
@click.argument("end", type=int, required=True)
def fix_offer_data_titelive(start: int, end: int) -> None:
    logger.info("[fix_offer_data_titelive] start between %d and %d", start, end)
    if start > end:
        raise ValueError('"start" must be less than "end"')

    with app.app_context():
        _fix_offers(start, end)
