import datetime
import enum
import logging

import sqlalchemy.orm as sa_orm
from dateutil.relativedelta import relativedelta

import pcapi.core.mails.transactional as transactional_mails
from pcapi import settings
from pcapi.connectors.dms import api as ds_api
from pcapi.connectors.dms import exceptions as dms_exceptions
from pcapi.connectors.dms import models as dms_models
from pcapi.core.finance import models as finance_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.subscription.phone_validation import exceptions as phone_validation_exceptions
from pcapi.core.users import models as users_models
from pcapi.core.users import repository
from pcapi.core.users.repository import find_user_by_email
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils import email as email_utils
from pcapi.utils import phone_number as phone_number_utils


logger = logging.getLogger(__name__)

# Avoid connection timeout when DS takes time to respond in daily or hourly cloud tasks (not in synchronous requests)
LONG_TIMEOUT = 60

# Sometimes BO users have timeout when accepting, which causes unconsistent data between DS and the backend
UPDATE_STATE_TIMEOUT = 30


class DsUserAccountUpdateProcredureField(enum.Enum):
    """
    All IDs are the same in testing and production procedures, except "Quel est ton nouveau nom ?".
    Let's keep both here instead of a more complex configuration by environment.
    """

    CHOICES = "Q2hhbXAtMzM0NjEyMA=="
    BIRTH_DATE = "Q2hhbXAtMzM0NjAwOQ=="
    OLD_EMAIL = "Q2hhbXAtMzM0NjE0NA=="
    NEW_EMAIL = "Q2hhbXAtMzM0NjE2MA=="
    NEW_PHONE_NUMBER = "Q2hhbXAtMzM2MDE5OQ=="
    NEW_FIRST_NAME = "Q2hhbXAtMzM2MDIwNA=="
    NEW_LAST_NAME = "Q2hhbXAtNDU2NzkwOQ=="
    NEW_LAST_NAME_TESTING = "Q2hhbXAtNDU2NjE2NQ=="


DS_CHOICE_TO_UPDATE_TYPE = {
    # Keep lowercase
    "changement d'adresse de mail": users_models.UserAccountUpdateType.EMAIL,
    "changement de n° de téléphone": users_models.UserAccountUpdateType.PHONE_NUMBER,
    "changement de prénom": users_models.UserAccountUpdateType.FIRST_NAME,
    "changement de nom": users_models.UserAccountUpdateType.LAST_NAME,
    "perte de l'identifiant de connexion": users_models.UserAccountUpdateType.LOST_CREDENTIALS,
    # Deprecated but still existing in applications; may be removed after all applications deleted (early 2027?):
    "compte a les mêmes informations": users_models.UserAccountUpdateType.ACCOUNT_HAS_SAME_INFO,
}

CORRECTION_MESSAGE = {
    "unreadable-photo": """Nous avons bien reçu ta demande, mais nous n’avons pas pu la finaliser car la photo que tu nous as envoyée a été refusée.
Elle était peut-être floue, mal cadrée ou trop sombre. Pas d’inquiétude, cela peut arriver !

Pour que nous puissions valider ton authentification, il faudrait renvoyer une nouvelle photo qui respecte ces critères :
Une photo de toi tenant ta carte d’identité (un selfie).
Assure-toi d’être dans un endroit bien éclairé, et que ton visage ainsi que ta pièce d’identité soient bien visibles.
Une photo de ta pièce d'identité bien lisible.

Attention : Tu disposes de 30 jours pour nous transmettre ce justificatif. Si tu as besoin de conseils pour prendre une photo conforme, tu peux consulter notre article https://aide.passculture.app/hc/fr/articles/4411991953681--Jeunes-Comment-faire-pour-me-prendre-en-photo-avec-ma-pi%C3%A8ce-d-identit%C3%A9""",
    "missing-file": """Nous avons bien reçu ta demande de modification, mais nous n’avons pas pu la finaliser, car il manque un ou plusieurs documents.

Pour que nous puissions traiter ta demande, il faut que tu t’assures que ces deux éléments figurent dans ton dossier Démarche Numérique :
Un document officiel qui justifie ton changement de nom ou prénom (par exemple : acte d’état civil, jugement, certificat de changement de prénom, etc.)
Une photo de ta nouvelle pièce d’identité ou de ton passeport avec ton nom ou prénom à jour, bien lisible.

Attention : Tu disposes de 30 jours pour nous transmettre ce justificatif. Si tu as besoin de conseils pour compléter ton dossier, tu peux consulter notre article https://aide.passculture.app/hc/fr/articles/4411998998673--Jeunes-18-ans-Quels-sont-les-documents-d-identit%C3%A9-accept%C3%A9s-pour-s-inscrire""",
    "refused-file": """Nous avons bien reçu ta demande, mais nous n’avons pas pu la finaliser, car le document d’identité que tu as envoyé n’est pas recevable. Il est peut-être flou, difficile à lire ou ne fait pas partie des documents acceptés.

Pour que nous puissions traiter ta demande, merci de renvoyer une photo lisible d’un des documents suivants :
Passeport
Carte nationale d’identité (CNI)
Titre de séjour

La pièce d’identité doit être bien visible, lisible et à ton nom.

Attention : Tu disposes de 30 jours pour nous transmettre ce justificatif. Si tu as besoin de conseils pour compléter ton dossier, tu peux consulter notre article https://aide.passculture.app/hc/fr/articles/4411998998673--Jeunes-18-ans-Quels-sont-les-documents-d-identit%C3%A9-accept%C3%A9s-pour-s-inscrire""",
}

IDENTITY_THEFT_MESSAGE = """Si tu suspectes une usurpation d’identité, il est important de déposer une plainte officielle auprès des autorités compétentes, une simple main courante ne suffit pas.
 
Pour rappel, l’inscription au pass Culture nécessite la présentation d’une pièce d’identité. Si un compte a été créé à ton insu, cela signifie que quelqu’un a pu accéder à tes informations et utiliser ton crédit.

Une fois la plainte déposée, tu peux nous la transmettre à l’adresse suivante : service.fraude@passculture.app"""


def sync_instructor_ids(procedure_number: int) -> None:
    logger.info("[DS] Sync instructor ids from DS procedure %s", procedure_number)

    ds_client = ds_api.DMSGraphQLClient(timeout=LONG_TIMEOUT)
    instructors = ds_client.get_instructors(procedure_number=procedure_number)
    emails = instructors.keys()

    users = (
        db.session.query(users_models.User)
        .outerjoin(users_models.User.backoffice_profile)
        .filter(
            users_models.User.email.in_(list(emails)),
            perm_models.BackOfficeUserProfile.id.is_not(None),
        )
        .options(
            sa_orm.load_only(users_models.User.email),
            sa_orm.contains_eager(users_models.User.backoffice_profile).load_only(
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
    procedure_number: int,
    since: datetime.datetime | None,
    set_without_continuation: bool = False,
) -> list:
    logger.info("[DS] Started processing User Update Account procedure %s", procedure_number)

    # Fetch instructors' User IDs only once
    user_id_by_email: dict[str, int] = dict(
        db.session.query(users_models.User.email, users_models.User.id)  # type: ignore [arg-type]
        .join(users_models.User.backoffice_profile)
        .filter(perm_models.BackOfficeUserProfile.dsInstructorId.is_not(None))
        .all()
    )

    ds_client = ds_api.DMSGraphQLClient(timeout=LONG_TIMEOUT)
    application_numbers = []

    for node in ds_client.get_beneficiary_account_update_nodes(procedure_number=procedure_number, since=since):
        try:
            ds_application_id = _sync_ds_application(procedure_number, node, user_id_by_email, set_without_continuation)
        except Exception:
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


def check_set_without_continuation(user_request: users_models.UserAccountUpdateRequest, node: dict, data: dict) -> None:
    last_user_action_date = (
        max([_from_ds_date(node["dateDerniereModificationChamps"]), data["dateLastUserMessage"]])
        if data["dateLastUserMessage"]
        else _from_ds_date(node["dateDerniereModificationChamps"])
    )

    if (
        user_request.status
        in (
            dms_models.GraphQLApplicationStates.draft,
            dms_models.GraphQLApplicationStates.on_going,
        )
        and data["dateLastInstructorMessage"] is not None
        and data["dateLastInstructorMessage"]
        + relativedelta(days=settings.DS_MARK_WITHOUT_CONTINUATION_UDPATE_REQUEST_DEADLINE)
        < date_utils.get_naive_utc_now().astimezone(datetime.timezone.utc)
        and data["dateLastInstructorMessage"] > last_user_action_date
    ):
        try:
            update_state(
                user_request,
                new_state=dms_models.GraphQLApplicationStates.without_continuation,
                instructor=None,  # If set, lastInstructor may no longer have access, mark with default api user
                motivation=f"Dossier classé sans suite car pas de correction apportée au dossier depuis {settings.DS_MARK_WITHOUT_CONTINUATION_UDPATE_REQUEST_DEADLINE} jours",
            )
        except (dms_exceptions.DmsGraphQLApiError, dms_exceptions.DmsGraphQLApiException):
            pass

        recipient_email = data["newEmail"] or (user_request.user.email if user_request.user else data["email"])
        transactional_mails.send_beneficiary_update_request_set_to_without_continuation(recipient_email)


def _reject_user_request_with_duplicates(user_request: users_models.UserAccountUpdateRequest, data: dict) -> None:
    motivation = ""
    if data.get("newEmail"):
        if user_request.user and data["oldEmail"] == data["newEmail"]:
            motivation = "Dossier rejeté car le nouvel email et l'ancien sont identiques dans le formulaire"
            transactional_mails.send_beneficiary_update_request_reject_for_duplicate_email(user_request)
        else:
            credited_user_with_same_email = (
                db.session.query(users_models.User)
                .join(finance_models.Deposit)
                .filter(users_models.User.email == data["newEmail"])
                .exists()
            )
            if db.session.query(credited_user_with_same_email).scalar():
                motivation = "Dossier rejeté car l'email est déjà utilisé par un compte crédité"
                transactional_mails.send_beneficiary_update_request_reject_for_already_used_email(user_request)

    elif data.get("newPhoneNumber"):
        if user_request.user and user_request.user.phoneNumber == data["newPhoneNumber"]:
            motivation = "Dossier rejeté car le numéro de téléphone est déjà enregistré sur ton compte"
            transactional_mails.send_beneficiary_update_request_reject_for_duplicate_phone_number(user_request)
        else:
            credited_user_with_same_phone_number = (
                db.session.query(users_models.User)
                .join(finance_models.Deposit)
                .filter(users_models.User.phoneNumber == data["newPhoneNumber"])
                .exists()
            )
            if db.session.query(credited_user_with_same_phone_number).scalar():
                motivation = "Dossier rejeté car le numéro de téléphone est déjà utilisé par un compte crédité"
                transactional_mails.send_beneficiary_update_request_reject_for_already_used_phone_number(user_request)

    elif (
        data.get("newFirstName")
        and not data.get("newLastName")
        and user_request.user
        and user_request.user.firstName == data.get("newFirstName")
    ):
        motivation = "Dossier rejeté car le prénom est déjà celui enregistré sur ton compte"
        transactional_mails.send_beneficiary_update_request_reject_for_duplicate_full_name(user_request)

    elif (
        data.get("newLastName")
        and not data.get("newFirstName")
        and user_request.user
        and user_request.user.lastName == data.get("newLastName")
    ):
        motivation = "Dossier rejeté car le nom est déjà celui enregistré sur ton compte"
        transactional_mails.send_beneficiary_update_request_reject_for_duplicate_full_name(user_request)

    elif (
        data.get("newFirstName")
        and data.get("newLastName")
        and user_request.user
        and user_request.user.firstName == data.get("newFirstName")
        and user_request.user.lastName == data.get("newLastName")
    ):
        motivation = "Dossier rejeté car les nom et prénom sont déjà ceux enregistrés sur ton compte"
        transactional_mails.send_beneficiary_update_request_reject_for_duplicate_full_name(user_request)

    if motivation:
        try:
            update_state(
                user_request,
                new_state=dms_models.GraphQLApplicationStates.refused,
                instructor=None,  # If set, lastInstructor may no longer have access, refuse with default api user
                motivation=motivation,
            )
        except (dms_exceptions.DmsGraphQLApiError, dms_exceptions.DmsGraphQLApiException):
            pass


def _sync_ds_application(
    procedure_number: int, node: dict, user_id_by_email: dict, set_without_continuation: bool
) -> int | None:
    try:
        ds_application_id = node["number"]
        fields = node.get("champs", [])
        instructors = node.get("instructeurs", [])
        messages = node.get("messages", [])
        user_messages = [message for message in messages if message["email"] == node["usager"]["email"]]
        instructor_messages = [message for message in messages if message["email"].endswith("@passculture.app")]

        if instructors:
            last_instructor_email = instructors[-1]["email"]
        elif instructor_messages:
            last_instructor_email = instructor_messages[-1]["email"]
        else:
            last_instructor_email = None

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
            "lastInstructorId": user_id_by_email.get(last_instructor_email) if last_instructor_email else None,
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
                    data["updateTypes"] = [DS_CHOICE_TO_UPDATE_TYPE.get(value.lower()) for value in field["values"]]

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
                        already_exisiting_user = find_user_by_email(value)
                        if already_exisiting_user is not None and not already_exisiting_user.deposit:
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

                case (
                    DsUserAccountUpdateProcredureField.NEW_LAST_NAME.value
                    | DsUserAccountUpdateProcredureField.NEW_LAST_NAME_TESTING.value
                ):
                    value = field["value"].strip() if field["value"] else None
                    if field["value"]:
                        data["newLastName"] = value
                    else:
                        data["flags"].add(users_models.UserAccountUpdateFlag.MISSING_VALUE)

        for message in reversed(messages):
            correction = message.get("correction")
            if correction:
                if correction.get("dateResolution"):
                    data["flags"].add(users_models.UserAccountUpdateFlag.CORRECTION_RESOLVED)
                else:
                    data["flags"].add(users_models.UserAccountUpdateFlag.WAITING_FOR_CORRECTION)
                break

        user_request = (
            db.session.query(users_models.UserAccountUpdateRequest)
            .filter_by(dsApplicationId=ds_application_id)
            .one_or_none()
        )

        ref_email = data.get("oldEmail") or data["email"]
        # Keep user associated in database when it has been set manually by support
        if not (user_request and (user_request.is_user_set_manually or user_request.is_closed)):
            data["user"] = repository.find_user_by_email(ref_email)

        if node["archived"]:
            if user_request:
                db.session.delete(user_request)
        else:
            if user_request:
                user_request_ref_email = user_request.oldEmail if user_request.has_email_update else user_request.email
                data["flags"] |= user_request.persistent_flags
                for key, value in data.items():
                    setattr(user_request, key, value)
            else:
                user_request_ref_email = None
                user_request = users_models.UserAccountUpdateRequest(dsApplicationId=ds_application_id, **data)

            db.session.add(user_request)
            db.session.flush()

            if user_request.status in (
                dms_models.GraphQLApplicationStates.draft,
                dms_models.GraphQLApplicationStates.on_going,
            ):
                _reject_user_request_with_duplicates(user_request, data)

            if (user_request_ref_email != ref_email) and data.get("user") is None:
                transactional_mails.send_update_request_user_account_not_found(data["email"], ds_application_id)

            if set_without_continuation:
                check_set_without_continuation(user_request, node, data)

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


def sync_deleted_user_account_update_requests(procedure_number: int, since: datetime.datetime | None = None) -> list:
    logger.info("[DS] Started processing User Update Account to delete, procedure %s", procedure_number)

    ds_client = ds_api.DMSGraphQLClient(timeout=LONG_TIMEOUT)
    application_numbers = []
    count_deleted = 0

    for deleted_application in ds_client.get_deleted_applications(procedure_number, deletedSince=since):
        application_numbers.append(deleted_application.number)

    if application_numbers:
        count_deleted = (
            db.session.query(users_models.UserAccountUpdateRequest)
            .filter(users_models.UserAccountUpdateRequest.dsApplicationId.in_(application_numbers))
            .delete()
        )

    logger.info(
        "[DS] Finished deleting User Update Account procedure %s.",
        procedure_number,
        extra={"procedure_number": procedure_number, "count_deleted": count_deleted},
    )

    return application_numbers


def update_state(
    user_request: users_models.UserAccountUpdateRequest,
    *,
    new_state: dms_models.GraphQLApplicationStates,
    instructor: users_models.User | None,
    motivation: str | None = None,
    disable_notification: bool = False,
) -> None:
    ds_client = ds_api.DMSGraphQLClient(timeout=UPDATE_STATE_TIMEOUT)
    if instructor is not None:
        instructor_id = instructor.backoffice_profile.dsInstructorId
    else:
        instructor_id = settings.DMS_INSTRUCTOR_ID

    if new_state == dms_models.GraphQLApplicationStates.on_going:
        node = ds_client.make_on_going(
            application_techid=user_request.dsTechnicalId,
            instructeur_techid=instructor_id,
            disable_notification=disable_notification,
            raise_if_already_ongoing=True,
        )
    elif new_state == dms_models.GraphQLApplicationStates.accepted:
        node = ds_client.make_accepted(
            application_techid=user_request.dsTechnicalId,
            instructeur_techid=instructor_id,
            motivation=motivation,
            disable_notification=disable_notification,
            from_draft=user_request.is_draft,
        )
    elif new_state == dms_models.GraphQLApplicationStates.without_continuation:
        node = ds_client.mark_without_continuation(
            application_techid=user_request.dsTechnicalId,
            instructeur_techid=instructor_id,
            motivation=motivation,
            disable_notification=disable_notification,
            from_draft=user_request.is_draft,
        )
    elif new_state == dms_models.GraphQLApplicationStates.refused:
        assert motivation  # helps mypy
        node = ds_client.make_refused(
            application_techid=user_request.dsTechnicalId,
            instructeur_techid=instructor_id,
            motivation=motivation,
            disable_notification=disable_notification,
            from_draft=user_request.is_draft,
        )
    else:
        raise NotImplementedError()

    for key, value in _get_updated_data(node).items():
        setattr(user_request, key, value)
    user_request.lastInstructor = instructor
    db.session.add(user_request)
    db.session.flush()


def archive(user_request: users_models.UserAccountUpdateRequest, *, motivation: str) -> None:
    ds_client = ds_api.DMSGraphQLClient()

    if user_request.status in (dms_models.GraphQLApplicationStates.draft, dms_models.GraphQLApplicationStates.on_going):
        ds_client.mark_without_continuation(
            application_techid=user_request.dsTechnicalId,
            instructeur_techid=settings.DMS_INSTRUCTOR_ID,
            motivation=motivation,
            disable_notification=True,
            from_draft=(user_request.status == dms_models.GraphQLApplicationStates.draft),
        )

    ds_client.archive_application(
        application_techid=user_request.dsTechnicalId,
        instructeur_techid=settings.DMS_INSTRUCTOR_ID,
    )

    db.session.delete(user_request)
    db.session.flush()


def send_user_message_with_correction(
    update_request: users_models.UserAccountUpdateRequest, instructor: users_models.User, correction_reason: str
) -> None:
    client = ds_api.DMSGraphQLClient()

    node = client.send_user_message(
        application_scalar_id=update_request.dsTechnicalId,
        instructeur_techid=instructor.backoffice_profile.dsInstructorId,
        body=CORRECTION_MESSAGE[correction_reason],
        with_correction=True,
    )
    update_request.lastInstructor = instructor
    update_request.status = dms_models.GraphQLApplicationStates.draft
    flags: list[users_models.UserAccountUpdateFlag] = [
        flag for flag in update_request.flags if flag != users_models.UserAccountUpdateFlag.CORRECTION_RESOLVED
    ]
    flags.append(users_models.UserAccountUpdateFlag.WAITING_FOR_CORRECTION)
    update_request.flags = flags
    update_request.dateLastStatusUpdate = _from_ds_date(node["dossierEnvoyerMessage"]["message"]["createdAt"])
    update_request.dateLastInstructorMessage = _from_ds_date(node["dossierEnvoyerMessage"]["message"]["createdAt"])

    db.session.add(update_request)
    db.session.flush()
