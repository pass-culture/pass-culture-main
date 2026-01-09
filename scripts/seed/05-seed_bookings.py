import argparse
import logging
import random
import sys
from datetime import datetime, timedelta

from base_generator import BaseGenerator
from psycopg2.extras import execute_values

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def parse_shard(shard_str: str) -> tuple[int, int]:
    """Parse shard string like '1/2' into (shard_index, total_shards)."""
    parts = shard_str.split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid shard format: {shard_str}. Expected format: '1/2'")
    shard_index = int(parts[0])
    total_shards = int(parts[1])
    if shard_index < 1 or shard_index > total_shards:
        raise ValueError(
            f"Invalid shard index: {shard_index}. Must be between 1 and {total_shards}"
        )
    if total_shards < 1:
        raise ValueError(f"Invalid total shards: {total_shards}. Must be at least 1")
    return shard_index, total_shards


def calculate_shard_range(
    total_count: int, shard_index: int, total_shards: int
) -> tuple[int, int]:
    """Calculate the start and end indices for a given shard."""
    base_size = total_count // total_shards
    remainder = total_count % total_shards
    start = 0
    for i in range(1, shard_index):
        start += base_size + (1 if i <= remainder else 0)
    shard_size = base_size + (1 if shard_index <= remainder else 0)
    end = start + shard_size
    return start, end


class BookingGenerator(BaseGenerator):
    def load_stock_data(self) -> list[dict]:
        """Load stock id and price from the database."""
        conn = self.connections.get("postgres")
        if not conn:
            return []
        with conn.cursor() as cursor:
            cursor.execute('SELECT id, price FROM stock ORDER BY id')
            return [{"id": row[0], "price": float(row[1])} for row in cursor.fetchall()]

    def generate_random_date_recent_bias(
        self, start: datetime, end: datetime
    ) -> datetime:
        """Generate random date with quadratic bias toward recent dates."""
        time_between = end - start
        days_between = time_between.days
        random_factor = random.random() ** 2
        random_days = int(days_between * random_factor)
        random_date = end - timedelta(days=random_days)
        random_seconds = random.randint(0, 86400)
        return random_date + timedelta(seconds=random_seconds)

    def generate_booking_token(self, booking_number: int) -> str:
        """Generate a unique 6-character token for a booking based on its number."""
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        base = len(chars)
        token = ""
        num = booking_number
        for _ in range(6):
            token = chars[num % base] + token
            num //= base
        return token

    def generate_bookings(
        self,
        count: int,
        shard_index: int,
        total_shards: int,
    ):
        shard_start, shard_end = calculate_shard_range(count, shard_index, total_shards)
        shard_count = shard_end - shard_start
        logger.info(
            f"Shard {shard_index}/{total_shards}: Generating bookings {shard_start + 1:,} to {shard_end:,} "
            f"({shard_count:,} bookings)..."
        )

        user_ids = self.get_ids("user")
        deposit_ids = self.get_ids("deposit")
        venue_ids = self.get_ids("venue")
        offerer_ids = self.get_ids("offerer")

        stock_data = self.load_stock_data()
        if not stock_data:
            logger.error("No stock data found in database! Run step 4 first.")
            sys.exit(1)

        current_booking_count = self.state.get("booking_count", 0)
        new_booking_count = 0
        booking_counter = shard_start

        status_distribution = [
            ("CONFIRMED", 50),
            ("USED", 30),
            ("CANCELLED", 15),
            ("REIMBURSED", 5),
        ]
        statuses = []
        for status, percentage in status_distribution:
            statuses.extend([status] * percentage)

        random.seed(shard_index)

        values = []
        for _ in range(shard_count):
            stock = random.choice(stock_data)
            user_id = random.choice(user_ids)
            deposit_id = random.choice(deposit_ids)
            venue_id = random.choice(venue_ids)
            offerer_id = random.choice(offerer_ids)
            status = random.choice(statuses)
            token = self.generate_booking_token(booking_counter)
            booking_counter += 1

            date_created = self.generate_random_date_recent_bias(
                self.start_date, self.end_date
            )

            cancellation_limit_date = date_created + timedelta(
                days=random.randint(1, 30)
            )

            date_used = None
            cancellation_date = None
            reimbursement_date = None

            if status == "USED":
                date_used = date_created + timedelta(days=random.randint(0, 30))
            elif status == "CANCELLED":
                cancellation_date = date_created + timedelta(days=random.randint(0, 7))
            elif status == "REIMBURSED":
                date_used = date_created + timedelta(days=random.randint(0, 30))
                reimbursement_date = date_used + timedelta(days=random.randint(7, 60))

            values.append(
                (
                    stock["id"],
                    user_id,
                    1,
                    stock["price"],
                    date_created,
                    status,
                    offerer_id,
                    venue_id,
                    token,
                    cancellation_limit_date,
                    date_used,
                    cancellation_date,
                    reimbursement_date,
                    deposit_id,
                )
            )

        for db_name, conn in self.connections.items():
            with conn.cursor() as cursor:
                execute_values(
                    cursor,
                    """
                    INSERT INTO booking (
                        "stockId", "userId", quantity, amount, "dateCreated",
                        status, "offererId", "venueId", token, "cancellationLimitDate",
                        "dateUsed", "cancellationDate", "reimbursementDate", "depositId"
                    )
                    VALUES %s
                    RETURNING id
                    """,
                    values,
                    page_size=len(values),
                )
                if db_name == "postgres":
                    new_booking_count = cursor.rowcount

        logger.info(
            f"Shard {shard_index}/{total_shards} complete: {new_booking_count:,} bookings created"
        )
        return current_booking_count + new_booking_count

    def run(
        self,
        num_bookings: int,
        shard_index: int,
        total_shards: int,
    ):
        logger.info("=" * 80)
        logger.info(f"Step 5: Seeding bookings (shard {shard_index}/{total_shards})")
        logger.info("=" * 80)

        self.load_state()
        self.connect()

        self.state["booking_count"] = self.generate_bookings(
            num_bookings, shard_index, total_shards
        )
        self.save_state()

        logger.info("-" * 80)
        logger.info("Done.")
        logger.info("-" * 80)
        logger.info(f"Total Bookings: {self.state['booking_count']:,}")

        self.close_connections()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--num-bookings",
        type=int,
        required=True,
    )
    parser.add_argument(
        "--shard",
        type=str,
        default="1/1",
        help="Shard specification in format 'index/total' (e.g., '1/2' for first of two shards)",
    )
    args = parser.parse_args()

    try:
        shard_index, total_shards = parse_shard(args.shard)
    except ValueError as e:
        logger.error(f"Invalid shard format: {e}")
        sys.exit(1)

    generator = BookingGenerator()
    try:
        generator.run(
            num_bookings=args.num_bookings,
            shard_index=shard_index,
            total_shards=total_shards,
        )
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
