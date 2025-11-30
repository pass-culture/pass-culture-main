import argparse
import logging
import random
import sys

from base_generator import BaseGenerator
from psycopg2.extras import execute_values

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


class VenueGenerator(BaseGenerator):
    def generate_venues(self, count: int):
        logger.info(f"Generating {count:,} venues...")

        offerer_ids = self.state["offerer_ids"]
        offerer_address_ids = self.state["offerer_address_ids"]
        num_offerers = len(offerer_ids)

        dms_token_base = random.randint(100000000, 999999999)
        all_ids: list[int] = []
        batch_size = 10000

        for batch_start in range(0, count, batch_size):
            batch_end = min(batch_start + batch_size, count)
            values = []

            for i in range(batch_start, batch_end):
                offerer_id = offerer_ids[i % num_offerers]
                offerer_address_id = offerer_address_ids[i % num_offerers]
                siret = f"{20000000000000 + i:014d}"
                values.append(
                    (
                        f"Venue {i}",
                        offerer_id,
                        f"{10000 + (i % 90000):05d}",
                        f"{i} Test Street",
                        "Paris",
                        self.generate_random_date(self.start_date, self.end_date),
                        0,
                        f"Venue {i}",
                        True,
                        "OTHER",
                        f"DMS{dms_token_base + i}",
                        offerer_address_id,
                        True,
                        siret,
                    )
                )

            for db_name, conn in self.connections.items():
                with conn.cursor() as cursor:
                    execute_values(
                        cursor,
                        """
                        INSERT INTO venue (
                            name, "managingOffererId", "postalCode", address, city, "dateCreated",
                            "thumbCount", "publicName", "isPermanent", "venueTypeCode", "dmsToken",
                            "offererAddressId", "isOpenToPublic", siret
                        )
                        VALUES %s
                        RETURNING id
                        """,
                        values,
                        page_size=len(values),
                    )
                    if db_name == "postgres":
                        all_ids.extend([row[0] for row in cursor.fetchall()])

        logger.info(f"{len(all_ids):,} venues created.")
        return all_ids

    def run(self, num_venues: int):
        logger.info("=" * 80)
        logger.info("Step 2: Seeding venues")
        logger.info("=" * 80)

        self.load_state()
        self.connect()

        self.state["venue_ids"] = self.generate_venues(num_venues)
        self.save_state()

        logger.info("-" * 80)
        logger.info("Done.")
        logger.info("-" * 80)
        logger.info(f"Venues: {len(self.state['venue_ids']):,}")

        self.close_connections()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-venues", type=int, required=True)
    args = parser.parse_args()

    generator = VenueGenerator()
    try:
        generator.run(num_venues=args.num_venues)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
