import logging

from pcapi.core.educational.utils import create_adage_jwt_fake_valid_token
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)

logger = logging.getLogger(__name__)

from pcapi.core import search
from pcapi.core.educational import api


@blueprint.cli.command("reindex_all_collective_offers")
def reindex_all_collective_offers() -> None:
    """
    TO BE USED IN LOCAL ENV
    """
    search.unindex_all_collective_offers()
    search.unindex_all_collective_offer_templates()
    search.index_all_collective_offers_and_templates()


@blueprint.cli.command("generate_fake_adage_token")
def generate_fake_adage_token() -> None:
    """
    TO BE USED IN LOCAL ENV
    """
    token = create_adage_jwt_fake_valid_token()
    print(f"Adage localhost URL: http://localhost:3002/?token={token}")


@blueprint.cli.command("synchronize_venues_from_adage_cultural_partners")
def synchronize_venues_from_adage_cultural_partners() -> None:
    api.synchronize_adage_ids_on_venues()
