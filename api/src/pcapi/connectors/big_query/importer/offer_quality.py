import itertools
import logging
import time
from typing import Sequence

from sqlalchemy import exc as sa_exc

from pcapi.connectors.big_query.queries.offer_quality import OfferQualityModel
from pcapi.connectors.big_query.queries.offer_quality import OfferQualityQuery
from pcapi.core.offers import models as offer_models
from pcapi.models import db
from pcapi.utils.repository import transaction


logger = logging.getLogger(__name__)


class OfferQualityImporter:
    """Importer to update offer quality scores from BigQuery data."""

    def run_offer_quality_update(self, batch_size: int = 1000, start_from_id: int = 0) -> None:
        logger.info("Starting offer quality scores update...")

        query = OfferQualityQuery(start_from_id=start_from_id)
        total_processed = 0

        for batch in itertools.batched(query.execute(), batch_size):
            self._process_batch(batch)
            total_processed += len(batch)
            last_processed_id = batch[-1].offer_id
            logger.info("last processed offerId", extra={"last_processed_id": last_processed_id})

        logger.info("Finished offer quality scores update", extra={"total_processed": total_processed})

    def _process_batch(self, batch: Sequence[OfferQualityModel]) -> None:
        if not batch:
            return

        start_time = time.perf_counter()
        try:
            with transaction():
                self._apply_updates(batch)

            duration = time.perf_counter() - start_time
            logger.info(
                "Successfully updated offer quality batch scores",
                extra={"batch_size": len(batch), "duration": duration},
            )

        except sa_exc.SQLAlchemyError as exc:
            duration = time.perf_counter() - start_time
            logger.warning("Batch update failed. Retrying one by one", extra={"duration": duration, "error": str(exc)})
            self._process_one_by_one(batch)

    def _process_one_by_one(self, batch: Sequence[OfferQualityModel]) -> None:
        for item in batch:
            try:
                with transaction():
                    self._apply_updates([item])
            except sa_exc.SQLAlchemyError as exc:
                logger.error(
                    "Failed to update quality scores for offer ", extra={"offer_id": item.offer_id, "error": str(exc)}
                )

    def _apply_updates(self, items: Sequence[OfferQualityModel]) -> None:
        ids = [item.offer_id for item in items]
        existing_offer = db.session.query(offer_models.Offer).filter(offer_models.Offer.id.in_(ids)).all()
        offer_map = {offer.id: offer for offer in existing_offer}
        for item in items:
            offer = offer_map.get(item.offer_id)
            if offer:
                if offer.quality is None:
                    offer.quality = offer_models.OfferQuality(completionScore=item.completion_score)
                else:
                    offer.quality.completionScore = item.completion_score
            else:
                logger.info("Skipping scores update for missing offer", extra={"offer_id": item.offer_id})
