from pcapi.models import AllocinePivot
from pcapi.repository import repository
from pcapi.scripts.override_venue_siret_for_allocine_synchronization import override_venue_siret_for_allocine_synchronization
import pytest
from pcapi.model_creators.generic_creators import create_allocine_pivot


@pytest.mark.usefixtures("db_session")
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
