"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-35867-script-fill-collective-oa/api/src/pcapi/scripts/fill_collective_offers_oa/main.py

"""

import argparse
import logging

import sqlalchemy as sa
from sqlalchemy import orm as sa_orm

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


logger = logging.getLogger(__name__)

OaByKeyType = dict[tuple[int, int, str], offerers_models.OffererAddress]

BATCH_SIZE = 2000


def get_or_create_offerer_address(
    venue: offerers_models.Venue,
    venue_offerer_address: offerers_models.OffererAddress | None,
    offerer_address_by_key: OaByKeyType,
) -> offerers_models.OffererAddress | None:
    # this should not happen as collective offers are linked to physical venues (which should have an OA)
    if venue_offerer_address is None:
        return None

    # we cannot use the venue's OA in the case offer.venueId != offer.offerVenue["venueId"]
    # we must create a new OA object (or re-use an existing one) with label = common_name of the venue
    offerer_id = venue.managingOffererId
    address_id = venue_offerer_address.addressId
    assert address_id is not None  # for mypy
    label = venue.common_name
    oa_key = (offerer_id, address_id, label)

    if oa_key in offerer_address_by_key:
        return offerer_address_by_key[oa_key]

    result = (
        db.session.query(offerers_models.OffererAddress)
        .filter(
            offerers_models.OffererAddress.offererId == offerer_id,
            offerers_models.OffererAddress.label == label,
            offerers_models.OffererAddress.addressId == address_id,
        )
        .one_or_none()
    )

    if result is not None:
        offerer_address_by_key[oa_key] = result
        return result

    new_offerer_address = offerers_models.OffererAddress(offererId=offerer_id, addressId=address_id, label=label)
    db.session.add(new_offerer_address)
    offerer_address_by_key[oa_key] = new_offerer_address

    return new_offerer_address


def fill_location_fields(
    offer: educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate,
    venue_from_offer_venue: offerers_models.Venue | None,
    oa_from_offer_venue: offerers_models.OffererAddress | None,
    offerer_address_by_key: OaByKeyType,
) -> None:
    match offer.offerVenue["addressType"]:
        case educational_models.OfferAddressType.OFFERER_VENUE.value:
            offerer_address: offerers_models.OffererAddress | None
            # offer located at its venue, use the venue's OA
            if offer.offerVenue["venueId"] == offer.venueId:
                offerer_address = offer.venue.offererAddress

            # offer located at a different venue
            elif venue_from_offer_venue is not None:
                offerer_address = get_or_create_offerer_address(
                    venue=venue_from_offer_venue,
                    venue_offerer_address=oa_from_offer_venue,
                    offerer_address_by_key=offerer_address_by_key,
                )

            # venue not found
            else:
                logger.warning(
                    "Found offer with id %s with offerVenue.addressType=offererVenue and no corresponding Venue. Fallback to offer.venue OA",
                    offer.id,
                )
                offerer_address = offer.venue.offererAddress

            if offerer_address is None:
                logger.warning("Found venue with no related OA, location fields were not set for offer %s", offer.id)
                return

            offer.locationType = educational_models.CollectiveLocationType.ADDRESS
            offer.locationComment = None
            offer.offererAddress = offerer_address

        case educational_models.OfferAddressType.SCHOOL.value:
            offer.locationType = educational_models.CollectiveLocationType.SCHOOL
            offer.locationComment = None
            offer.offererAddress = None

        case educational_models.OfferAddressType.OTHER.value:
            offer.locationType = educational_models.CollectiveLocationType.TO_BE_DEFINED
            # we often store "" in otherAddress, in this case prefer None for locationComment
            offer.locationComment = offer.offerVenue["otherAddress"] or None
            offer.offererAddress = None

        case _:
            raise ValueError("Unexpected addressType received")


def get_query(
    model: type[educational_models.CollectiveOffer] | type[educational_models.CollectiveOfferTemplate],
    location_type_none_only: bool,
) -> "sa_orm.Query[tuple[educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate, offerers_models.Venue | None, offerers_models.OffererAddress | None]]":
    aliased_venue = sa_orm.aliased(offerers_models.Venue)
    aliased_oa = sa_orm.aliased(offerers_models.OffererAddress)

    # outerjoined venue is the venue corresponding to offer.offerVenue["venueId"]
    # outerjoined OA is the OA of this venue
    query = (
        db.session.query(model, aliased_venue, aliased_oa)
        .outerjoin(
            aliased_venue,
            aliased_venue.id == sa.cast(model.offerVenue.op("->>")("venueId"), sa.BigInteger),
        )
        .outerjoin(aliased_oa, aliased_oa.id == aliased_venue.offererAddressId)
        .options(sa_orm.joinedload(model.venue).joinedload(offerers_models.Venue.offererAddress))
        .order_by(model.id)
    )

    if location_type_none_only:
        query = query.filter(model.locationType.is_(None))

    return query


def process_offers(
    model: type[educational_models.CollectiveOffer] | type[educational_models.CollectiveOfferTemplate],
    location_type_none_only: bool,
    offerer_address_by_key: OaByKeyType,
) -> None:
    query = get_query(model=model, location_type_none_only=location_type_none_only)

    progress = 0
    for collective_offer, venue_from_offer_venue, oa_from_offer_venue in query.yield_per(BATCH_SIZE):
        try:
            fill_location_fields(
                offer=collective_offer,
                venue_from_offer_venue=venue_from_offer_venue,
                oa_from_offer_venue=oa_from_offer_venue,
                offerer_address_by_key=offerer_address_by_key,
            )
        except Exception:
            logger.warning("Error while processing offer %s", collective_offer.id)
            raise

        db.session.add(collective_offer)

        progress += 1
        if progress % BATCH_SIZE == 0:
            logger.info("Processed %s offers", progress)

    db.session.flush()


def main(location_type_none_only: bool = False) -> None:
    # we use a dict to store the OA objects that we get or create in the case "offer.venueId != offer.offerVenue["venueId"]"
    # this way we emit a single query for each OA key (offererId, addressId, label)
    offerer_address_by_key: OaByKeyType = {}

    logger.info("Starting to process collective offers")
    process_offers(
        model=educational_models.CollectiveOffer,
        location_type_none_only=location_type_none_only,
        offerer_address_by_key=offerer_address_by_key,
    )
    logger.info("Finished processing collective offers")

    logger.info("Starting to process collective offer templates")
    process_offers(
        model=educational_models.CollectiveOfferTemplate,
        location_type_none_only=location_type_none_only,
        offerer_address_by_key=offerer_address_by_key,
    )
    logger.info("Finished processing collective offer templates")


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument(
        "--location-type-none-only",
        action="store_true",
        help="""
            When this argument is set, compute locationType only for offers with locationType = None
            By default, process all the collective offers
        """,
    )
    args = parser.parse_args()

    main(location_type_none_only=args.location_type_none_only)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
