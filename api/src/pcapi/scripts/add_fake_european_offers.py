import json
import logging

import click

from pcapi import repository
from pcapi.core import search
from pcapi.core.european_offers import api
import pcapi.core.european_offers.repository as european_offers_repository
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


def _get_json_data() -> list[dict]:
    data = []
    with open("./src/pcapi/scripts/fake_european_offer.json", "r", encoding="UTF-8") as f:
        data = json.load(f)

    return data


@blueprint.cli.command("add_fake_european_offers")
@click.option("--clear", help="Clear EuropeanOffer table", type=bool, default=False)
def add_fake_european_offers(clear: bool) -> None:
    count = european_offers_repository.get_all_european_offers_count()
    logger.info("We start with %d EuropeOffers", count)

    if clear:
        european_offers_repository.delete_all_european_offers()
        search.unindex_all_european_offers()

    data = _get_json_data()
    with repository.transaction():
        for offer_dict in data:
            offer = api.EuropeanOfferData(**offer_dict)
            european_offer = api.create_offer(offer)
    all_european_offers = european_offers_repository.get_all_european_offers()
    search.index_european_offer_ids([european_offer.id for european_offer in all_european_offers])

    count = european_offers_repository.get_all_european_offers_count()
    logger.info("There are now %d EuropeOffers !", count)
