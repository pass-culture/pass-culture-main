import argparse
import logging

from pcapi.flask_app import app


logger = logging.getLogger(__name__)


def synchronize_venues_with_acceslibre(venue_ids: list[int], dry_run: bool = True) -> None:
    synchronize_venues_with_acceslibre(venue_ids, dry_run)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("venue_ids", type=int, nargs=-1, required=True)
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=False)
    args = parser.parse_args()
    with app.app_context():
        synchronize_venues_with_acceslibre(dry_run=args.dry_run, venue_ids=args.venue_ids)


if __name__ == "__main__":
    main()
