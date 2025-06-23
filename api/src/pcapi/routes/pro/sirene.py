from flask_login import login_required

from pcapi.connectors.entreprise import sirene
from pcapi.models import api_errors
from pcapi.repository.session_management import atomic
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import sirene as sirene_serializers
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint


# This route must be public because it's used when registering a new
# offerer, when the user is not authenticated yet.
@private_api.route("/sirene/siren/<siren>", methods=["GET"])
@atomic()
@spectree_serialize(
    response_model=sirene_serializers.SirenInfo,
    api=blueprint.pro_private_schema,
)
def get_siren_info(siren: str) -> sirene_serializers.SirenInfo:
    try:
        int(siren)
    except ValueError:
        raise api_errors.ApiErrors(
            {"code": "INVALID_SIREN", "message": "Siren invalide"},
            status_code=400,
        )
    info = sirene.get_siren(siren, with_address=True)
    assert info.address  # helps mypy
    info_address_dict = info.address.dict()
    info_address_dict.pop("insee_code")
    return sirene_serializers.SirenInfo(
        siren=siren,
        name=info.name,
        address=sirene_serializers.Address(**info_address_dict),
        ape_code=info.ape_code or "00.00Z",  # APE code can be null, frontend expects a string
    )


@private_api.route("/sirene/siret/<siret>", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    response_model=sirene_serializers.SiretInfo,
    api=blueprint.pro_private_schema,
)
def get_siret_info(siret: str) -> sirene_serializers.SiretInfo:
    info = sirene.get_siret(siret)
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
