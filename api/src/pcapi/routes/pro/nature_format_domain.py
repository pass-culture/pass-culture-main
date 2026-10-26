from flask_login import login_required

from pcapi.core.nature_format_domain import nature_format_domain
from pcapi.routes.pro.blueprint import pro_blueprint
from pcapi.routes.serialization.nature_format_domain_serialize import NatureFormatDomainListResponseModel
from pcapi.routes.serialization.nature_format_domain_serialize import NatureFormatDomainResponseModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from . import blueprint


@pro_blueprint.route("/nature-format-domain", methods=["GET"])
@login_required
@spectree_serialize(
    api=blueprint.pro_schema,
    response_model=NatureFormatDomainListResponseModel,
)
@atomic()
def get_nature_format_domain() -> NatureFormatDomainListResponseModel:
    return NatureFormatDomainListResponseModel(
        [NatureFormatDomainResponseModel.model_validate(item) for item in nature_format_domain.NFD]
    )
