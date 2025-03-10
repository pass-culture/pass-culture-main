import logging

from pcapi.app import app
from pcapi.core.artist.commands import import_all_artists_data


logger = logging.getLogger(__name__)

if __name__ == "__main__":
    app.app_context().push()

    import_all_artists_data()
