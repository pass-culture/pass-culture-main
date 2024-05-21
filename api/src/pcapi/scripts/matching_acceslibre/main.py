import argparse
import logging

from pcapi.core.offerers import api as offerers_api
from pcapi.flask_app import app


logger = logging.getLogger(__name__)
BATCH_SIZE = 1000


def acceslibre_matching(batch_size: int = 1000, dry_run: bool = False, start_from_batch: int = 1) -> None:
    offerers_api.acceslibre_matching(batch_size, dry_run, start_from_batch)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--start-from-batch", type=int, default=1)
    args = parser.parse_args()
    with app.app_context():
        acceslibre_matching(dry_run=args.dry_run, start_from_batch=args.start_from_batch)


if __name__ == "__main__":
    main()
