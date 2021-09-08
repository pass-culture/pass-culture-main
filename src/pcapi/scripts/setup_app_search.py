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


def setup_offers_engine():
    offers_engine = appsearch.AppSearchBackend().offers_engine
    response = offers_engine.create_engine()
    if not _check_errors(response):
        return
    print("Offer engine has been created.")

    response = offers_engine.update_schema()
    if not _check_errors(response):
        return
    print("Offer schema has been initialized.")

    for response in offers_engine.update_synonyms():
        if not _check_errors(response):
            return
    print("Offer synonyms have been set.")


def index_offers():
    # FIXME (dbaty, 2021-07-01): late import to avoid import loop of models.
    import pcapi.core.offers.models as offers_models

    backend = appsearch.AppSearchBackend()

    offers = offers_models.Offer.query.all()
    documents = []
    for offer in offers:
        if offer.isBookable:
            print(f"Found {offer} to add to index ({offer.name[:20]}...)")
            documents.append(backend.serialize_offer(offer))

    if not documents:
        print("ERR: Could not find any bookable offers to index")
        return

    backend.offers_engine.create_or_update_documents(documents)
    print(f"Successfully created or updated {len(documents)} offers")


def get_parser():
    parser = argparse.ArgumentParser()

    main_subparsers = parser.add_subparsers()

    # engine (setup)
    engine = main_subparsers.add_parser("engine", help="Commands related to engines.")
    engine_subparsers = engine.add_subparsers()
    engine_setup = engine_subparsers.add_parser("setup", help="Setup a new engine.")
    engine_setup.set_defaults(callback=setup_offers_engine)

    # offers (index)
    offers = main_subparsers.add_parser("offers", help="Commands related to offers.")
    offers_subparsers = offers.add_subparsers()
    offers_index = offers_subparsers.add_parser("index", help="Index offers.")
    offers_index.set_defaults(callback=index_offers)

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
