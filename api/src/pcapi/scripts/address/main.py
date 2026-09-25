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

import pcapi.core.educational.models as educational_models
import pcapi.core.geography.models as geography_models
import pcapi.core.offerers.models as offerer_models
import pcapi.core.offers.models as offers_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

BATCH_SIZE = 5000
UPDATED_OFFERS_MAX_LIMIT = 2_000_000


def change_offers_location(
    offer_model: type[offers_models.Offer]
    | type[educational_models.CollectiveOffer]
    | type[educational_models.CollectiveOfferTemplate],
    old_location_id: int,
    new_location_id: int,
    apply: bool = False,
) -> bool:
    try:
        with atomic():
            batch_counter = 0
            subquery_for_batch = (
                db.session.query(offer_model.id)
                .filter(offer_model.offererAddressId == old_location_id)
                .limit(BATCH_SIZE)
                .subquery()
            )
            while db.session.query(subquery_for_batch).first() and batch_counter < UPDATED_OFFERS_MAX_LIMIT:
                try:
                    with atomic():
                        # raise sa_exc.OperationalError("hello", "parameter", "origin")
                        updated_offers = db.session.execute(
                            sa.update(offer_model)
                            .where(offer_model.id.in_(subquery_for_batch))
                            .values(offererAddressId=new_location_id)
                        )
                        db.session.flush()
                        batch_counter += updated_offers.rowcount
                except sa.OperationalError:  # when updating multiple offers is too much
                    try:
                        with atomic():
                            subquery = (
                                db.session.query(offer_model.id)
                                .filter(offer_model.offererAddressId == old_location_id)
                                .limit(1)
                                .subquery()
                            )
                            counter = 0
                            # raise sa_exc.OperationalError("hello", "parameter", "origin")
                            updated_offer = db.session.execute(
                                sa.update(offer_model)
                                .where(offer_model.id.in_(subquery))
                                .values(offererAddressId=new_location_id)
                            )
                            while updated_offer.rowcount and counter < BATCH_SIZE:
                                db.session.flush()
                                counter += 1
                                updated_offer = db.session.execute(
                                    sa.update(offer_model)
                                    .where(offer_model.id.in_(subquery))
                                    .values(offererAddressId=new_location_id)
                                )
                            batch_counter += counter
                            if counter >= BATCH_SIZE:
                                logger.warning(
                                    "updated %s offers for new location %s, stopping now",
                                    BATCH_SIZE,
                                    new_location_id,
                                )
                    except sa.exc.OperationalError:
                        logger.info(
                            "Failed to update offers from %s to new location %s",
                            old_location_id,
                            new_location_id,
                        )
                        raise IndexError()
            if batch_counter >= UPDATED_OFFERS_MAX_LIMIT:
                logger.warning(
                    "updated %s offers for location %s, stopping now",
                    UPDATED_OFFERS_MAX_LIMIT,
                    new_location_id,
                )
                raise IndexError()
    except IndexError:
        return False
    return True


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
    logger.info("Found %d addresses with missing inseeCode", len(addresses_with_missing_insees))
    address_counter = 0
    empty_address_counter = 0
    for address in addresses_with_missing_insees:
        try:
            with atomic():
                if not apply:
                    mark_transaction_as_invalid()
                assert address.banId
                address.inseeCode = address.banId[0:5]
                db.session.flush()
                address_counter += 1
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
                try:
                    with atomic():
                        if not apply:
                            mark_transaction_as_invalid()

                        locations_with_bad_address = (
                            db.session.query(offerer_models.OffererAddress)
                            .filter(offerer_models.OffererAddress.addressId == address.id)
                            .all()
                        )
                        for location in locations_with_bad_address:
                            location.addressId = sister_address.id
                        db.session.flush()
                        db.session.delete(address)
                        db.session.flush()
                        address_counter += 1
                except sa.exc.IntegrityError:
                    logger.info(
                        "Failed to update location from address id %s to address id %s, moving offers to sister address",
                        address.id,
                        sister_address.id,
                    )
                    with atomic():
                        if not apply:
                            mark_transaction_as_invalid()
                        db.session.query(offerer_models.OffererAddress).filter(
                            offerer_models.OffererAddress.addressId == address.id,
                            offerer_models.OffererAddress.type == offerer_models.LocationType.VENUE_LOCATION,
                        ).update({offerer_models.OffererAddress.addressId: sister_address.id})
                        old_locations = (
                            db.session.query(offerer_models.OffererAddress)
                            .filter(
                                offerer_models.OffererAddress.addressId == address.id,
                                offerer_models.OffererAddress.type == offerer_models.LocationType.OFFER_LOCATION,
                            )
                            .all()
                        )
                        for old_location in old_locations:
                            new_location_id = db.session.query(offerer_models.OffererAddress.id).filter(
                                offerer_models.OffererAddress.addressId == sister_address.id,
                                offerer_models.OffererAddress.type == offerer_models.LocationType.OFFER_LOCATION,
                                offerer_models.OffererAddress.label == old_location.label,
                                offerer_models.OffererAddress.venueId == old_location.venueId,
                                offerer_models.OffererAddress.offererId == old_location.offererId,
                            ).first()[0]
                            if (
                                change_offers_location(
                                    offer_model=educational_models.CollectiveOfferTemplate,
                                    old_location_id=old_location.id,
                                    new_location_id=new_location_id,
                                    apply=apply,
                                )
                                and change_offers_location(
                                    offer_model=educational_models.CollectiveOffer,
                                    old_location_id=old_location.id,
                                    new_location_id=new_location_id,
                                    apply=apply,
                                )
                                and change_offers_location(
                                    offer_model=offers_models.Offer,
                                    old_location_id=old_location.id,
                                    new_location_id=new_location_id,
                                    apply=apply,
                                )
                            ):
                                db.session.query(offerer_models.OffererAddress).filter(
                                    offerer_models.OffererAddress.id == old_location.id
                                ).delete()
                                empty_address_counter += 1
            else:
                logger.info("manual check needed for address id %s", address.id)
    logger.info("Total addresses updated: %s", address_counter)
    logger.info("Total emptyaddresses to delete now: %s", empty_address_counter)


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    main(args.apply)
    logger.info("Finished")
