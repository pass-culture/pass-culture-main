import argparse
import logging

from pcapi.app import app
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
from pcapi.models import db


app.app_context().push()
logger = logging.getLogger(__name__)

DATA_MODEL = ("venue_id", "correct_oa_id", "incorrect_oa_id")
DATA = [
    (9731, 98985, 95225),
    (9731, 98985, 21090),
    (9731, 98985, 95576),
    (121823, 27031, 95193),
    (13960, 27061, 89900),
    (40711, 21098, 95058),
    (5288, 55579, 89710),
    (57776, 46293, 95323),
]


def relocate_offers(items: list[dict]) -> list:

    ingnored_or_in_error = []
    for item in items:
        venue_id = item.get("venue_id")
        correct_oa_id = item.get("correct_oa_id")
        incorrect_oa_id = item.get("incorrect_oa_id")
        try:
            correct_oa = offerers_models.OffererAddress.query.filter(
                offerers_models.OffererAddress.id == correct_oa_id
            ).one_or_none()
            if correct_oa is None:
                ingnored_or_in_error.append(incorrect_oa_id)
                logger.info("IGNORED: OA #%s not found for Venue #%s", correct_oa_id, venue_id)
                continue

            (
                offers_models.Offer.query.join(offerers_models.Venue)
                .filter(offers_models.Offer.venueId == venue_id)
                .filter(offers_models.Offer.offererAddressId == incorrect_oa_id)
                .update(
                    {offers_models.Offer.offererAddressId: correct_oa_id},
                    synchronize_session=False,
                )
            )

            db.session.flush()
            logger.info("CORRECTED: offers attached to OA #%s for Venue #%s", correct_oa_id, venue_id)

        except Exception as e:  # pylint: disable=broad-exception-caught
            ingnored_or_in_error.append(incorrect_oa_id)
            logger.info(
                "NOT CORRECTED: error moving offers on OA #%s for Venue #%s - %s", correct_oa_id, venue_id, str(e)
            )
            continue
    return ingnored_or_in_error


def delete_oa(items: set) -> None:
    try:
        offerers_models.OffererAddress.query.filter(
            offerers_models.OffererAddress.id.in_(items),
        ).delete()
        db.session.flush()
        logger.info("CORRECTED: deleted OA %s", items)
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.info("NOT CORRECTED: error deleting OA #%s - %s", items, str(e))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script pour attacher les offres à la bonne localisation après fix des OA"
    )
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    items_to_correct = [dict(zip(DATA_MODEL, item)) for item in DATA]
    not_corrected = relocate_offers(items_to_correct)
    items_to_delete = {item["incorrect_oa_id"] for item in items_to_correct} - set(not_corrected)
    delete_oa(items_to_delete)

    if args.not_dry:
        logger.info("COMMIT: Finished relocating offers")
        db.session.commit()
    else:
        logger.info("ROLLBACK: Finished dry run for relocating offers")
        db.session.rollback()
