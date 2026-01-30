"""
Please take care not to publish any private information here.
The view is exposed to general view and should not
include GDPR protected data.
"""

from flask_login import login_required

from pcapi.core.offerers import repository as offerers_repository
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import public_information_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from . import blueprint


@private_api.route("/venues/siret/<siret>", methods=["GET"])
@login_required
@atomic()
@spectree_serialize(
    response_model=public_information_serialize.GetVenuesOfOffererFromSiretResponseModel,
    api=blueprint.pro_private_schema,
)
def get_venues_of_offerer_from_siret(
    siret: str,
) -> public_information_serialize.GetVenuesOfOffererFromSiretResponseModel:
    offerer, db_venues = offerers_repository.find_venues_of_offerer_from_siret(siret)
    venue_with_siret = next((v for v in db_venues if v.siret == siret), None)
    if venue_with_siret:
        db_venues.insert(0, db_venues.pop(db_venues.index(venue_with_siret)))
    return public_information_serialize.GetVenuesOfOffererFromSiretResponseModel(
        offererSiren=offerer.siren if offerer else None,
        offererName=offerer.name if offerer else None,
        venues=[
            public_information_serialize.VenueOfOffererFromSiretResponseModel.from_orm(venue) for venue in db_venues
        ],
    )
