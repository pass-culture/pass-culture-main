import itertools
import logging
import time
from typing import Sequence

from sqlalchemy import exc as sa_exc

from pcapi.connectors.big_query.queries.artist import ArtistScoresModel
from pcapi.connectors.big_query.queries.artist import ArtistScoresQuery
from pcapi.core.artist import models as artist_models
from pcapi.models import db
from pcapi.utils.repository import transaction


logger = logging.getLogger(__name__)


class ArtistScoresImporter:
    """
    Imports ranking scores to improve artist search for the "App Jeune" and "Portail Pro".

    For more details on the scoring algorithm and filter implementation:
    https://www.notion.so/passcultureapp/Artistes-Qualit-Scoring-2e9ad4e0ff988063b4b0e9df0b18d290
    """

    def run_scores_update(self, batch_size: int = 1000) -> None:
        logger.info("Starting artist scores update...")

        query = ArtistScoresQuery()
        total_processed = 0

        for batch in itertools.batched(query.execute(), batch_size):
            self._process_batch(batch)
            total_processed += len(batch)

        logger.info("Finished artist scores update", extra={"total_processed": total_processed})

    def _process_batch(self, batch: Sequence[ArtistScoresModel]) -> None:
        if not batch:
            return

        start_time = time.perf_counter()
        try:
            with transaction():
                self._apply_updates(batch)

            duration = time.perf_counter() - start_time
            logger.info(
                "Successfully updated artists batch scores", extra={"batch_size": len(batch), "duration": duration}
            )

        except sa_exc.SQLAlchemyError as exc:
            duration = time.perf_counter() - start_time
            logger.warning("Batch update failed. Retrying one by one", extra={"duration": duration, "error": str(exc)})
            self._process_one_by_one(batch)

    def _process_one_by_one(self, batch: Sequence[ArtistScoresModel]) -> None:
        for item in batch:
            try:
                with transaction():
                    self._apply_updates([item])
            except sa_exc.SQLAlchemyError as exc:
                logger.error("Failed to update scores for artist", extra={"artist_id": item.id, "error": str(exc)})

    def _apply_updates(self, items: Sequence[ArtistScoresModel]) -> None:
        ids = [item.id for item in items]
        existing_artists = db.session.query(artist_models.Artist).filter(artist_models.Artist.id.in_(ids)).all()
        artist_map = {artist.id: artist for artist in existing_artists}
        for item in items:
            artist = artist_map.get(item.id)
            if artist:
                artist.app_search_score = item.app_search_score
                artist.pro_search_score = item.pro_search_score
            else:
                logger.info("Skipping scores update for missing artist", extra={"artist_id": item.id})
