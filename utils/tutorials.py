import os

from connectors.thumb_storage import create_thumb
from models import Mediation
from repository import repository


def upsert_tuto_mediations():
    _upsert_tuto_mediation(0)
    _upsert_tuto_mediation(1, True)


def _upsert_tuto_mediation(index, has_back=False):
    tutos_path = f'{os.path.dirname(os.path.realpath(__file__))}/../static/tuto_mediations'
    existing_mediation = Mediation.query.filter_by(tutoIndex=index).first()

    if existing_mediation:
        return

    mediation = Mediation()
    mediation.tutoIndex = index
    repository.save(mediation)
    image_name_path = f'{tutos_path}/{str(index)}'

    with open(f'{image_name_path}.png', 'rb') as file:
        mediation = create_thumb(mediation,
                                 file.read(),
                                 0,
                                 convert=False,
                                 image_type='png')

    if has_back:
        with open(f'{image_name_path}_verso.png', 'rb') as file:
            mediation = create_thumb(mediation,
                                     file.read(),
                                     1,
                                     convert=False,
                                     image_type='png')

    repository.save(mediation)
