# This script is temporary and will only be executed once.
import datetime
import logging
import statistics
import time

import click
import pytz

from pcapi.models import db
from pcapi.utils.blueprint import Blueprint


BATCH_SIZE = 1_000
REPORT_EVERY = 100_000

logger = logging.getLogger(__name__)
blueprint = Blueprint(__name__, __name__)


def _get_eta(end: int, current: int, elapsed_per_batch: list[int]) -> str:
    left_to_do = end - current
    seconds_eta = left_to_do / BATCH_SIZE * statistics.mean(elapsed_per_batch)
    eta = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds_eta)
    eta = eta.astimezone(pytz.timezone("Europe/Paris"))
    str_eta = eta.strftime("%d/%m/%Y %H:%M:%S")
    return str_eta


@blueprint.cli.command("fill_product_ean")
@click.argument("start", type=int, required=True)
@click.argument("end", type=int, required=True)
def fill_product_ean(start: int, end: int) -> None:
    if start > end:
        raise ValueError('"start" must be less than "end"')

    elapsed_per_batch = []
    to_report = 0
    for i in range(start, end, BATCH_SIZE):
        start_time = time.perf_counter()
        db.session.execute(
            """
            update product set "jsonData" = jsonb_set("jsonData", '{ean}', "jsonData"->'ean')
            where "jsonData"->>'ean' != ''
            and id between :start and :end
            """,
            params={"start": i, "end": i + BATCH_SIZE},
        )
        db.session.commit()
        elapsed_per_batch.append(int(time.perf_counter() - start_time))
        eta = _get_eta(end, start, elapsed_per_batch)
        to_report += BATCH_SIZE
        if to_report >= REPORT_EVERY:
            to_report = 0
            print(f"BATCH : id from {i} | eta = {eta}")


@blueprint.cli.command("fill_offer_ean")
@click.argument("start", type=int, required=True)
@click.argument("end", type=int, required=True)
def fill_offer_ean(start: int, end: int) -> None:
    if start > end:
        raise ValueError('"start" must be less than "end"')

    elapsed_per_batch = []
    to_report = 0
    for i in range(start, end, BATCH_SIZE):
        start_time = time.perf_counter()
        db.session.execute(
            """
            update offer set "jsonData" = jsonb_set("jsonData", '{ean}', "jsonData"->'ean')
            where "jsonData"->>'ean' != ''
            and id between :start and :end
            """,
            params={"start": i, "end": i + BATCH_SIZE},
        )
        db.session.commit()
        elapsed_per_batch.append(int(time.perf_counter() - start_time))
        eta = _get_eta(end, start, elapsed_per_batch)

        to_report += BATCH_SIZE
        if to_report >= REPORT_EVERY:
            to_report = 0
            print(f"BATCH : id from {i} | eta = {eta}")


@blueprint.cli.command("delete_offer_ean")
@click.argument("start", type=int, required=True)
@click.argument("end", type=int, required=True)
def delete_offer_ean(start: int, end: int) -> None:
    if start > end:
        raise ValueError('"start" must be less than "end"')

    elapsed_per_batch = []
    to_report = 0
    for i in range(start, end, BATCH_SIZE):
        start_time = time.perf_counter()
        db.session.execute(
            """
            update offer set "jsonData" = "offer.jsonsData" - 'isbn'::text
            and id between :start and :end
            """,
            params={"start": i, "end": i + BATCH_SIZE},
        )
        db.session.commit()
        elapsed_per_batch.append(int(time.perf_counter() - start_time))
        eta = _get_eta(end, start, elapsed_per_batch)

        to_report += BATCH_SIZE
        if to_report >= REPORT_EVERY:
            to_report = 0
            print(f"BATCH : id from {i} | eta = {eta}")


@blueprint.cli.command("delete_product_ean")
@click.argument("start", type=int, required=True)
@click.argument("end", type=int, required=True)
def delete_product_ean(start: int, end: int) -> None:
    if start > end:
        raise ValueError('"start" must be less than "end"')

    elapsed_per_batch = []
    to_report = 0
    for i in range(start, end, BATCH_SIZE):
        start_time = time.perf_counter()
        db.session.execute(
            """
            update product set "jsonData" = "jsonData" - 'ean'::text
            where id between :start and :end
            """,
            params={"start": i, "end": i + BATCH_SIZE},
        )
        db.session.commit()
        elapsed_per_batch.append(int(time.perf_counter() - start_time))
        eta = _get_eta(end, start, elapsed_per_batch)

        to_report += BATCH_SIZE
        if to_report >= REPORT_EVERY:
            to_report = 0
            print(f"BATCH : id from {i} | eta = {eta}")
