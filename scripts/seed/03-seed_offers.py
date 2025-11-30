import argparse
import json
import logging
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

import psycopg2
from base_generator import BaseGenerator
from psycopg2.extras import execute_values

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

STATE_FILE = Path(__file__).parent / "seed_state.json"

POSTGRES_PORT = 5434
TIMESCALEDB_PORT = 5435


class OfferGenerator(BaseGenerator):
    def generate_offers(self, count: int):
        logger.info(f"Generating {count:,} offers...")

        venue_ids = self.state["venue_ids"]
        num_venues = len(venue_ids)

        all_ids: list[int] = []
        batch_size = 10000

        for batch_start in range(0, count, batch_size):
            batch_end = min(batch_start + batch_size, count)
            values = []

            for i in range(batch_start, batch_end):
                venue_id = venue_ids[i % num_venues]
                values.append(
                    (
                        f"Offer {i}",
                        venue_id,
                        self.generate_random_date(self.start_date, self.end_date),
                        False,
                        "SUPPORT_PHYSIQUE_FILM",
                    )
                )

            for db_name, conn in self.connections.items():
                with conn.cursor() as cursor:
                    execute_values(
                        cursor,
                        """
                        INSERT INTO offer (
                            name, "venueId", "dateCreated", "isNational", "subcategoryId"
                        )
                        VALUES %s
                        RETURNING id
                        """,
                        values,
                        page_size=len(values),
                    )
                    if db_name == "postgres":
                        all_ids.extend([row[0] for row in cursor.fetchall()])

        logger.info(f"Created {len(all_ids):,} offers in both databases.")
        return all_ids

    def run(self, num_offers: int):
        logger.info("=" * 80)
        logger.info("Step 3: Seeding offers")
        logger.info("=" * 80)

        self.load_state()
        self.connect()

        self.state["offer_ids"] = self.generate_offers(num_offers)
        self.save_state()

        logger.info("-" * 80)
        logger.info("Done.")
        logger.info("-" * 80)
        logger.info(f"Offers: {len(self.state['offer_ids']):,}")

        self.close_connections()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-offers", type=int, default=2000000)
    args = parser.parse_args()

    generator = OfferGenerator()
    try:
        generator.run(num_offers=args.num_offers)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
