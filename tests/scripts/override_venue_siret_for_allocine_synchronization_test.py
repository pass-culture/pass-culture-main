from models import AllocinePivot
from repository import repository
from scripts.override_venue_siret_for_allocine_synchronization import override_venue_siret_for_allocine_synchronization
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_allocine_pivot


@clean_database
def test_should_change_venue_siret_information_for_allocine_synchronization(app):
    # given
    old_siret = '1234567891234'
    new_siret = '5432198765432'
    theater_id = 'XXXXXXXXXXXXXXXXXX=='
    allocine_pivot = create_allocine_pivot(old_siret, theater_id)
    repository.save(allocine_pivot)

    # when
    override_venue_siret_for_allocine_synchronization(theater_id, new_siret)

    # then
    new_allocine_pivot = AllocinePivot.query.one()
    assert new_allocine_pivot.siret == new_siret
