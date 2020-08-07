from models import AllocinePivot
from repository import repository


def link_theater_to_siret(siret: str, theater_id: str):
    allocine_pivot = AllocinePivot()
    allocine_pivot.siret = siret
    allocine_pivot.theaterId = theater_id
    repository.save(allocine_pivot)
