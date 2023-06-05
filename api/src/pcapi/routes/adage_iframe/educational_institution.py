from datetime import datetime

import sqlalchemy as sa

from pcapi.core.educational import models as educational_models
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization import educational_institution
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.serialization.decorator import spectree_serialize


@blueprint.adage_iframe.route("/collective/institution", methods=["GET"])
@spectree_serialize(
    response_model=educational_institution.EducationalInstitutionWithBudgetResponseModel,
    api=blueprint.api,
)
@adage_jwt_required
def get_educational_institution_with_budget(
    authenticated_information: AuthenticatedInformation,
) -> educational_institution.EducationalInstitutionWithBudgetResponseModel:
    institution_uai = authenticated_information.uai

    institution = educational_models.EducationalInstitution.query.filter_by(institutionId=institution_uai)
    institution = institution.options(
        sa.orm.joinedload(educational_models.EducationalInstitution.deposits, innerjoin=True)
    )
    institution = institution.one_or_none()

    if not institution:
        raise ApiErrors(
            {"global": "L'établissement scolaire ne semble pas exister."},
            status_code=404,
        )

    for deposit in institution.deposits:
        if datetime.utcnow().year == deposit.educationalYear.beginningDate.year:
            amount = deposit.get_amount()
            break
    else:
        raise ApiErrors(
            {"global": "L'établissement scolaire ne semble pas avoir de budget pour cette année."},
            status_code=404,
        )

    return educational_institution.EducationalInstitutionWithBudgetResponseModel(
        id=institution.id,
        name=institution.name,
        institutionType=institution.institutionType,
        postalCode=institution.postalCode,
        city=institution.city,
        phoneNumber=institution.phoneNumber,
        budget=amount,
    )
