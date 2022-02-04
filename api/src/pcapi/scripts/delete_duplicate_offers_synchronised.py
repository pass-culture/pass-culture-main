from pcapi.core.offers.models import Mediation
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferReport
from pcapi.core.offers.models import Stock
from pcapi.core.payments.models import CustomReimbursementRule
from pcapi.core.search import unindex_offer_ids
from pcapi.core.users.models import Favorite
from pcapi.flask_app import app
from pcapi.models import db
from pcapi.models.offer_criterion import OfferCriterion


app.app_context().push()
from datetime import datetime
import logging


logger = logging.getLogger(__name__)
logging_indent = 6 * " "


step_size = 1000


OFFER_IDS_REQUEST = """
WITH reserved("stockId") AS (
    SELECT DISTINCT "stockId" FROM booking
), unreserved_zero_stock(id, "offerId", quantity, bookings) AS (
    SELECT s.id, s."offerId", s.quantity, COUNT(r."stockId") AS bookings
    FROM stock s
        LEFT JOIN reserved r ON r."stockId"=s.id
    WHERE s.quantity = 0
        AND r."stockId" IS NULL
    GROUP BY s.id, s."offerId", s.quantity
    LIMIT 100000
), synced_unereserved_zero_stock_offer(id, "idAtProvider", "stockId", "quantity", bookings) AS (
    SELECT o.id, o."idAtProvider", s.id AS "stockId", s.quantity, s.bookings
    FROM unreserved_zero_stock s
        JOIN offer o ON o.id = s."offerId"
    WHERE o."idAtProvider" IS NOT NULL
)
SELECT DISTINCT id
FROM synced_unereserved_zero_stock_offer
WHERE quantity = 0
    AND bookings = 0
    AND "idAtProvider" IS NOT NULL;
"""


def get_offer_ids() -> set[int]:
    res = db.session.execute(OFFER_IDS_REQUEST)
    return {row.id for row in res}


def delete_custom_reimbursement_rules_for_offers(offer_ids: list[int]) -> None:
    CustomReimbursementRule.query.filter(CustomReimbursementRule.offerId.in_(offer_ids)).delete(
        synchronize_session=False
    )


def delete_offer_criterion_for_offers(offer_ids: list[int]) -> None:
    OfferCriterion.query.filter(OfferCriterion.offerId.in_(offer_ids)).delete(synchronize_session=False)


def delete_offer_reports_for_offers(offer_ids: list[int]) -> None:
    OfferReport.query.filter(OfferReport.offerId.in_(offer_ids)).delete(synchronize_session=False)


def delete_stocks_for_offers(offer_ids: list[int]) -> None:
    Stock.query.filter(Stock.offerId.in_(offer_ids), Stock.bookings == None, Stock.quantity == 0).delete(
        synchronize_session=False
    )


def delete_mediations_for_offers(offer_ids: list[int]) -> None:
    Mediation.query.filter(Mediation.offerId.in_(offer_ids)).delete(synchronize_session=False)


def delete_favorites_for_offers(offer_ids: list[int]) -> None:
    Favorite.query.filter(Favorite.offerId.in_(offer_ids)).delete(synchronize_session=False)


def delete_ids(ids) -> None:
    try:
        # Delete related to offers
        delete_stocks_for_offers(ids)

        # Get the offers without a stock
        offers = db.session.query(Offer.id).filter(Offer.id.in_(ids), Offer.stocks == None).all()
        offer_ids = [offer.id for offer in offers]

        # Delete related objects to Offer with the new set of Offer ids
        delete_favorites_for_offers(offer_ids)
        delete_mediations_for_offers(offer_ids)
        delete_custom_reimbursement_rules_for_offers(offer_ids)
        delete_offer_criterion_for_offers(offer_ids)
        delete_offer_reports_for_offers(offer_ids)

        # Delete the Offers
        offers = Offer.query.filter(Offer.id.in_(offer_ids)).delete(synchronize_session=False)

        db.session.commit()

        unindex_offer_ids(offer_ids)
    except Exception as e:
        db.session.rollback()
        logger.info(e)
        raise


def delete_ids_batched(offer_ids) -> None:
    number_of_items = len(offer_ids)
    logging.info(
        "%sDeleting %d items of type %s using batches of %d size:",
        logging_indent,
        number_of_items,
        Offer.__name__,
        step_size,
    )

    last_id = 0
    offer_ids = list(offer_ids)

    while last_id + step_size <= number_of_items:
        delete_ids(offer_ids[last_id : last_id + step_size])
        logging.info("%s   %d%%", logging_indent, int(last_id / number_of_items * 100))
        last_id += step_size

    delete_ids(offer_ids[last_id:])
    logging.info("%s   100%%", logging_indent)


def main(round_number=1) -> None:
    logging.info("Running cleanup of Offers")
    start_time = datetime.now()
    offer_ids = get_offer_ids()

    while len(offer_ids) > 0:
        logging.info("Round %d of cleanup of Offers", round_number)
        delete_ids_batched(offer_ids)
        logging.info("Getting the new round of data...")
        offer_ids = get_offer_ids()
        round_number = round_number + 1

    logging.info("Cleanup finished, total duration: %s", datetime.now() - start_time)
