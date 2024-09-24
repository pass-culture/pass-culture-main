import json
import logging

from pcapi import repository
from pcapi.core.european_offers import api
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


def _get_json_data() -> list[dict]:
    data = []
    with open("./src/pcapi/scripts/fake_european_offer.json", "r", encoding="UTF-8") as f:
        data = json.load(f)

    return data


@blueprint.cli.command("add_fake_european_offers")
def add_fake_european_offers() -> None:
    """
    Regenerate the expected_openapi.json used in the blueprint_openapi_test
    """
    data = _get_json_data()
    with repository.transaction():
        for offer_dict in data:
            offer = api.EuropeanOfferData(**offer_dict)
            api.create_offer(offer)
