import argparse
import json
import logging
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

import bcrypt
import psycopg2
from psycopg2.extras import execute_values

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

STATE_FILE = Path(__file__).parent / "seed_state.json"


class BaseEntityGenerator:
    DEFAULT_PASSWORD_HASH = bcrypt.hashpw("".encode("utf-8"), bcrypt.gensalt())

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.conn_str = (
            f"host={host} port={port} dbname={database} user={user} password={password}"
        )
        self.conn = None
        self.start_date = datetime(2020, 1, 1)
        self.end_date = datetime(2025, 1, 1)
        self.state = {}

    def connect(self):
        logger.info("Connecting to database...")
        self.conn = psycopg2.connect(self.conn_str)
        self.conn.autocommit = True
        logger.info("Connected to database.")

    def generate_random_date(self, start: datetime, end: datetime) -> datetime:
        time_between = end - start
        days_between = time_between.days
        random_days = random.randint(0, days_between)
        random_date = start + timedelta(days=random_days)
        random_seconds = random.randint(0, 86400)
        return random_date + timedelta(seconds=random_seconds)

    def generate_users(self, count: int):
        logger.info(f"Generating {count:,} users...")
        all_ids = []
        batch_size = 10000

        if not self.conn:
            raise ValueError("Database connection is not established")
        with self.conn.cursor() as cursor:
            for batch_start in range(0, count, batch_size):
                batch_end = min(batch_start + batch_size, count)
                values = []

                for i in range(batch_start, batch_end):
                    values.append(
                        (
                            f"user{i}@example.com",
                            f"User{i} First Name",
                            f"User{i} Last Name",
                            self.generate_random_date(self.start_date, self.end_date),
                            True,
                            True,
                            self.DEFAULT_PASSWORD_HASH,
                        )
                    )

                execute_values(
                    cursor,
                    """
                    INSERT INTO "user" (
                        email, "firstName", "lastName", "dateCreated", "isEmailValidated", "hasSeenProTutorials", password
                    )
                    VALUES %s
                    ON CONFLICT (email) DO NOTHING
                    RETURNING id
                    """,
                    values,
                    page_size=len(values),
                )
                all_ids.extend([row[0] for row in cursor.fetchall()])

        logger.info(f"{len(all_ids):,} users created.")
        return all_ids

    def generate_deposits(self, user_ids: list[int]):
        logger.info(f"Generating {len(user_ids):,} deposits...")
        all_ids = []
        batch_size = 10000

        if not self.conn:
            raise ValueError("Database connection is not established")
        with self.conn.cursor() as cursor:
            for batch_start in range(0, len(user_ids), batch_size):
                batch_end = min(batch_start + batch_size, len(user_ids))
                values = []

                for i in range(batch_start, batch_end):
                    user_id = user_ids[i]
                    values.append(
                        (
                            user_id,
                            5000.00,
                            self.generate_random_date(self.start_date, self.end_date),
                            "age-18",
                            1,
                        )
                    )

                execute_values(
                    cursor,
                    """
                    INSERT INTO deposit (
                        "userId", amount, "dateCreated", source, version
                    )
                    VALUES %s
                    RETURNING id
                    """,
                    values,
                    page_size=len(values),
                )
                all_ids.extend([row[0] for row in cursor.fetchall()])

        logger.info(f"{len(all_ids):,} deposits created.")
        return all_ids

    def generate_offerers(self, count: int):
        logger.info(f"Generating {count:,} offerers...")
        all_ids = []
        batch_size = 10000

        if not self.conn:
            raise ValueError("Database connection is not established")
        with self.conn.cursor() as cursor:
            for batch_start in range(0, count, batch_size):
                batch_end = min(batch_start + batch_size, count)
                values = []

                for i in range(batch_start, batch_end):
                    siren = f"{100000000 + i:09d}"
                    values.append(
                        (
                            siren,
                            f"Offerer {i}",
                            self.generate_random_date(self.start_date, self.end_date),
                            True,
                            "VALIDATED",
                        )
                    )

                execute_values(
                    cursor,
                    """
                    INSERT INTO offerer (
                        siren, name, "dateCreated", "isActive", "validationStatus"
                    )
                    VALUES %s
                    ON CONFLICT (siren) DO NOTHING
                    RETURNING id
                    """,
                    values,
                    page_size=len(values),
                )
                all_ids.extend([row[0] for row in cursor.fetchall()])

        logger.info(f"{len(all_ids):,} offerers created.")
        return all_ids

    def generate_addresses(self, count: int):
        logger.info(f"Generating {count:,} addresses...")
        all_ids = []
        batch_size = 10000

        if not self.conn:
            raise ValueError("Database connection is not established")
        with self.conn.cursor() as cursor:
            for batch_start in range(0, count, batch_size):
                batch_end = min(batch_start + batch_size, count)
                values = []

                for i in range(batch_start, batch_end):
                    values.append(
                        (
                            f"{i} Test Street",
                            f"{(i % 90000 + 10000):05d}",
                            "Paris",
                            48.8566 + (i % 100) * 0.001,
                            2.3522 + (i % 100) * 0.001,
                            "75",
                        )
                    )

                execute_values(
                    cursor,
                    """
                    INSERT INTO address (
                        street, "postalCode", city, latitude, longitude, "departmentCode"
                    )
                    VALUES %s
                    RETURNING id
                    """,
                    values,
                    page_size=len(values),
                )
                all_ids.extend([row[0] for row in cursor.fetchall()])

        logger.info(f"{len(all_ids):,} addresses created.")
        return all_ids

    def generate_offerer_addresses(
        self, offerer_ids: list[int], address_ids: list[int]
    ):
        count = min(len(offerer_ids), len(address_ids))
        logger.info(f"Generating {count:,} offerer_addresses...")
        all_ids = []
        batch_size = 10000

        if not self.conn:
            raise ValueError("Database connection is not established")
        with self.conn.cursor() as cursor:
            for batch_start in range(0, count, batch_size):
                batch_end = min(batch_start + batch_size, count)
                values = []

                for i in range(batch_start, batch_end):
                    address_id = address_ids[i]
                    offerer_id = offerer_ids[i]
                    values.append((address_id, offerer_id))

                execute_values(
                    cursor,
                    """
                    INSERT INTO offerer_address (
                        "addressId", "offererId"
                    )
                    VALUES %s
                    RETURNING id
                    """,
                    values,
                    page_size=len(values),
                )
                all_ids.extend([row[0] for row in cursor.fetchall()])

        logger.info(f"{len(all_ids):,} offerer_addresses created.")
        return all_ids

    def save_state(self):
        logger.info(f"Saving state to {STATE_FILE}...")
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)
        logger.info("✓ State saved")

    def run(self, num_users: int, num_offerers: int):
        logger.info("=" * 70)
        logger.info("Step 1: Generating Base Entities")
        logger.info("=" * 70)

        self.connect()

        self.state["user_ids"] = self.generate_users(num_users)
        self.state["deposit_ids"] = self.generate_deposits(self.state["user_ids"])
        self.state["offerer_ids"] = self.generate_offerers(num_offerers)
        self.state["address_ids"] = self.generate_addresses(num_offerers)
        self.state["offerer_address_ids"] = self.generate_offerer_addresses(
            self.state["offerer_ids"], self.state["address_ids"]
        )

        self.save_state()

        logger.info("=" * 70)
        logger.info("✓ Step 1 Complete!")
        logger.info("=" * 70)
        logger.info(f"Users: {len(self.state['user_ids']):,}")
        logger.info(f"Deposits: {len(self.state['deposit_ids']):,}")
        logger.info(f"Offerers: {len(self.state['offerer_ids']):,}")
        logger.info(f"Addresses: {len(self.state['address_ids']):,}")
        logger.info(f"Offerer Addresses: {len(self.state['offerer_address_ids']):,}")

        if not self.conn:
            raise ValueError("Database connection is not established")
        self.conn.close()


def main():
    parser = argparse.ArgumentParser(description="Step 1: Generate base entities")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int)
    parser.add_argument("--database", default="pass_culture")
    parser.add_argument("--user", default="pass_culture")
    parser.add_argument("--password", default="passq")
    parser.add_argument("--num-users", type=int)
    parser.add_argument("--num-offerers", type=int)

    args = parser.parse_args()

    generator = BaseEntityGenerator(
        host=args.host,
        port=args.port,
        database=args.database,
        user=args.user,
        password=args.password,
    )

    try:
        generator.run(num_users=args.num_users, num_offerers=args.num_offerers)
    except Exception as e:
        logger.error(f"✗ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
