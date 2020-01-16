import os
from pathlib import Path

from connectors.thumb_storage import save_thumb
from models import Mediation
from repository.repository import Repository

TUTOS_PATH = Path(os.path.dirname(os.path.realpath(__file__))) / '..' \
             / 'static' / 'tuto_mediations'


def upsert_tuto_mediations():
    _upsert_tuto_mediation(0)
    _upsert_tuto_mediation(1, True)


def _upsert_tuto_mediation(index, has_back=False):
    existing_mediation = Mediation.query.filter_by(tutoIndex=index) \
        .first()
    if existing_mediation:
        return
    mediation = Mediation()
    mediation.tutoIndex = index
    Repository.save(mediation)

    with open(TUTOS_PATH / (str(index) + '.png'), "rb") as f:
        save_thumb(
            mediation,
            f.read(),
            0,
            convert=False,
            image_type='png'
        )

    if has_back:
        with open(TUTOS_PATH / (str(index) + '_verso.png'), "rb") as f:
            save_thumb(
                mediation, f.read(),
                1,
                convert=False,
                image_type='png'
            )

    Repository.save(mediation)
