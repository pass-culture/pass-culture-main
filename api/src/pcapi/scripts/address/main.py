"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=set_location_type_for_offers \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy as sa

import pcapi.core.geography.models as geography_models
import pcapi.core.offerers.models as offerer_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


def main(apply: bool = False) -> None:
    addresses_with_missing_insees = (
        db.session.query(geography_models.Address)
        .filter(
            geography_models.Address.inseeCode.is_(None),
            geography_models.Address.banId.is_not(None),
            geography_models.Address.isManualEdition.is_(False),
        )
        .all()
    )
    for address in addresses_with_missing_insees:
        try:
            with atomic():
                if not apply:
                    mark_transaction_as_invalid()
                assert address.banId
                db.session.query(geography_models.Address).filter(geography_models.Address.id == address.id).update(
                    {geography_models.Address.inseeCode: address.banId[0:5]}
                )
        except sa.exc.IntegrityError:
            sister_address = (
                db.session.query(geography_models.Address)
                .filter(
                    geography_models.Address.street == address.street,
                    geography_models.Address.city == address.city,
                    geography_models.Address.departmentCode == address.departmentCode,
                    geography_models.Address.postalCode == address.postalCode,
                    geography_models.Address.latitude == address.latitude,
                    geography_models.Address.longitude == address.longitude,
                    geography_models.Address.timezone == address.timezone,
                    geography_models.Address.banId == address.banId,
                    geography_models.Address.isManualEdition.is_(False),
                    geography_models.Address.inseeCode.is_not(None),
                )
                .one_or_none()
            )
            if sister_address:
                with atomic():
                    if not apply:
                        mark_transaction_as_invalid()
                    db.session.query(offerer_models.OffererAddress).filter(
                        offerer_models.OffererAddress.addressId == address.id
                    ).update({offerer_models.OffererAddress.addressId: sister_address.id})
                    db.session.flush()
                    db.session.delete(address)
            else:
                logger.info("manual check needed for address id %s", address.id)


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    main(args.apply)
    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        # db.session.rollback()
