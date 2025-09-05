"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-37261-api-ajouter-une-localisation-sur-les-venues-virtuelles/api/src/pcapi/scripts/fill_virtual_venue_location/main.py

"""

import argparse
import logging
import time
import traceback

import sqlalchemy.orm as sa_orm

import pcapi.core.offerers.api as offerer_api
import pcapi.core.offerers.models as offerer_models
from pcapi.app import app
from pcapi.connectors import api_adresse
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(dry_run: bool) -> None:
    venue_ids = (
        db.session.query(offerer_models.Venue)
        .filter(
            offerer_models.Venue.isVirtual == True,
            offerer_models.Venue.offererAddressId == None,
        )
        .options(
            sa_orm.joinedload(offerer_models.Venue.managingOfferer),
        )
        .execution_options(include_deleted=True)
        .with_entities(offerer_models.Venue.id)
        .all()
    )
    for (venue_id,) in venue_ids:
        venue = (
            db.session.query(offerer_models.Venue)
            .filter(offerer_models.Venue.id == venue_id)
            .options(
                sa_orm.joinedload(offerer_models.Venue.managingOfferer),
            )
            .execution_options(include_deleted=True)
            .one()
        )
        try:
            address_info = api_adresse.get_municipality_centroid(
                city=venue.managingOfferer.city, postcode=venue.managingOfferer.postalCode
            )
            latitude = address_info.latitude
            longitude = address_info.longitude
            location_data = offerer_api.LocationData(
                city=venue.managingOfferer.city,
                postal_code=venue.managingOfferer.postalCode,
                latitude=latitude,
                longitude=longitude,
                street=venue.managingOfferer.street or "adresse non diffusée",
                ban_id=None,
                insee_code=address_info.citycode,
            )
            address = offerer_api.get_or_create_address(location_data, is_manual_edition=True)
            location = offerer_api.get_or_create_offerer_address(venue.managingOffererId, address.id, venue.name)
            venue.offererAddress = location
            db.session.add_all([address, location, venue])
            if dry_run:
                print(f"Would add localisation to virtual venue id={venue.id}")
                db.session.rollback()
            else:
                print(f"Added localisation to virtual venue id={venue.id}")
                db.session.commit()
        except Exception as e:
            print(traceback.format_exc())
            logger.exception(f"Error while adding localisation to virtual venue id={venue.id}, error: {str(e)}")
            db.session.rollback()
        time.sleep(1)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(dry_run=not args.not_dry)

    if args.not_dry:
        logger.info("Finished")
    else:
        logger.info("Finished dry run, rollback")
