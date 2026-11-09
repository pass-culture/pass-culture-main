import pytest

from pcapi.core.artist import models as artist_models
from pcapi.core.highlights import models as highlights_models
from pcapi.models import db
from pcapi.sandboxes.scripts.creators.tiny.create_engagement import create_tiny_engagement


@pytest.mark.usefixtures("db_session")
def test_create_tiny_engagement():
    create_tiny_engagement()

    assert db.session.query(artist_models.Artist).count() == 3
    highlight = db.session.query(highlights_models.Highlight).one()
    assert highlight.name == "Temps fort petit"
    assert highlight.is_available
    assert highlight.highlight_requests == []
