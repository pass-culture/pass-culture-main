import logging

import click

from pcapi.core.products import api as products_api
from pcapi.utils.blueprint import Blueprint


logger = logging.getLogger(__name__)

blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("check_product_counts_consistency")
@click.argument("batch_size", required=False, type=int, default=10_000)
def check_product_counts_consistency(batch_size: int) -> None:
    product_ids = products_api.fetch_inconsistent_products(batch_size)

    if product_ids:
        logger.error("Inconsistent product counts found", extra={"product_ids": product_ids})
