import datetime

import pytest

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import messages
from pcapi.core.users import factories as users_factories



class SubscriptionMessagesTest:
    def test_build_duplicate_error_message_duplicate_user_ine(self):
        # Duplicate user
        users_factories.UserFactory(ineHash="some_HASH", email="lucille.ellingson@example.com")

        user = users_factories.UserFactory()
        content = fraud_factories.EduconnectContentFactory(ine_hash="some_HASH")
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.EDUCONNECT, resultContent=content
        )

        expected_message = (
            "Ton dossier a été refusé car il y a déjà un compte bénéficiaire associé aux identifiants ÉduConnect que tu as fournis. "
            "Connecte-toi avec l’adresse mail luc***@example.com ou contacte le support si tu penses qu’il s’agit d’une erreur. "
            "Si tu n’as plus ton mot de passe, tu peux effectuer une demande de réinitialisation."
        )

        message = messages.build_duplicate_error_message(
            user, messages.fraud_models.FraudReasonCode.DUPLICATE_INE, content
        )

        assert message == expected_message

    def test_build_duplicate_error_message_duplicate_user_name_and_birth_date(self):
        # Duplicate user
        users_factories.BeneficiaryGrant18Factory(
            firstName="Lucille",
            lastName="Ellingson",
            email="lucille.ellingson@example.com",
            validatedBirthDate=datetime.date(year=2003, month=10, day=3),
        )

        user = users_factories.UserFactory()
        content = fraud_factories.UbbleContentFactory(
            birth_date="2003-10-03",
            first_name="Lucille",
            last_name="Ellingson",
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.UBBLE, resultContent=content
        )

        expected_message = (
            "Ton dossier a été refusé car il y a déjà un compte bénéficiaire à ton nom. "
            "Connecte-toi avec l’adresse mail luc***@example.com ou contacte le support si tu penses qu’il s’agit d’une erreur. "
            "Si tu n’as plus ton mot de passe, tu peux effectuer une demande de réinitialisation."
        )

        message = messages.build_duplicate_error_message(
            user, messages.fraud_models.FraudReasonCode.DUPLICATE_USER, content
        )

        assert message == expected_message

    def test_build_duplicate_error_message_duplicate_user_id_piece_number(self):
        # Duplicate user
        users_factories.BeneficiaryGrant18Factory(email="lucille.ellingson@example.com", idPieceNumber="123456789")

        user = users_factories.UserFactory()
        content = fraud_factories.DMSContentFactory(id_piece_number="123456789")
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, resultContent=content
        )

        expected_message = (
            "Ton dossier a été refusé car il y a déjà un compte bénéficiaire associé à ce numéro de pièce d’identité. "
            "Connecte-toi avec l’adresse mail luc***@example.com ou contacte le support si tu penses qu’il s’agit d’une erreur. "
            "Si tu n’as plus ton mot de passe, tu peux effectuer une demande de réinitialisation."
        )

        message = messages.build_duplicate_error_message(
            user, messages.fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER, content
        )

        assert message == expected_message

    def test_build_duplicate_error_message_duplicate_user_not_found(self):
        user = users_factories.UserFactory()
        content = fraud_factories.DMSContentFactory(id_piece_number="123456789")
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, resultContent=content
        )

        expected_message = (
            "Ton dossier a été refusé car il y a déjà un compte bénéficiaire associé à ce numéro de pièce d’identité. "
            "Contacte le support si tu penses qu’il s’agit d’une erreur. "
            "Si tu n’as plus ton mot de passe, tu peux effectuer une demande de réinitialisation."
        )

        message = messages.build_duplicate_error_message(
            user, messages.fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER, content
        )

        assert message == expected_message
