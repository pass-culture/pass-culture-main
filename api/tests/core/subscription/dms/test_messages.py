from datetime import datetime

import pytest

from pcapi.core.subscription import factories as subscription_factories
from pcapi.core.subscription import messages
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.subscription.dms import messages as dms_messages
from pcapi.core.subscription.dms import schemas as dms_schemas
from pcapi.core.users import factories as users_factories
from pcapi.utils.string import u_nbsp


class DmsMessagesTest:
    @pytest.mark.parametrize(
        "error_key, expected_error_message",
        [
            (
                dms_schemas.DmsFieldErrorKeyEnum.birth_date,
                "Il semblerait que ta date de naissance soit erronée. Tu peux te rendre sur le site demarche.numerique.gouv.fr pour la rectifier.",
            ),
            (
                dms_schemas.DmsFieldErrorKeyEnum.first_name,
                "Il semblerait que ton prénom soit erroné. Tu peux te rendre sur le site demarche.numerique.gouv.fr pour le rectifier.",
            ),
            (
                dms_schemas.DmsFieldErrorKeyEnum.id_piece_number,
                "Il semblerait que ton numéro de pièce d'identité soit erroné. Tu peux te rendre sur le site demarche.numerique.gouv.fr pour le rectifier.",
            ),
            (
                dms_schemas.DmsFieldErrorKeyEnum.last_name,
                "Il semblerait que ton nom de famille soit erroné. Tu peux te rendre sur le site demarche.numerique.gouv.fr pour le rectifier.",
            ),
            (
                dms_schemas.DmsFieldErrorKeyEnum.postal_code,
                "Il semblerait que ton code postal soit erroné. Tu peux te rendre sur le site demarche.numerique.gouv.fr pour le rectifier.",
            ),
        ],
    )
    def test_get_error_updatable_message(self, error_key, expected_error_message):
        errors = [dms_schemas.DmsFieldErrorDetails(key=error_key, value="¯\\_(ツ)_/¯")]
        application_content = subscription_factories.DMSContentFactory(field_errors=errors)

        expected_message = subscription_schemas.SubscriptionMessage(
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
            dms_schemas.DmsFieldErrorDetails(key=dms_schemas.DmsFieldErrorKeyEnum.birth_date, value="¯\\_(ツ)_/¯"),
            dms_schemas.DmsFieldErrorDetails(key=dms_schemas.DmsFieldErrorKeyEnum.first_name, value="¯\\_(ツ)_/¯"),
        ]
        application_content = subscription_factories.DMSContentFactory(field_errors=errors)
        expected_error_message = "Il semblerait que tes date de naissance et prénom soient erronés. Tu peux te rendre sur le site demarche.numerique.gouv.fr pour les rectifier."
        expected_message = subscription_schemas.SubscriptionMessage(
            user_message=expected_error_message,
            call_to_action=messages.REDIRECT_TO_DMS_CALL_TO_ACTION,
            pop_over_icon=None,
            updated_at=datetime(2021, 1, 1),
        )

        message = dms_messages.get_error_updatable_message(
            application_content=application_content, birth_date_error=None, updated_at=datetime(2021, 1, 1)
        )

        assert message == expected_message

    @pytest.mark.usefixtures("db_session")
    @pytest.mark.parametrize(
        "error_key, expected_error_message",
        [
            (
                dms_schemas.DmsFieldErrorKeyEnum.birth_date,
                "le format de la date de naissance renseignée est invalide.",
            ),
            (
                dms_schemas.DmsFieldErrorKeyEnum.first_name,
                "le format du prénom renseigné est invalide.",
            ),
            (
                dms_schemas.DmsFieldErrorKeyEnum.id_piece_number,
                "le format du numéro de pièce d'identité renseigné est invalide.",
            ),
            (
                dms_schemas.DmsFieldErrorKeyEnum.last_name,
                "le format du nom de famille renseigné est invalide.",
            ),
            (
                dms_schemas.DmsFieldErrorKeyEnum.postal_code,
                "le format du code postal renseigné est invalide.",
            ),
        ],
    )
    def test_get_error_processed_message(self, error_key, expected_error_message):
        user = users_factories.UserFactory()
        errors = [
            dms_schemas.DmsFieldErrorDetails(key=error_key, value="¯\\_(ツ)_/¯"),
        ]
        application_content = subscription_factories.DMSContentFactory(field_errors=errors)
        expected_message = subscription_schemas.SubscriptionMessage(
            user_message=f"Ton dossier déposé sur le site demarche.numerique.gouv.fr a été refusé{u_nbsp}: {expected_error_message} Tu peux contacter le support pour mettre à jour ton dossier.",
            call_to_action=subscription_schemas.CallToActionMessage(
                title="Contacter le support",
                link=messages.SUBSCRIPTION_SUPPORT_FORM_URL,
                icon=subscription_schemas.CallToActionIcon.EXTERNAL,
            ),
            pop_over_icon=None,
            updated_at=datetime(2021, 1, 1),
        )

        message = dms_messages.get_error_processed_message(
            user=user,
            reason_codes=[subscription_models.FraudReasonCode.ERROR_IN_DATA],
            application_content=application_content,
            birth_date_error=None,
            updated_at=datetime(2021, 1, 1),
        )

        assert message == expected_message

    @pytest.mark.usefixtures("db_session")
    def test_get_error_processed_message_with_multiple_errors(self):
        user = users_factories.UserFactory()
        errors = [
            dms_schemas.DmsFieldErrorDetails(key=dms_schemas.DmsFieldErrorKeyEnum.birth_date, value="¯\\_(ツ)_/¯"),
            dms_schemas.DmsFieldErrorDetails(key=dms_schemas.DmsFieldErrorKeyEnum.first_name, value="¯\\_(ツ)_/¯"),
        ]
        application_content = subscription_factories.DMSContentFactory(field_errors=errors)
        expected_message = subscription_schemas.SubscriptionMessage(
            user_message=f"Ton dossier déposé sur le site demarche.numerique.gouv.fr a été refusé{u_nbsp}: le format des date de naissance et prénom renseignés est invalide. Tu peux contacter le support pour mettre à jour ton dossier.",
            call_to_action=subscription_schemas.CallToActionMessage(
                title="Contacter le support",
                link=messages.SUBSCRIPTION_SUPPORT_FORM_URL,
                icon=subscription_schemas.CallToActionIcon.EXTERNAL,
            ),
            pop_over_icon=None,
            updated_at=datetime(2021, 1, 1),
        )

        message = dms_messages.get_error_processed_message(
            user=user,
            reason_codes=[subscription_models.FraudReasonCode.ERROR_IN_DATA],
            application_content=application_content,
            birth_date_error=None,
            updated_at=datetime(2021, 1, 1),
        )

        assert message == expected_message

    @pytest.mark.usefixtures("db_session")
    def test_get_error_processed_message_with_id_piece_number_errors(self):
        user = users_factories.UserFactory()
        application_content = subscription_factories.DMSContentFactory()
        expected_message = subscription_schemas.SubscriptionMessage(
            user_message=f"Ton dossier déposé sur le site demarche.numerique.gouv.fr a été refusé{u_nbsp}: le format du numéro de pièce d'identité renseigné est invalide. Tu peux contacter le support pour plus d'informations.",
            call_to_action=subscription_schemas.CallToActionMessage(
                title="Contacter le support",
                link=messages.SUBSCRIPTION_SUPPORT_FORM_URL,
                icon=subscription_schemas.CallToActionIcon.EXTERNAL,
            ),
            pop_over_icon=None,
            updated_at=datetime(2021, 1, 1),
        )

        message = dms_messages.get_error_processed_message(
            user=user,
            reason_codes=[subscription_models.FraudReasonCode.INVALID_ID_PIECE_NUMBER],
            application_content=application_content,
            birth_date_error=None,
            updated_at=datetime(2021, 1, 1),
        )

        assert message == expected_message

    @pytest.mark.usefixtures("db_session")
    @pytest.mark.parametrize(
        "error_key, expected_error_message",
        [
            (
                dms_schemas.DmsFieldErrorKeyEnum.birth_date,
                "Il semblerait que ta date de naissance soit erronée.",
            ),
            (
                dms_schemas.DmsFieldErrorKeyEnum.first_name,
                "Il semblerait que ton prénom soit erroné.",
            ),
            (
                dms_schemas.DmsFieldErrorKeyEnum.id_piece_number,
                "Il semblerait que ton numéro de pièce d'identité soit erroné.",
            ),
            (
                dms_schemas.DmsFieldErrorKeyEnum.last_name,
                "Il semblerait que ton nom de famille soit erroné.",
            ),
            (
                dms_schemas.DmsFieldErrorKeyEnum.postal_code,
                "Il semblerait que ton code postal soit erroné.",
            ),
        ],
    )
    def test_get_error_not_updatable_message(self, error_key, expected_error_message):
        user = users_factories.UserFactory()
        errors = [
            dms_schemas.DmsFieldErrorDetails(key=error_key, value="¯\\_(ツ)_/¯"),
        ]
        application_content = subscription_factories.DMSContentFactory(field_errors=errors)
        expected_message = subscription_schemas.SubscriptionMessage(
            user_message=f"{expected_error_message} Tu peux contacter le support pour plus d’informations.",
            call_to_action=subscription_schemas.CallToActionMessage(
                title="Contacter le support",
                link=messages.SUBSCRIPTION_SUPPORT_FORM_URL,
                icon=subscription_schemas.CallToActionIcon.EXTERNAL,
            ),
            pop_over_icon=None,
            updated_at=datetime(2021, 1, 1),
        )

        message = dms_messages.get_error_not_updatable_message(
            user=user,
            reason_codes=[subscription_models.FraudReasonCode.ERROR_IN_DATA],
            application_content=application_content,
            birth_date_error=None,
            updated_at=datetime(2021, 1, 1),
        )

        assert message == expected_message
