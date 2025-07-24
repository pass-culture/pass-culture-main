from flask_login import login_required

from pcapi.core.offerers import api as offerers_api
from pcapi.repository.session_management import atomic
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import sirene as sirene_serializers
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint


@private_api.route("/sirene/siret/<siret>", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    response_model=sirene_serializers.SiretInfo,
    api=blueprint.pro_private_schema,
)
def get_siret_info(siret: str) -> sirene_serializers.SiretInfo:
    info = offerers_api.find_siret_info(siret)
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
