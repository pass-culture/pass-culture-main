from models import AllocinePivot
from repository import repository
from scripts.link_theater_and_siret_in_allocine_pivot import link_theater_to_siret
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_venue, create_offerer


@clean_database
def test_can_create_link_between_siret_and_theater(app):
    # Given
    offerer = create_offerer(siren='123456789')
    venue = create_venue(offerer, siret='12345678900001')
    repository.save(venue)
    theater_id = 'XXXXXXXXXXXXXXXXXX=='

    # When
    link_theater_to_siret('12345678900001', theater_id)

    # Then
    assert AllocinePivot.query.filter_by(siret='12345678900001', theaterId='XXXXXXXXXXXXXXXXXX==').one() is not None
