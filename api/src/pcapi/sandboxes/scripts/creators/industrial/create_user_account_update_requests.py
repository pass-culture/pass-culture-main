import logging

from pcapi.connectors.dms import models as dms_models
from pcapi.core.users import factories as users_factories


logger = logging.getLogger(__name__)


def create_user_account_update_requests() -> None:
    logger.info("create_user_account_update_requests")
    instructor = users_factories.AdminFactory(firstName="Support", lastName="Jeune")
    users_factories.UserAccountUpdateRequestFactory()

    users_factories.UserAccountUpdateRequestFactory(
        lastName="Changeant de Prénom",
        email="change_prenom@example.com",
        newEmail=None,
        newFirstName="Vieux",
        lastInstructor=instructor,
        dateLastInstructorMessage=None,
    )
    users_factories.UserAccountUpdateRequestFactory(
        lastName="Changeant de Nom et Email",
        email="change_nom@example.com",
        newEmail="nouveau@example.com",
        newLastName="Nouveau",
        lastInstructor=instructor,
        dateLastUserMessage=None,
    )
    users_factories.UserAccountUpdateRequestFactory(
        status=dms_models.GraphQLApplicationStates.draft,
        lastName="Changeant de Numéro",
        email="change_telephone@example.com",
        user__phoneNumber="+33799886677",
        newEmail=None,
        newPhoneNumber="+33799887766",
        lastInstructor=instructor,
    )
    users_factories.UserAccountUpdateRequestFactory(
        status=dms_models.GraphQLApplicationStates.draft,
        lastName="Changeant de Prénom",
        email="inconnu@example.com",
        user=None,
        newEmail=None,
        newFirstName="Nouveau",
        lastInstructor=instructor,
    )
    logger.info("created user account update requests")
