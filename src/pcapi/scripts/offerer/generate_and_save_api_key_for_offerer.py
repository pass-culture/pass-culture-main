import logging

from tabulate import tabulate

from pcapi.core.offerers.api import generate_and_save_api_key
from pcapi.core.offerers.models import ApiKey
from pcapi.core.offerers.models import Offerer
from pcapi.models import db


logger = logging.getLogger(__name__)


def generate_and_save_api_key_for_offerer(sirens: str) -> list[list[str]]:
    logging_lines = []

    for siren in sirens:
        offerer = db.session.query(Offerer).filter(Offerer.siren == siren).one_or_none()
        if not offerer:
            logging_lines.append([siren, "X", "Error: Siren inconnu"])
        else:
            api_key_exist = ApiKey.query.filter_by(offererId=offerer.id).count()

            if api_key_exist:
                logging_lines.append([siren, "X", "Warning: Clé déjà existante pour ce siren"])
            else:
                clear_api_key = generate_and_save_api_key(offerer.id)
                logging_lines.append([siren, clear_api_key, "Success"])

    logger.info("Generated api key for offerer\n%s", tabulate(logging_lines, headers=["Siren", "api_key", "Result"]))
    return logging_lines
