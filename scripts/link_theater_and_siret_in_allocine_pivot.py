from models import AllocinePivot
from repository import repository


def link_theater_to_siret(siret: str, theater_id: str):
    venue_is_already_in_allocine_pivot = AllocinePivot.query.filter_by(theaterId=theater_id).count() == 1
    if venue_is_already_in_allocine_pivot:
        allocine_pivot = AllocinePivot.query.filter_by(theaterId=theater_id).one()
        allocine_pivot.siret = siret
        repository.save(allocine_pivot)
    else:
        new_allocine_pivot = AllocinePivot()
        new_allocine_pivot.siret = siret
        new_allocine_pivot.theaterId = theater_id
        repository.save(new_allocine_pivot)
