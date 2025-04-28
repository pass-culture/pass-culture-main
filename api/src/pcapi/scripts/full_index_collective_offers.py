import datetime
import logging
import statistics
import time

import click
import pytz

from pcapi.core import search
import pcapi.core.educational.models as collective_offers_models
from pcapi.core.search.backends import algolia
from pcapi.utils.blueprint import Blueprint


BATCH_SIZE = 1_000
REPORT_EVERY = 10_000

logger = logging.getLogger(__name__)
blueprint = Blueprint(__name__, __name__)


def _get_eta(end: int, current: int, elapsed_per_batch: list) -> str:
    left_to_do = end - current
    eta = left_to_do / BATCH_SIZE * statistics.mean(elapsed_per_batch)
    eta = datetime.datetime.utcnow() + datetime.timedelta(seconds=eta)
    eta = eta.astimezone(pytz.timezone("Europe/Paris"))
    eta = eta.strftime("%d/%m/%Y %H:%M:%S")
    return eta


@blueprint.cli.command("full_index_collective_template_offers")
@click.argument("start", type=int, required=True)
@click.argument("end", type=int, required=True)
def full_index_collective_template_offers(start: int, end: int) -> None:
    """Reindex all active collective template offers."""
    if start > end:
        raise ValueError('"start" must be less than "end"')
    backend = algolia.AlgoliaBackend()

    queue: list = []

    def enqueue_or_index(
        q: list,
        template_offer: collective_offers_models.CollectiveOfferTemplate | None,
        force_index: bool = False,
    ) -> None:
        if template_offer is not None:
            q.append(template_offer)
        if force_index or len(q) > BATCH_SIZE:
            try:
                backend.index_collective_offer_templates(q)
            except Exception as exc:
                logger.exception(
                    "Full collective template offer reindexation: error while reindexing from %d to %d: %s",
                    q[0][0].id,
                    q[-1][0].id,
                    exc,
                )
            q.clear()

    to_report = 0
    elapsed_per_batch = []

    while start <= end:
        start_time = time.perf_counter()
        collective_offers_template = (
            search.get_base_query_for_collective_template_offer_indexation()
            .filter(
                collective_offers_models.CollectiveOfferTemplate.isActive.is_(True),
                collective_offers_models.CollectiveOfferTemplate.isArchived.is_(False),  # type: ignore[attr-defined]
                collective_offers_models.CollectiveOfferTemplate.id.between(start, min(start + BATCH_SIZE, end)),
            )
            .order_by(collective_offers_models.CollectiveOfferTemplate.id)
        )

        for template_offer in collective_offers_template:
            if template_offer.is_eligible_for_search:
                enqueue_or_index(queue, template_offer)
        elapsed_per_batch.append(int(time.perf_counter() - start_time))
        start = start + BATCH_SIZE
        eta = _get_eta(end, start, elapsed_per_batch)
        to_report += BATCH_SIZE
        if to_report >= REPORT_EVERY:
            to_report = 0
            print(f"  => OK: {start} | eta = {eta}")
    enqueue_or_index(queue, template_offer=None, force_index=True)
    print("Done")
