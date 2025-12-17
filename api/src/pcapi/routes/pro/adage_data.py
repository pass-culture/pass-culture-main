import logging
import math

from flask_login import login_required

from pcapi.core.educational.api import adage as educational_api_adage
from pcapi.core.educational.api import institution as educational_api_institution
from pcapi.routes.apis import private_api
from pcapi.routes.pro import blueprint
from pcapi.routes.serialization import educational_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)


@private_api.route("/educational_institutions", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    response_model=educational_serialize.EducationalInstitutionsResponseModel,
    on_success_status=200,
    on_error_statuses=[401],
    api=blueprint.pro_private_schema,
)
def get_educational_institutions(
    query: educational_serialize.EducationalInstitutionsQueryModel,
) -> educational_serialize.EducationalInstitutionsResponseModel:
    institutions, total = educational_api_institution.get_all_educational_institutions(
        page=query.page,
        per_page_limit=query.per_page_limit,
    )
    return educational_serialize.EducationalInstitutionsResponseModel(
        educational_institutions=[
            educational_serialize.EducationalInstitutionResponseModelV2(
                id=institution.id,
                name=institution.name,
                institution_type=institution.institutionType,
                postal_code=institution.postalCode,
                city=institution.city,
                phone_number=institution.phoneNumber,
                institution_id=institution.institutionId,
            )
            for institution in institutions
        ],
        page=query.page,
        pages=max(int(math.ceil(total / query.per_page_limit)), 1),
        total=total,
    )


@private_api.route("/cultural-partners", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    response_model=educational_serialize.AdageCulturalPartnersResponseModel,
    on_success_status=200,
    on_error_statuses=[401],
    api=blueprint.pro_private_schema,
)
def get_educational_partners() -> educational_serialize.AdageCulturalPartnersResponseModel:
    venues = educational_api_adage.get_cultural_partners()
    return educational_serialize.AdageCulturalPartnersResponseModel.model_validate(venues)
