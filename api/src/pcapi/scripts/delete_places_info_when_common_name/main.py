from pcapi.core.offerers import models as offerer_models
from pcapi.models import db


for google_place_info_entry_to_delete in (
    offerer_models.GooglePlacesInfo.query.join(offerer_models.Venue)
    .filter(offerer_models.Venue.common_name != offerer_models.Venue.name)
    .with_entities(offerer_models.GooglePlacesInfo)
    .yield_per(100)
):
    db.session.delete(google_place_info_entry_to_delete)
db.session.commit()
