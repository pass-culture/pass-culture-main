# FIXME(fseguin,2022-06-20): remove after it has been successfully executed on all envs
import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.models as offerers_models
from pcapi.models import db


def add_dms_token_to_each_venue(batch_size: int = 100) -> None:
    print(f"[add_dms_token_to_each_venue] {batch_size=} START")

    batch_nr = 1

    query = offerers_models.Venue.query.filter(offerers_models.Venue.dms_token.is_(None))
    venues_to_update = query.limit(batch_size).all()

    while len(venues_to_update) > 0:
        print(f"[add_dms_token_to_each_venue] Batch {batch_nr}")
        for venue in venues_to_update:
            venue.dms_token = offerers_api.generate_dms_token()
            db.session.add(venue)
        db.session.commit()
        batch_nr += 1
        venues_to_update = query.limit(batch_size).all()

    print("[add_dms_token_to_each_venue] END")
