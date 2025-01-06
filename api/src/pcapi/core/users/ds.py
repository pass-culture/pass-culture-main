import datetime
import enum
import logging

import sqlalchemy as sa

from pcapi.connectors.dms import api as ds_api
from pcapi.connectors.dms import models as dms_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.subscription.phone_validation import exceptions as phone_validation_exceptions
from pcapi.core.users import models as users_models
from pcapi.core.users import repository
from pcapi.core.users.repository import find_user_by_email
from pcapi.models import db
from pcapi.utils import email as email_utils
from pcapi.utils import phone_number as phone_number_utils


logger = logging.getLogger(__name__)

# Avoid connection timeout when DS takes time to respond in daily or hourly cloud tasks (not in synchronous requests)
LONG_TIMEOUT = 60


class DsUserAccountUpdateProcredureField(enum.Enum):
    CHOICES = "Q2hhbXAtMzM0NjEyMA=="
    BIRTH_DATE = "Q2hhbXAtMzM0NjAwOQ=="
    OLD_EMAIL = "Q2hhbXAtMzM0NjE0NA=="
    NEW_EMAIL = "Q2hhbXAtMzM0NjE2MA=="
    NEW_PHONE_NUMBER = "Q2hhbXAtMzM2MDE5OQ=="
    NEW_FIRST_NAME = "Q2hhbXAtMzM2MDIwNA=="
    NEW_LAST_NAME = "Q2hhbXAtNDU2NjE2NQ=="


DS_CHOICE_TO_UPDATE_TYPE = {
    "changement d'adresse de mail": users_models.UserAccountUpdateType.EMAIL,
    "changement de n° de téléphone": users_models.UserAccountUpdateType.PHONE_NUMBER,
    "changement de prénom": users_models.UserAccountUpdateType.FIRST_NAME,
    "changement de nom": users_models.UserAccountUpdateType.LAST_NAME,
    "compte a les mêmes informations": users_models.UserAccountUpdateType.ACCOUNT_HAS_SAME_INFO,
}


def sync_instructor_ids(procedure_number: int) -> None:
    logger.info("[DS] Sync instructor ids from DS procedure %s", procedure_number)

    ds_client = ds_api.DMSGraphQLClient(timeout=LONG_TIMEOUT)
    instructors = ds_client.get_instructors(procedure_number=procedure_number)
    emails = instructors.keys()

    users = (
        users_models.User.query.outerjoin(users_models.User.backoffice_profile)
        .filter(
            users_models.User.email.in_(list(emails)),
            perm_models.BackOfficeUserProfile.id.is_not(None),
        )
        .options(
            sa.orm.load_only(users_models.User.email),
            sa.orm.contains_eager(users_models.User.backoffice_profile).load_only(
                perm_models.BackOfficeUserProfile.dsInstructorId
            ),
        )
        .all()
    )

    for user in users:
        ds_instructor_id = instructors[user.email]
        if user.backoffice_profile.dsInstructorId != ds_instructor_id:
            user.backoffice_profile.dsInstructorId = ds_instructor_id
            db.session.add(user.backoffice_profile)

    db.session.flush()


def sync_user_account_update_requests(
    procedure_number: int, since: datetime.datetime | None, archived: bool = False
) -> list:
    logger.info("[DS] Started processing User Update Account procedure %s", procedure_number)

    # Fetch instructors' User IDs only once
    user_id_by_email = dict(
        db.session.query(users_models.User.email, users_models.User.id)
        .join(users_models.User.backoffice_profile)
        .filter(perm_models.BackOfficeUserProfile.dsInstructorId.is_not(None))
        .all()
    )

    ds_client = ds_api.DMSGraphQLClient(timeout=LONG_TIMEOUT)
    application_numbers = []

    for node in ds_client.get_beneficiary_account_update_nodes(
        procedure_number=procedure_number, since=since, archived=archived
    ):
        try:
            ds_application_id = _sync_ds_application(procedure_number, node, user_id_by_email)
        except Exception:  # pylint: disable=broad-exception-caught
            # If we don't rollback here, we will persist in the faulty transaction
            # and we won't be able to commit at the end of the process and to set the current import `isProcessing` attr to False
            # Therefore, this import could be seen as on going for other next attempts, forever.
            db.session.rollback()
        else:
            if ds_application_id:
                application_numbers.append(ds_application_id)
            # Committing here ensures that we have a proper transaction for each application successfully imported
            # And that for each faulty application, the failure only impacts that particular one.
            db.session.commit()

    logger.info(
        "[DS] Finished processing User Update Account procedure %s.",
        procedure_number,
        extra={"procedure_number": procedure_number, "count_applications": len(application_numbers)},
    )

    return application_numbers


def _from_ds_date(date_time: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(date_time).astimezone(datetime.timezone.utc)


def _get_updated_data(node: dict) -> dict:
    # data extracted when "dossiers" are synchronized but also after every mutation
    return {
        "dsTechnicalId": node["id"],
        "status": dms_models.GraphQLApplicationStates(node["state"]),
        "dateCreated": _from_ds_date(node["dateDepot"]),
        "dateLastStatusUpdate": _from_ds_date(
            max(
                filter(
                    bool,
                    (
                        node["dateDepot"],
                        node["datePassageEnConstruction"],
                        node["dateDerniereCorrectionEnAttente"],
                        node["dateDerniereModificationChamps"],
                        node["datePassageEnInstruction"],
                        node["dateTraitement"],
                    ),
                )
            )
        ),
    }


def _sync_ds_application(procedure_number: int, node: dict, user_id_by_email: dict) -> int | None:
    try:
        ds_application_id = node["number"]
        fields = node.get("champs", [])
        instructors = node.get("instructeurs", [])
        messages = node.get("messages", [])
        user_messages = [message for message in messages if message["email"] == node["usager"]["email"]]
        instructor_messages = [
            message for message in messages if message["email"] in (instructor["email"] for instructor in instructors)
        ]

        data = {
            "firstName": node["demandeur"]["prenom"],
            "lastName": node["demandeur"]["nom"],
            "email": email_utils.sanitize_email(node["demandeur"]["email"] or node["usager"]["email"]),
            "birthDate": None,
            "updateTypes": [],
            "oldEmail": None,
            "newEmail": None,
            "newPhoneNumber": None,
            "newFirstName": None,
            "newLastName": None,
            "allConditionsChecked": all(field["checked"] for field in fields if "checked" in field),
            "lastInstructorId": user_id_by_email.get(instructors[-1]["email"]) if instructors else None,
            "dateLastUserMessage": _from_ds_date(user_messages[-1]["createdAt"]) if user_messages else None,
            "dateLastInstructorMessage": (
                _from_ds_date(instructor_messages[-1]["createdAt"]) if instructor_messages else None
            ),
            "flags": set(),
        }
        data.update(_get_updated_data(node))

        for field in fields:
            match field["id"]:
                case DsUserAccountUpdateProcredureField.CHOICES.value:
                    data["updateTypes"] = [DS_CHOICE_TO_UPDATE_TYPE.get(value) for value in field["values"]]

                case DsUserAccountUpdateProcredureField.BIRTH_DATE.value:
                    if field["date"]:  # was not mandatory
                        data["birthDate"] = datetime.date.fromisoformat(field["date"])

                case DsUserAccountUpdateProcredureField.OLD_EMAIL.value:
                    value = email_utils.sanitize_email(field["value"].strip()) if field["value"] else None
                    if value:
                        data["oldEmail"] = value
                        if not email_utils.is_valid_email(value):
                            data["flags"].add(users_models.UserAccountUpdateFlag.INVALID_VALUE)
                    else:
                        data["flags"].add(users_models.UserAccountUpdateFlag.MISSING_VALUE)

                case DsUserAccountUpdateProcredureField.NEW_EMAIL.value:
                    value = email_utils.sanitize_email(field["value"].strip()) if field["value"] else None
                    if value:
                        data["newEmail"] = value
                        if not email_utils.is_valid_email(value):
                            data["flags"].add(users_models.UserAccountUpdateFlag.INVALID_VALUE)
                        if find_user_by_email(value) is not None:
                            data["flags"].add(users_models.UserAccountUpdateFlag.DUPLICATE_NEW_EMAIL)
                    else:
                        data["flags"].add(users_models.UserAccountUpdateFlag.MISSING_VALUE)

                case DsUserAccountUpdateProcredureField.NEW_PHONE_NUMBER.value:
                    value = field["value"].strip() if field["value"] else None
                    if value:  # was not mandatory
                        try:
                            data["newPhoneNumber"] = phone_number_utils.ParsedPhoneNumber(value).phone_number
                        except phone_validation_exceptions.InvalidPhoneNumber:
                            data["newPhoneNumber"] = value
                            data["flags"].add(users_models.UserAccountUpdateFlag.INVALID_VALUE)
                    else:
                        data["flags"].add(users_models.UserAccountUpdateFlag.MISSING_VALUE)

                case DsUserAccountUpdateProcredureField.NEW_FIRST_NAME.value:
                    value = field["value"].strip() if field["value"] else None
                    if value:
                        data["newFirstName"] = value
                    else:
                        data["flags"].add(users_models.UserAccountUpdateFlag.MISSING_VALUE)

                case DsUserAccountUpdateProcredureField.NEW_LAST_NAME.value:
                    value = field["value"].strip() if field["value"] else None
                    if field["value"]:
                        data["newLastName"] = value
                    else:
                        data["flags"].add(users_models.UserAccountUpdateFlag.MISSING_VALUE)

        ref_email = data.get("oldEmail") or data["email"]
        data["user"] = repository.find_user_by_email(ref_email)

        for message in reversed(messages):
            correction = message.get("correction")
            if correction:
                if correction.get("dateResolution"):
                    data["flags"].add(users_models.UserAccountUpdateFlag.CORRECTION_RESOLVED)
                else:
                    data["flags"].add(users_models.UserAccountUpdateFlag.WAITING_FOR_CORRECTION)
                break

        user_request = users_models.UserAccountUpdateRequest.query.filter_by(
            dsApplicationId=ds_application_id
        ).one_or_none()
        if node["archived"]:
            if user_request:
                db.session.delete(user_request)
        else:
            if user_request:
                for key, value in data.items():
                    setattr(user_request, key, value)
            else:
                user_request = users_models.UserAccountUpdateRequest(dsApplicationId=ds_application_id, **data)
            db.session.add(user_request)
    except Exception as exc:
        logger.exception(
            "[DS] Application parsing failed with error %s",
            str(exc),
            extra={
                "application_number": node.get("number"),
                "procedure_number": procedure_number,
            },
        )
        raise

    return ds_application_id


def update_state(
    user_request: users_models.UserAccountUpdateRequest,
    *,
    new_state: dms_models.GraphQLApplicationStates,
    instructor: users_models.User,
    motivation: str | None = None,
) -> None:
    ds_client = ds_api.DMSGraphQLClient()

    if new_state == dms_models.GraphQLApplicationStates.on_going:
        node = ds_client.make_on_going(
            application_techid=user_request.dsTechnicalId,
            instructeur_techid=instructor.backoffice_profile.dsInstructorId,
        )
    elif new_state == dms_models.GraphQLApplicationStates.accepted:
        node = ds_client.make_accepted(
            application_techid=user_request.dsTechnicalId,
            instructeur_techid=instructor.backoffice_profile.dsInstructorId,
            motivation=motivation,
        )
    else:
        raise NotImplementedError()

    for key, value in _get_updated_data(node).items():
        setattr(user_request, key, value)
    user_request.lastInstructor = instructor
    db.session.add(user_request)
    db.session.flush()
