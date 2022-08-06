from flask_login import login_required

from pcapi.connectors import sirene
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import sirene as sirene_serializers
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint


# This route must be public because it's used when registering a new
# offerer, when the user is not authenticated yet.
@private_api.route("/sirene/siren/<siren>", methods=["GET"])
@spectree_serialize(
    response_model=sirene_serializers.SirenInfo,
    api=blueprint.pro_private_schema,
)
def get_siren_info(siren: str) -> sirene_serializers.SirenInfo:
    info = sirene.get_siren(siren, with_address=True)
    assert info.address  # helps mypy
    return sirene_serializers.SirenInfo(
        siren=siren,
        name=info.name,
        address=sirene_serializers.Address(**info.address.dict()),
    )


@private_api.route("/sirene/siret/<siret>", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=sirene_serializers.SiretInfo,
    api=blueprint.pro_private_schema,
)
def get_siret_info(siret: str) -> sirene_serializers.SiretInfo:
    info = sirene.get_siret(siret)
    assert info.address  # helps mypy
    return sirene_serializers.SiretInfo(
        siret=siret,
        name=info.name,
        address=sirene_serializers.Address(**info.address.dict()),
    )
