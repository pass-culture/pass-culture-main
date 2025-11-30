import json
import logging
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

import psycopg2

STATE_FILE = Path(__file__).parent / "seed_state.json"

POSTGRES_PORT = 5434
TIMESCALEDB_PORT = 5435


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


class BaseGenerator:
    def __init__(
        self,
    ):
        self.host = "0.0.0.0"
        self.database = "pass_culture"
        self.user = "pass_culture"
        self.password = "passq"
        self.connections: dict[str, psycopg2.extensions.connection] = {}
        self.start_date = datetime(2020, 1, 1)
        self.end_date = datetime(2025, 1, 1)
        self.state = {}

    def connect(self):
        logger.info("Connecting to databases...")
        for name, port in [
            ("postgres", POSTGRES_PORT),
            ("timescaledb", TIMESCALEDB_PORT),
        ]:
            conn_str = f"host={self.host} port={port} dbname={self.database} user={self.user} password={self.password}"
            self.connections[name] = psycopg2.connect(conn_str)
            self.connections[name].autocommit = True
            logger.info(f"Connected to `{name}` on port `{port}`.")

    def close_connections(self):
        for name, conn in self.connections.items():
            conn.close()
            logger.info(f"Disconnected from `{name}`.")

    def load_state(self):
        logger.info(f"Loading state from {STATE_FILE}...")
        if not STATE_FILE.exists():
            logger.error("State file not found! Run step 1 first.")
            sys.exit(1)

        with open(STATE_FILE, "r") as f:
            self.state = json.load(f)

        logger.info("State loaded:")
        logger.info(f"- Addresses: {len(self.state.get('address_ids', [])):,}")
        logger.info(f"- Bookings: {len(self.state.get('booking_ids', [])):,}")
        logger.info(f"- Deposits: {len(self.state.get('deposit_ids', [])):,}")
        logger.info(f"- Offerers: {len(self.state.get('offerer_ids', [])):,}")
        logger.info(
            f"- Offerer Addresses: {len(self.state.get('offerer_address_ids', [])):,}"
        )
        logger.info(f"- Offers: {len(self.state.get('offer_ids', [])):,}")
        logger.info(f"- Stocks: {len(self.state.get('stock_data', [])):,}")
        logger.info(f"- Venues: {len(self.state.get('venue_ids', [])):,}")
        logger.info(f"- Users: {len(self.state.get('user_ids', [])):,}")

    def save_state(self):
        logger.info(f"Saving state to {STATE_FILE}...")
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)
        logger.info("State saved.")

    def generate_random_date(self, start: datetime, end: datetime) -> datetime:
        time_between = end - start
        days_between = time_between.days
        random_days = random.randint(0, days_between)
        random_date = start + timedelta(days=random_days)
        random_seconds = random.randint(0, 86400)

        return random_date + timedelta(seconds=random_seconds)
