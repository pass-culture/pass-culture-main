from models import AllocinePivot
from repository import repository


def override_venue_siret_for_allocine_synchronization(theater_id: str, new_siret: str):
    allocine_pivot = AllocinePivot.query.filter_by(theaterId=theater_id).one()
    allocine_pivot.siret = new_siret
    repository.save(allocine_pivot)
