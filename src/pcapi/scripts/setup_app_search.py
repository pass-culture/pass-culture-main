import argparse
import os
import sys

from pcapi.core.search.backends import appsearch
from pcapi.flask_app import app


def _check_errors(response):
    if not response.ok:
        result = response.json()
        try:
            errors = [result["error"]]
        except KeyError:
            errors = result["errors"]
        print("\n".join(f"ERR: {error}" for error in errors))
        return False
    return True


def setup_engine(engine, engine_names, meta_name=None):
    for engine_name in engine_names:
        response = engine.create_engine(engine_name)
        if not _check_errors(response):
            return
        print(f"{engine_name}: Engine has been created.")

    if meta_name:
        response = engine.create_engine(meta_name, engine_names)
        if not _check_errors(response):
            return
        print(f"{meta_name}: Meta-engine has been created.")

    for engine_name in engine_names + ([meta_name] if meta_name else []):
        if engine_name != meta_name:
            response = engine.update_schema(engine_name)
            if not _check_errors(response):
                return
            print(f"{engine_name}: Schema has been initialized.")

        for response in engine.update_synonyms(engine_name):
            if not _check_errors(response):
                return
        print(f"{engine_name}: Synonyms have been set.")

        response = engine.set_search_settings(engine_name)
        if hasattr(response, "ok") and not _check_errors(response):
            return
        print(f"{engine_name}: Search settings have been set.")


def setup_offers_engines():
    backend = appsearch.AppSearchBackend()
    setup_engine(
        backend.offers_engine, engine_names=appsearch.OFFERS_ENGINE_NAMES, meta_name=appsearch.OFFERS_META_ENGINE_NAME
    )


def setup_educational_offers_engines():
    backend = appsearch.AppSearchBackend()
    setup_engine(backend.offers_engine, engine_names=[appsearch.EDUCATIONAL_OFFER_ENGINE_NAME])


def setup_venues_engine():
    backend = appsearch.AppSearchBackend()
    setup_engine(backend.venues_engine, engine_names=[appsearch.VENUES_ENGINE_NAME])


def index_offers():
    # FIXME (dbaty, 2021-07-01): late import to avoid import loop of models.
    import pcapi.core.offers.models as offers_models

    bookable_offers = []
    for offer in offers_models.Offer.query.all():
        if offer.isBookable:
            print(f"Found {offer} to add to index ({offer.name[:20]}...)")
            bookable_offers.append(offer)

    if not bookable_offers:
        print("ERR: Could not find any bookable offers to index")
        return

    backend = appsearch.AppSearchBackend()
    backend.index_offers(bookable_offers)
    print(f"Successfully created or updated {len(bookable_offers)} offers")


def index_venues():
    # FIXME (antoinewg, 2021-09-15): late import to avoid import loop of models.
    import pcapi.core.offerers.models as offerers_models

    permanent_venues = []
    for venue in offerers_models.Venue.query.all():
        if venue.isPermanent:
            print(f"Found {venue} to add to index ({venue.name[:20]}...)")
            permanent_venues.append(venue)

    if not permanent_venues:
        print("ERR: Could not find any permanent venues to index")
        return

    backend = appsearch.AppSearchBackend()
    backend.index_venues(permanent_venues)
    print(f"Successfully created or updated {len(permanent_venues)} venues")


def get_parser():
    parser = argparse.ArgumentParser()

    main_subparsers = parser.add_subparsers()

    # offers
    offers_parser = main_subparsers.add_parser("offers", help="Commands related to offers.")
    offers_subparsers = offers_parser.add_subparsers()
    offers_setup = offers_subparsers.add_parser("setup", help="Setup a new engine for offers.")
    offers_setup.set_defaults(callback=setup_offers_engines)
    educational_offers_setup = offers_subparsers.add_parser(
        "setup_educational",
        help="Setup a new engine for educational offers.",
    )
    educational_offers_setup.set_defaults(callback=setup_educational_offers_engines)
    offers_index = offers_subparsers.add_parser("index", help="Index offers.")
    offers_index.set_defaults(callback=index_offers)

    # venues
    venues_parser = main_subparsers.add_parser("venues", help="Commands related to venues.")
    venues_subparsers = venues_parser.add_subparsers()
    venues_setup = venues_subparsers.add_parser("setup", help="Setup a new engine for venues.")
    venues_setup.set_defaults(callback=setup_venues_engine)
    venues_index = venues_subparsers.add_parser("index", help="Index venues.")
    venues_index.set_defaults(callback=index_venues)

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    if not hasattr(args, "callback"):
        parser.print_usage()
        sys.exit(os.EX_USAGE)

    args = dict(vars(args))
    callback = args.pop("callback")

    with app.app_context():
        callback()


if __name__ == "__main__":
    main()
