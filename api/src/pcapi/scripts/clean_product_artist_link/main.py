import logging

from pcapi.app import app
from pcapi.connectors.big_query.importer.artist import ArtistProductLinkImporter


logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Starting artists update from delta tables...")
    ArtistProductLinkImporter().run_delta_update()
    logger.info("Artists update from delta tables finished successfully.")


if __name__ == "__main__":
    app.app_context().push()
    main()
