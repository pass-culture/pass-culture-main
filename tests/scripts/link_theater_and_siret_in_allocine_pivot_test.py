from pcapi.models import AllocinePivot
from pcapi.repository import repository
from pcapi.scripts.link_theater_and_siret_in_allocine_pivot import link_theater_to_siret
import pytest
from pcapi.model_creators.generic_creators import create_venue, create_offerer


@pytest.mark.usefixtures("db_session")
def should_create_link_between_siret_and_theater(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    repository.save(venue)
    theater_id = 'XXXXXXXXXXXXXXXXXX=='

    # When
    link_theater_to_siret(venue.siret, theater_id)

    # Then
    assert AllocinePivot.query.filter_by(siret=venue.siret, theaterId=theater_id).one() is not None
