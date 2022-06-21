import logging
import re
import typing

from dateutil import parser as date_parser

from pcapi.connectors.dms import models as dms_models
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import exceptions as subscription_exceptions
from pcapi.core.subscription.dms import models as dms_types
from pcapi.core.users import models as users_models
from pcapi.utils.date import FrenchParserInfo


logger = logging.getLogger(__name__)


DMS_ACTIVITY_ENUM_MAPPING = {
    "Lycéen": users_models.ActivityEnum.HIGH_SCHOOL_STUDENT.value,
    "Étudiant": users_models.ActivityEnum.STUDENT.value,
    "Etudiant": users_models.ActivityEnum.STUDENT.value,
    "Employé": users_models.ActivityEnum.EMPLOYEE.value,
    "En recherche d'emploi ou chômeur": users_models.ActivityEnum.UNEMPLOYED.value,
    "Inactif (ni en emploi ni au chômage), En incapacité de travailler": users_models.ActivityEnum.INACTIVE.value,
    "Apprenti": users_models.ActivityEnum.APPRENTICE.value,
    "Alternant": users_models.ActivityEnum.APPRENTICE_STUDENT.value,
    "Volontaire en service civique rémunéré": users_models.ActivityEnum.VOLUNTEER.value,
}


def parse_beneficiary_information_graphql(
    application_detail: dms_models.DmsApplicationResponse, procedure_id: int
) -> fraud_models.DMSContent:

    application_number = application_detail.number
    civility = application_detail.applicant.civility
    email = application_detail.profile.email
    first_name = application_detail.applicant.first_name
    last_name = application_detail.applicant.last_name
    registration_datetime = application_detail.draft_date
    processed_datetime = application_detail.processed_datetime

    # Fields that may be filled
    activity = None
    address = None
    birth_date = None
    city = None
    department = None
    id_piece_number = None
    phone = None
    postal_code = None

    parsing_errors: list[dms_types.DmsParsingErrorDetails] = []

    if not fraud_api.is_subscription_name_valid(first_name):
        parsing_errors.append(
            dms_types.DmsParsingErrorDetails(key=dms_types.DmsParsingErrorKeyEnum.first_name, value=first_name)
        )

    if not fraud_api.is_subscription_name_valid(last_name):
        parsing_errors.append(
            dms_types.DmsParsingErrorDetails(key=dms_types.DmsParsingErrorKeyEnum.last_name, value=last_name)
        )

    for field in application_detail.fields:
        label = field.label
        value = field.value

        if label in (dms_models.FieldLabel.BIRTH_DATE_ET.value, dms_models.FieldLabel.BIRTH_DATE_FR.value):
            try:
                birth_date = date_parser.parse(value, FrenchParserInfo())  # type: ignore [arg-type]
            except Exception:  # pylint: disable=broad-except
                parsing_errors.append(
                    dms_types.DmsParsingErrorDetails(key=dms_types.DmsParsingErrorKeyEnum.birth_date, value=value)
                )

        elif label in (dms_models.FieldLabel.TELEPHONE_FR.value, dms_models.FieldLabel.TELEPHONE_ET.value):
            phone = value.replace(" ", "")  # type: ignore [union-attr]
        elif label in (
            dms_models.FieldLabel.POSTAL_CODE_ET.value,
            dms_models.FieldLabel.POSTAL_CODE_FR.value,
            dms_models.FieldLabel.POSTAL_CODE_OLD.value,
        ):
            space_free = str(value).strip().replace(" ", "")
            try:
                postal_code = re.search("^[0-9]{5}", space_free).group(0)  # type: ignore [union-attr]
            except Exception:  # pylint: disable=broad-except
                parsing_errors.append(
                    dms_types.DmsParsingErrorDetails(key=dms_types.DmsParsingErrorKeyEnum.postal_code, value=value)
                )

        elif label in (dms_models.FieldLabel.ACTIVITY_FR.value, dms_models.FieldLabel.ACTIVITY_ET.value):
            activity = DMS_ACTIVITY_ENUM_MAPPING.get(value) if value else None
            if activity is None:
                logger.error("Unknown activity value for application %s: %s", application_number, value)

        elif label in (
            dms_models.FieldLabel.ADDRESS_ET.value,
            dms_models.FieldLabel.ADDRESS_FR.value,
        ):
            address = value
        elif label in (
            dms_models.FieldLabel.ID_PIECE_NUMBER_FR.value,
            dms_models.FieldLabel.ID_PIECE_NUMBER_ET.value,
            dms_models.FieldLabel.ID_PIECE_NUMBER_PROCEDURE_4765.value,
        ):
            value = value.strip()  # type: ignore [union-attr]
            if not fraud_api.validate_id_piece_number_format_fraud_item(value):
                parsing_errors.append(
                    dms_types.DmsParsingErrorDetails(key=dms_types.DmsParsingErrorKeyEnum.id_piece_number, value=value)
                )
            else:
                id_piece_number = value
        elif label in (dms_models.FieldLabel.CITY_FR.value, dms_models.FieldLabel.CITY_ET.value):
            city = value

    result_content = fraud_models.DMSContent(
        activity=activity,
        address=address,
        application_number=application_number,
        birth_date=birth_date,
        city=city,
        civility=_parse_dms_civility(civility),
        department=department,
        email=email,
        first_name=first_name,
        id_piece_number=id_piece_number,
        last_name=last_name,
        phone=phone,
        postal_code=postal_code,
        procedure_id=procedure_id,
        processed_datetime=processed_datetime,
        registration_datetime=registration_datetime,
        state=application_detail.state.value,
    )

    if parsing_errors:
        raise subscription_exceptions.DMSParsingError(email, parsing_errors, result_content, "Error validating")
    return result_content


def _parse_dms_civility(civility: dms_models.Civility) -> typing.Optional[users_models.GenderEnum]:
    if civility == dms_models.Civility.M:
        return users_models.GenderEnum.M
    if civility == dms_models.Civility.MME:
        return users_models.GenderEnum.F
    return None
