from typing import Iterable

from pcapi.core.offerers.api import generate_and_save_api_key
from pcapi.core.offerers.models import ApiKey
from pcapi.core.offerers.models import Offerer
from pcapi.models import db


def generate_and_save_api_key_for_offerer(sirens: Iterable[str]) -> None:
    for siren in sirens:
        offerer = db.session.query(Offerer).filter(Offerer.siren == siren).one_or_none()
        if not offerer:
            print(f"ERR: Unknown SIREN {siren}")
            continue
        exists = ApiKey.query.filter_by(offererId=offerer.id).first()
        if exists:
            print(f"WARN: Found existing key for SIREN {siren}")
            continue
        clear_api_key = generate_and_save_api_key(offerer.id)
        print(f"OK: Created key for SIREN {siren}: {clear_api_key}")
