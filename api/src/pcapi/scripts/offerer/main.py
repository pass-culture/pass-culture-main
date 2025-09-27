"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/bdalbianco/PC-36989_replace_data_for_partially_diffusibles/api/src/pcapi/scripts/offerer/main.py

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.geography import models as geography_models
from pcapi.core.offerers import models as offerer_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(not_dry: bool) -> None:
    # offerers = (
    #     db.session.query(offerer_models.Offerer)
    #     .filter(offerer_models.Offerer._address.contains("[ND]"))
    #     .update({"_address": "Adresse non diffusée", "_street": "Adresse non diffusée"}, synchronize_session=False)
    # )
    # logger.info("found %d offerers with non conform address", offerers)

    # venues = (
    #     db.session.query(offerer_models.Venue)
    #     .filter((offerer_models.Venue._street.contains("[ND]")) | (offerer_models.Venue._street == "n/d"))
    #     .update({"_address": "Adresse non diffusée", "_street": "Adresse non diffusée"}, synchronize_session=False)
    # )
    # logger.info("found %d venues", venues)

    # if not_dry:
    #     logger.info("Finished")
    #     db.session.commit()
    # else:
    #     logger.info("Finished dry run, rollback")
    #     db.session.rollback()

    addresses = (
        db.session.query(geography_models.Address)
        .filter(geography_models.Address.street == "Adresse non diffusée", geography_models.Address.banId != None)
        .all()
    )
    count = 0
    for address in addresses:
        # address.street = "Adresse non diffusée"
        address.banId = None
        address.isManualEdition = True
        count += 1
        if not_dry:
            try:
                save_id = address.id
                db.session.add(address)
                db.session.commit()
            except:
                logger.warning("Skipping address with id %d due to copy", save_id)
                db.session.rollback()
    logger.info("found %d addresses", count)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)
