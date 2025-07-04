import datetime
import logging

import factory

from pcapi.connectors.dms import models as dms_models
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users.repository import find_user_by_email
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration


logger = logging.getLogger(__name__)


@log_func_duration
def create_user_account_update_requests() -> None:
    logger.info("create_user_account_update_requests")

    instructor = users_factories.AdminFactory.create(firstName="Support", lastName="Jeune")
    users_factories.UserAccountUpdateRequestFactory.create()

    accepted_request = users_factories.FirstNameUpdateRequestFactory.create(
        status=dms_models.GraphQLApplicationStates.accepted,
        firstName="Nouveau-Prénom",
        lastName="Accepté",
        newFirstName="Nouveau-Prénom",
        lastInstructor=instructor,
    )
    history_factories.ActionHistoryFactory.create(
        actionType=history_models.ActionType.INFO_MODIFIED,
        actionDate=datetime.datetime.utcnow(),
        user=accepted_request.user,
        authorUser=instructor,
        comment=None,
        extraData={
            "modified_info": {
                "firstName": {"old_info": "Ancien-Prénom", "new_info": "Nouveau-Prénom"},
            }
        },
    )

    email_accepted_request = users_factories.EmailUpdateRequestFactory.create(
        status=dms_models.GraphQLApplicationStates.accepted,
        lastName="A changé d'Email",
        newEmail=factory.SelfAttribute("email"),
        lastInstructor=instructor,
    )
    users_factories.EmailAdminUpdateEntryFactory.create(
        user=email_accepted_request.user,
        oldUserEmail=email_accepted_request.oldEmail.split("@")[0],
        oldDomainEmail=email_accepted_request.oldEmail.split("@")[1],
        newUserEmail=email_accepted_request.user.email.split("@")[0],
        newDomainEmail=email_accepted_request.user.email.split("@")[1],
    )

    users_factories.FirstNameUpdateRequestFactory.create(
        status=dms_models.GraphQLApplicationStates.draft,
        user__firstName="Jeune",
        firstName="Vieux",
        lastName="Changeant de Prénom",
        email="change_prenom@example.com",
        newFirstName="Vieux",
        lastInstructor=instructor,
        dateLastInstructorMessage=None,
    )

    users_factories.UserAccountUpdateRequestFactory.create(
        status=dms_models.GraphQLApplicationStates.draft,
        lastName="Changeant de Nom et Email",
        email="nouveau@example.com",
        updateTypes=[
            users_models.UserAccountUpdateType.EMAIL,
            users_models.UserAccountUpdateType.LAST_NAME,
        ],
        oldEmail="change_nom@example.com",
        newEmail="nouveau@example.com",
        newLastName="Nouveau",
        lastInstructor=instructor,
        dateLastUserMessage=None,
    )

    users_factories.PhoneNumberUpdateRequestFactory.create(
        lastName="Changeant de Numéro",
        email="change_telephone@example.com",
        user__phoneNumber="+33799886677",
        newPhoneNumber="+33799887766",
        lastInstructor=instructor,
    )

    users_factories.LastNameUpdateRequestFactory.create(
        status=dms_models.GraphQLApplicationStates.draft,
        lastName="Changeant de Nom",
        email="inconnu@example.com",
        user=None,
        newFirstName="Nouveau",
        lastInstructor=instructor,
        flags=[users_models.UserAccountUpdateFlag.CORRECTION_RESOLVED],
    )

    users_factories.FirstNameUpdateRequestFactory.create(
        status=dms_models.GraphQLApplicationStates.refused,
        lastName="Refusé",
        newFirstName="Pseudo",
        lastInstructor=instructor,
    )

    duplicate = users_factories.UserFactory.create(
        firstName="Jeune",
        lastName="Doublon",
        email="bene_18_bis@example.com",
    )

    users_factories.EmailUpdateRequestFactory.create(
        lastName="Doublon",
        email=duplicate.email,
        user=find_user_by_email("bene_18@example.com"),
        oldEmail="bene_18@example.com",
        newEmail=duplicate.email,
        lastInstructor=instructor,
        dateLastUserMessage=None,
        flags=[users_models.UserAccountUpdateFlag.DUPLICATE_NEW_EMAIL],
    )

    users_factories.PhoneNumberUpdateRequestFactory.create(
        status=dms_models.GraphQLApplicationStates.draft,
        lastName="Erreur",
        email="erreur@example.com",
        newPhoneNumber="0700000000",
        lastInstructor=instructor,
        dateLastUserMessage=None,
        flags=[
            users_models.UserAccountUpdateFlag.INVALID_VALUE,
            users_models.UserAccountUpdateFlag.WAITING_FOR_CORRECTION,
        ],
    )

    logger.info("created user account update requests")
