from datetime import datetime

import pytest

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import messages
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.dms import messages as dms_messages
from pcapi.core.users import factories as users_factories
from pcapi.utils.string import u_nbsp


class DmsMessagesTest:
    @pytest.mark.parametrize(
        "error_key, expected_error_message",
        [
            (
                fraud_models.DmsFieldErrorKeyEnum.birth_date,
                "Il semblerait que ta date de naissance soit erronée. Tu peux te rendre sur le site demarches-simplifiees.fr pour la rectifier.",
            ),
            (
                fraud_models.DmsFieldErrorKeyEnum.first_name,
                "Il semblerait que ton prénom soit erroné. Tu peux te rendre sur le site demarches-simplifiees.fr pour le rectifier.",
            ),
            (
                fraud_models.DmsFieldErrorKeyEnum.id_piece_number,
                "Il semblerait que ton numéro de pièce d'identité soit erroné. Tu peux te rendre sur le site demarches-simplifiees.fr pour le rectifier.",
            ),
            (
                fraud_models.DmsFieldErrorKeyEnum.last_name,
                "Il semblerait que ton nom de famille soit erroné. Tu peux te rendre sur le site demarches-simplifiees.fr pour le rectifier.",
            ),
            (
                fraud_models.DmsFieldErrorKeyEnum.postal_code,
                "Il semblerait que ton code postal soit erroné. Tu peux te rendre sur le site demarches-simplifiees.fr pour le rectifier.",
            ),
        ],
    )
    def test_get_error_updatable_message(self, error_key, expected_error_message):
        errors = [fraud_models.DmsFieldErrorDetails(key=error_key, value="¯\\_(ツ)_/¯")]
        application_content = fraud_factories.DMSContentFactory(field_errors=errors)

        expected_message = subscription_models.SubscriptionMessage(
            user_message=expected_error_message,
            call_to_action=messages.REDIRECT_TO_DMS_CALL_TO_ACTION,
            pop_over_icon=None,
            updated_at=datetime(2021, 1, 1),
        )

        message = dms_messages.get_error_updatable_message(
            application_content=application_content, birth_date_error=None, updated_at=datetime(2021, 1, 1)
        )

        assert message == expected_message

    def test_get_error_updatable_message_with_multiple_errors(self):
        errors = [
            fraud_models.DmsFieldErrorDetails(key=fraud_models.DmsFieldErrorKeyEnum.birth_date, value="¯\\_(ツ)_/¯"),
            fraud_models.DmsFieldErrorDetails(key=fraud_models.DmsFieldErrorKeyEnum.first_name, value="¯\\_(ツ)_/¯"),
        ]
        application_content = fraud_factories.DMSContentFactory(field_errors=errors)
        expected_error_message = "Il semblerait que tes date de naissance et prénom soient erronés. Tu peux te rendre sur le site demarches-simplifiees.fr pour les rectifier."
        expected_message = subscription_models.SubscriptionMessage(
            user_message=expected_error_message,
            call_to_action=messages.REDIRECT_TO_DMS_CALL_TO_ACTION,
            pop_over_icon=None,
            updated_at=datetime(2021, 1, 1),
        )

        message = dms_messages.get_error_updatable_message(
            application_content=application_content, birth_date_error=None, updated_at=datetime(2021, 1, 1)
        )

        assert message == expected_message


    @pytest.mark.parametrize(
        "error_key, expected_error_message",
        [
            (
                fraud_models.DmsFieldErrorKeyEnum.birth_date,
                "le format de la date de naissance renseignée est invalide.",
            ),
            (
                fraud_models.DmsFieldErrorKeyEnum.first_name,
                "le format du prénom renseigné est invalide.",
            ),
            (
                fraud_models.DmsFieldErrorKeyEnum.id_piece_number,
                "le format du numéro de pièce d'identité renseigné est invalide.",
            ),
            (
                fraud_models.DmsFieldErrorKeyEnum.last_name,
                "le format du nom de famille renseigné est invalide.",
            ),
            (
                fraud_models.DmsFieldErrorKeyEnum.postal_code,
                "le format du code postal renseigné est invalide.",
            ),
        ],
    )
    def test_get_error_processed_message(self, error_key, expected_error_message):
        user = users_factories.UserFactory()
        errors = [
            fraud_models.DmsFieldErrorDetails(key=error_key, value="¯\\_(ツ)_/¯"),
        ]
        application_content = fraud_factories.DMSContentFactory(field_errors=errors)
        expected_message = subscription_models.SubscriptionMessage(
            user_message=f"Ton dossier déposé sur le site demarches-simplifiees.fr a été refusé{u_nbsp}: {expected_error_message} Tu peux contacter le support pour mettre à jour ton dossier.",
            call_to_action=subscription_models.CallToActionMessage(
                title="Contacter le support",
                link=f"{messages.MAILTO_SUPPORT}{messages.MAILTO_SUPPORT_PARAMS.format(id=user.id)}",
                icon=subscription_models.CallToActionIcon.EMAIL,
            ),
            pop_over_icon=None,
            updated_at=datetime(2021, 1, 1),
        )

        message = dms_messages.get_error_processed_message(
            user=user,
            reason_codes=[fraud_models.FraudReasonCode.ERROR_IN_DATA],
            application_content=application_content,
            birth_date_error=None,
            updated_at=datetime(2021, 1, 1),
        )

        assert message == expected_message


    def test_get_error_processed_message_with_multiple_errors(self):
        user = users_factories.UserFactory()
        errors = [
            fraud_models.DmsFieldErrorDetails(key=fraud_models.DmsFieldErrorKeyEnum.birth_date, value="¯\\_(ツ)_/¯"),
            fraud_models.DmsFieldErrorDetails(key=fraud_models.DmsFieldErrorKeyEnum.first_name, value="¯\\_(ツ)_/¯"),
        ]
        application_content = fraud_factories.DMSContentFactory(field_errors=errors)
        expected_message = subscription_models.SubscriptionMessage(
            user_message=f"Ton dossier déposé sur le site demarches-simplifiees.fr a été refusé{u_nbsp}: le format des date de naissance et prénom renseignés est invalide. Tu peux contacter le support pour mettre à jour ton dossier.",
            call_to_action=subscription_models.CallToActionMessage(
                title="Contacter le support",
                link=f"{messages.MAILTO_SUPPORT}{messages.MAILTO_SUPPORT_PARAMS.format(id=user.id)}",
                icon=subscription_models.CallToActionIcon.EMAIL,
            ),
            pop_over_icon=None,
            updated_at=datetime(2021, 1, 1),
        )

        message = dms_messages.get_error_processed_message(
            user=user,
            reason_codes=[fraud_models.FraudReasonCode.ERROR_IN_DATA],
            application_content=application_content,
            birth_date_error=None,
            updated_at=datetime(2021, 1, 1),
        )

        assert message == expected_message


    def test_get_error_processed_message_with_id_piece_number_errors(self):
        user = users_factories.UserFactory()
        application_content = fraud_factories.DMSContentFactory()
        expected_message = subscription_models.SubscriptionMessage(
            user_message=f"Ton dossier déposé sur le site demarches-simplifiees.fr a été refusé{u_nbsp}: le format du numéro de pièce d'identité renseigné est invalide. Tu peux contacter le support pour plus d'informations.",
            call_to_action=subscription_models.CallToActionMessage(
                title="Contacter le support",
                link=f"{messages.MAILTO_SUPPORT}{messages.MAILTO_SUPPORT_PARAMS.format(id=user.id)}",
                icon=subscription_models.CallToActionIcon.EMAIL,
            ),
            pop_over_icon=None,
            updated_at=datetime(2021, 1, 1),
        )

        message = dms_messages.get_error_processed_message(
            user=user,
            reason_codes=[fraud_models.FraudReasonCode.INVALID_ID_PIECE_NUMBER],
            application_content=application_content,
            birth_date_error=None,
            updated_at=datetime(2021, 1, 1),
        )

        assert message == expected_message


    @pytest.mark.parametrize(
        "error_key, expected_error_message",
        [
            (
                fraud_models.DmsFieldErrorKeyEnum.birth_date,
                "Il semblerait que ta date de naissance soit erronée.",
            ),
            (
                fraud_models.DmsFieldErrorKeyEnum.first_name,
                "Il semblerait que ton prénom soit erroné.",
            ),
            (
                fraud_models.DmsFieldErrorKeyEnum.id_piece_number,
                "Il semblerait que ton numéro de pièce d'identité soit erroné.",
            ),
            (
                fraud_models.DmsFieldErrorKeyEnum.last_name,
                "Il semblerait que ton nom de famille soit erroné.",
            ),
            (
                fraud_models.DmsFieldErrorKeyEnum.postal_code,
                "Il semblerait que ton code postal soit erroné.",
            ),
        ],
    )
    def test_get_error_not_updatable_message(self, error_key, expected_error_message):
        user = users_factories.UserFactory()
        errors = [
            fraud_models.DmsFieldErrorDetails(key=error_key, value="¯\\_(ツ)_/¯"),
        ]
        application_content = fraud_factories.DMSContentFactory(field_errors=errors)
        expected_message = subscription_models.SubscriptionMessage(
            user_message=f"{expected_error_message} Tu peux contacter le support pour plus d’informations.",
            call_to_action=subscription_models.CallToActionMessage(
                title="Contacter le support",
                link=f"{messages.MAILTO_SUPPORT}{messages.MAILTO_SUPPORT_PARAMS.format(id=user.id)}",
                icon=subscription_models.CallToActionIcon.EMAIL,
            ),
            pop_over_icon=None,
            updated_at=datetime(2021, 1, 1),
        )

        message = dms_messages.get_error_not_updatable_message(
            user=user,
            reason_codes=[fraud_models.FraudReasonCode.ERROR_IN_DATA],
            application_content=application_content,
            birth_date_error=None,
            updated_at=datetime(2021, 1, 1),
        )

        assert message == expected_message
