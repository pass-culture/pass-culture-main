from flask_login import login_required

from pcapi.connectors.entreprise import api as api_entreprise
from pcapi.connectors.entreprise import exceptions as sirene_exceptions
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.models.api_errors import ApiErrors
from pcapi.repository.session_management import atomic
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import sirene as sirene_serializers
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint


# TODO: deprecated, to delete once the frontend does not call this endpoint anymore
@private_api.route("/sirene/siret/<siret>", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    response_model=sirene_serializers.SiretInfo,
    api=blueprint.pro_private_schema,
)
def get_siret_info(siret: str) -> sirene_serializers.SiretInfo:
    info = offerers_api.find_structure_data(siret)
    assert info.address  # helps mypy
    info_address_dict = info.address.dict()
    info_address_dict.pop("insee_code")
    return sirene_serializers.SiretInfo(
        siret=siret,
        name=info.name,
        active=info.active,
        address=sirene_serializers.Address(**info_address_dict),
        ape_code=info.ape_code or "00.00Z",  # APE code can be null, frontend expects a string
        legal_category_code=info.legal_category_code,
    )


@private_api.route("/structure/search/<search_input>", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=sirene_serializers.StructureDataBodyModel,
    api=blueprint.pro_private_schema,
)
def get_structure_data(search_input: str) -> sirene_serializers.StructureDataBodyModel:
    if not api_entreprise.is_valid_siret(search_input) or api_entreprise.is_pass_culture_siret(search_input):
        raise sirene_exceptions.InvalidFormatException()
    try:
        data = offerers_api.find_structure_data(search_input)
        address = offerers_api.find_ban_address_from_insee_address(data.diffusible, data.address)
    except offerers_exceptions.InactiveSirenException:
        raise ApiErrors(errors={"global": ["Ce SIRET n'est pas actif."]})
    return sirene_serializers.StructureDataBodyModel(
        siret=data.siret,
        siren=data.siren,
        name=data.name if data.diffusible else None,
        apeCode=data.ape_code,
        address=address,
        isDiffusible=data.diffusible,
    )
