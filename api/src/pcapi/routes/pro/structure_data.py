import logging

from flask_login import current_user
from flask_login import login_required

from pcapi.connectors.entreprise import api as api_entreprise
from pcapi.connectors.entreprise import exceptions as sirene_exceptions
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import sirene as sirene_serializers
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from . import blueprint


logger = logging.getLogger(__name__)


@private_api.route("/structure/search/<search_input>", methods=["GET"])
@login_required
@atomic()
@spectree_serialize(
    response_model=sirene_serializers.StructureDataBodyModel,
    api=blueprint.pro_private_schema,
)
def get_structure_data(search_input: str) -> sirene_serializers.StructureDataBodyModel:
    if not api_entreprise.is_valid_siret(search_input):
        raise sirene_exceptions.InvalidFormatException()
    try:
        data = offerers_api.find_structure_data(search_input)
        address = offerers_api.find_ban_address_from_insee_address(data.diffusible, data.address)
    except offerers_exceptions.InactiveSirenException:
        raise ApiErrors(errors={"global": ["Ce SIRET n'est pas actif."]})
    except sirene_exceptions.NonPublicDataException:
        raise ApiErrors(
            errors={"global": ["Le propriétaire de ce SIRET s'oppose à la diffusion de ses données au public."]}
        )

    logger.info(
        "Searching for structure",
        extra={"user_id": current_user.id, "siret": data.siret, "is_diffusible": data.diffusible},
        technical_message_id="structure_identification",
    )

    return sirene_serializers.StructureDataBodyModel(
        siret=data.siret,
        siren=data.siren,
        name=data.name if data.diffusible else None,
        apeCode=data.ape_code,
        location=address,
        isDiffusible=data.diffusible,
    )
