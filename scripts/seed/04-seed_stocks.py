import argparse
import logging
import random
import sys
from decimal import Decimal

from base_generator import BaseGenerator
from psycopg2.extras import execute_values

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


class StockGenerator(BaseGenerator):
    def generate_stocks(self, count: int):
        logger.info(f"Generating {count:,} stocks...")

        offer_ids = self.get_ids("offer")
        all_stock_data: list[dict] = []
        batch_size = 10000

        for batch_start in range(0, count, batch_size):
            batch_end = min(batch_start + batch_size, count)
            values = []

            for i in range(batch_start, batch_end):
                offer_id = random.choice(offer_ids)
                price = Decimal(
                    random.choice([5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 50.0, 100.0])
                )
                date_created = self.generate_random_date(self.start_date, self.end_date)
                values.append(
                    (
                        offer_id,
                        price,
                        date_created,
                        False,
                        date_created,
                    )
                )

            for db_name, conn in self.connections.items():
                with conn.cursor() as cursor:
                    execute_values(
                        cursor,
                        """
                        INSERT INTO stock (
                            "offerId", price, "dateCreated", "isSoftDeleted", "dateModified"
                        )
                        VALUES %s
                        RETURNING id, "offerId", price
                        """,
                        values,
                        page_size=len(values),
                    )

                    if db_name == "postgres":
                        for row in cursor.fetchall():
                            stock_id, offer_id, price = row
                            all_stock_data.append(
                                {
                                    "id": stock_id,
                                    "offerId": offer_id,
                                    "price": float(price),
                                }
                            )

        logger.info(f"{len(all_stock_data):,} stocks created.")

        return all_stock_data

    def run(self, num_stocks: int):
        logger.info("=" * 80)
        logger.info("Step 4: Seeding stocks")
        logger.info("=" * 80)

        self.load_state()
        self.connect()

        stock_data = self.generate_stocks(num_stocks)
        self.state["stock_count"] = len(stock_data)
        self.save_state()

        logger.info("-" * 80)
        logger.info("Done.")
        logger.info("-" * 80)
        logger.info(f"Stocks: {self.state['stock_count']:,}")

        self.close_connections()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-stocks", type=int, required=True)
    args = parser.parse_args()

    generator = StockGenerator()
    try:
        generator.run(num_stocks=args.num_stocks)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
