"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/pcharlet/pc-37378-remove-false-action-history-venue-permanent/api/src/pcapi/scripts/remove_permanent_action_history/main.py

"""

import argparse
import csv
import logging
import os
import typing

from pcapi.app import app
from pcapi.core.history import models as history_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


def _read_csv_file() -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/downloaded-logs.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


@atomic()
def main(not_dry: bool) -> None:
    if not not_dry:
        mark_transaction_as_invalid()
    logs = _read_csv_file()
    origin_and_destination_venues_ids = []
    for log in logs:
        message = log["jsonPayload.message"].split()
        message_type = message[0]
        # We get origin venue and destination venue ids for each transfer
        if message_type == "Transfer":
            destination_origin_tuple = (int(message[4]), int(message[-1]))
            origin_and_destination_venues_ids.append(destination_origin_tuple)
        # Pour chaque transfert, il y a un log de type "Transfer done for venue XXXX to venue YYYY"
        # permettant de récupérer la liste des venues de destination.
        # Toutes ces venues ont donc un ActionHistory associé, légitime ou non, indiquant le passage en permanent.
        # Pour savoir quels sont les vrais passages en permanent,
        # on regarde les log du type "Destination venue XXXX updated to permanent"
        # Si ce log n'existe pas pour la venue de destination, c'est que la venue était déjà permanente.
        # Attention Les logs sont classés par ordre décroissant temporellement, le 1er du csv est le dernier à avoir été loggé
        elif message_type == "Destination" and int(message[2]) == destination_origin_tuple[1]:
            origin_and_destination_venues_ids.pop()
    for origin_and_destination_venue_id in origin_and_destination_venues_ids:
        origin_venue_id = origin_and_destination_venue_id[0]
        destination_venue_id = origin_and_destination_venue_id[1]
        db.session.query(history_models.ActionHistory).filter(
            history_models.ActionHistory.actionType == history_models.ActionType.VENUE_REGULARIZATION,
            history_models.ActionHistory.venueId == destination_venue_id,
            history_models.ActionHistory.extraData
            == {
                "origin_venue_id": origin_venue_id,
                "modified_info": {"isPermanent": {"old_info": False, "new_info": True}},
            },
        ).delete()
        logger.info(
            "Action history for venue %d wrongly modified to permanent from transfer of venue %d removed",
            destination_venue_id,
            origin_venue_id,
        )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)

    if args.not_dry:
        logger.info("Finished")
    else:
        db.session.rollback()
        logger.info("Finished dry run, rollback")
