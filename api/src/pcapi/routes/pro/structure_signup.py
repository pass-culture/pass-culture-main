import logging

from flask_login import current_user
from flask_login import login_required

from pcapi import settings
from pcapi.connectors.api_recaptcha import ReCaptchaException
from pcapi.connectors.api_recaptcha import check_web_recaptcha_token
from pcapi.connectors.entreprise import api as api_entreprise
from pcapi.connectors.entreprise import exceptions as sirene_exceptions
from pcapi.core.mails.transactional import send_signup_simulation_summary_email
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import structure_signup_api
from pcapi.models import feature
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import resource_not_found_error
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import offerers_serialize
from pcapi.routes.serialization import public_information_serialize
from pcapi.routes.serialization import sirene_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from . import blueprint


logger = logging.getLogger(__name__)


@private_api.route("/offerers/new", methods=["POST"])
@atomic()
@login_required
@spectree_serialize(
    on_success_status=201,
    response_model=public_information_serialize.PostOffererResponseModel,
    api=blueprint.pro_private_schema,
)
def signup_structure(
    body: offerers_serialize.SaveNewOnboardingDataQueryModel,
) -> public_information_serialize.PostOffererResponseModel:
    try:
        check_web_recaptcha_token(
            body.token,
            settings.RECAPTCHA_SECRET,
            original_action="saveNewOnboardingData",
            minimal_score=settings.RECAPTCHA_MINIMAL_SCORE,
        )
    except ReCaptchaException:
        raise ApiErrors({"token": "The given token is invalid"})

    try:
        user_offerer = offerers_api.create_from_onboarding_data(current_user, body)
    except offerers_exceptions.InactiveSirenException:
        raise ApiErrors({"siret": "Le SIRET n'est pas actif"})
    except offerers_exceptions.NotACollectivity:
        raise ApiErrors({"siret": "Le SIRET n'appartient pas à une collectivité"})
    except offerers_exceptions.publicNameRequiredException:
        raise ApiErrors({"publicName": "Veuillez renseigner un nom public pour votre structure."})

    return public_information_serialize.PostOffererResponseModel.model_validate(user_offerer.offerer)


@private_api.route("/structure/search/<search_input>", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    response_model=sirene_serialize.StructureDataBodyModel,
    api=blueprint.pro_private_schema,
)
def get_structure_data(search_input: str) -> sirene_serialize.StructureDataBodyModel:
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
        technical_message_id="structure_signup.search",
    )

    return sirene_serialize.StructureDataBodyModel(
        siret=data.siret,
        siren=data.siren,
        name=data.name if data.diffusible else None,
        apeCode=data.ape_code,
        location=address,
        isDiffusible=data.diffusible,
    )


@private_api.route("/structure/check/<search_input>", methods=["GET"])
@atomic()
@spectree_serialize(
    on_success_status=204,
    api=blueprint.pro_private_schema,
)
def check_structure(search_input: str) -> None:
    if not feature.FeatureToggle.WIP_PRE_SIGNUP_SIMULATION.is_active():
        raise resource_not_found_error()

    if not api_entreprise.is_valid_siret(search_input):
        raise sirene_exceptions.InvalidFormatException()

    try:
        data = offerers_api.find_structure_data(search_input)
    except offerers_exceptions.InactiveSirenException:
        raise ApiErrors(errors={"global": ["Ce SIRET n'est pas actif."]})

    logger.info(
        "Searching for structure in signup simulation",
        extra={
            "siret": data.siret,
            "is_diffusible": data.diffusible,
            "legal_category": data.legal_category_code,
            "ape_code": data.ape_code,
        },
        technical_message_id="structure_signup.check",
    )


@private_api.route("/structure/simulate-signup", methods=["POST"])
@atomic()
@spectree_serialize(
    response_model=sirene_serialize.SignupSimulationResponseModel,
    api=blueprint.pro_private_schema,
)
def simulate_signup(
    body: sirene_serialize.SignupSimulationPayload,
) -> sirene_serialize.SignupSimulationResponseModel:
    if not feature.FeatureToggle.WIP_PRE_SIGNUP_SIMULATION.is_active():
        raise resource_not_found_error()

    try:
        data = offerers_api.find_structure_data(body.siret)
    except offerers_exceptions.InactiveSirenException:
        raise ApiErrors(errors={"global": ["Ce SIRET n'est pas actif."]})

    if data.ape_code is None:
        raise ApiErrors(errors={"global": ["Impossible d'effectuer une simulation pour ce SIRET."]})

    result = structure_signup_api.get_signup_documents_and_messages(
        ape_code=data.ape_code,
        legal_category_code=data.legal_category_code,
        is_open_to_public=body.is_open_to_public,
        targets=body.targets,
        activity=offerers_models.Activity[body.activity.name],
    )

    return sirene_serialize.SignupSimulationResponseModel(
        eligibility_documents=result.documents,
        messages=[
            sirene_serialize.SignupSimulationMessageModel(level=message.level, type=message.type)
            for message in result.messages
        ],
    )


@private_api.route("/structure/summarise-signup", methods=["POST"])
@atomic()
@spectree_serialize(
    on_success_status=204,
    api=blueprint.pro_private_schema,
)
def send_signup_simulation_summary(body: sirene_serialize.SignupSimulationSummaryPayload) -> None:
    if not feature.FeatureToggle.WIP_PRE_SIGNUP_SIMULATION.is_active():
        raise resource_not_found_error()

    try:
        data = offerers_api.find_structure_data(body.siret)
    except offerers_exceptions.InactiveSirenException:
        raise ApiErrors(errors={"global": ["Ce SIRET n'est pas actif."]})

    if data.ape_code is None:
        raise ApiErrors(errors={"global": ["Impossible d'effectuer une simulation pour ce SIRET."]})

    activity = offerers_models.Activity[body.activity.name]
    signup_link = structure_signup_api.build_signup_link(
        siret=body.siret,
        is_open_to_public=body.is_open_to_public,
        targets=body.targets,
        activity=activity,
    )
    eligibility_documents = structure_signup_api.get_signup_documents_and_messages(
        ape_code=data.ape_code,
        legal_category_code=data.legal_category_code,
        is_open_to_public=body.is_open_to_public,
        targets=body.targets,
        activity=activity,
    ).documents

    send_signup_simulation_summary_email(
        email=body.email, signup_link=signup_link, eligibility_documents=eligibility_documents
    )

    logger.info(
        "Sending signup simluation summary",
        extra={
            "siret": body.siret,
            "is_open_to_public": body.is_open_to_public,
            "targets": body.targets,
            "activity": body.activity,
            "number_of_documents": len(eligibility_documents),
        },
        technical_message_id="structure_signup.sending_summary",
    )
