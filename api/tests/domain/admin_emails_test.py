from unittest.mock import MagicMock

import pytest

from pcapi.connectors import sirene
import pcapi.core.mails.testing as mails_testing
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories
from pcapi.domain.admin_emails import maybe_send_offerer_validation_email
from pcapi.domain.admin_emails import send_suspended_fraudulent_users_email


@pytest.mark.usefixtures("db_session")
def test_maybe_send_offerer_validation_email_sends_email_to_pass_culture_when_objects_to_validate():
    # Given
    response_return_value = MagicMock(status_code=200, text="")
    response_return_value.json = MagicMock(
        return_value={
            "unite_legale": {"etablissement_siege": {"siret": ""}, "etablissements": [], "activite_principale": ""}
        }
    )
    user = users_factories.UserFactory()
    offerer = offerers_factories.NotValidatedOffererFactory()
    user_offerer = offerers_factories.UserOffererFactory(offerer=offerer, user=user)
    siren_info = sirene.SirenInfo(
        siren="123456789",
        name="whatever",
        head_office_siret="12345678900001",
        ape_code="16.64Z",
        legal_category_code="???",
        address=None,
    )

    # When
    maybe_send_offerer_validation_email(offerer, user_offerer, siren_info)

    # Then
    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["To"] == "administration@example.com"


@pytest.mark.usefixtures("db_session")
def test_maybe_send_offerer_validation_email_does_not_send_email_if_all_validated(app):
    # Given
    user = users_factories.UserFactory()
    offerer = offerers_factories.OffererFactory()
    user_offerer = offerers_factories.UserOffererFactory(offerer=offerer, user=user)
    siren_info = sirene.SirenInfo(
        siren="123456789",
        name="whatever",
        head_office_siret="12345678900001",
        ape_code="16.64Z",
        legal_category_code="???",
        address=None,
    )

    # When
    maybe_send_offerer_validation_email(offerer, user_offerer, siren_info)

    # Then
    assert not mails_testing.outbox


@override_features(TEMP_DISABLE_OFFERER_VALIDATION_EMAIL=True)
@pytest.mark.usefixtures("db_session")
def test_maybe_send_offerer_validation_email_disabled(app):
    # Given
    user = users_factories.UserFactory()
    offerer = offerers_factories.NotValidatedOffererFactory()
    user_offerer = offerers_factories.NotValidatedUserOffererFactory(offerer=offerer, user=user)
    siren_info = sirene.SirenInfo(
        siren="123456789",
        name="whatever",
        head_office_siret="12345678900001",
        ape_code="16.64Z",
        legal_category_code="???",
        address=None,
    )

    # When
    result = maybe_send_offerer_validation_email(offerer, user_offerer, siren_info)

    # Then
    assert result is True
    assert not mails_testing.outbox


@pytest.mark.usefixtures("db_session")
def test_send_suspended_fraudulent_users_email(app):
    admin = users_factories.UserFactory(email="admin@email.com")
    fraudulent_users = [users_factories.UserFactory()]
    nb_cancelled_bookings = 0

    send_suspended_fraudulent_users_email(fraudulent_users, nb_cancelled_bookings, admin.email)

    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["To"] == "admin@email.com"
    assert mails_testing.outbox[0].sent_data["subject"] == "Fraude : suspension des utilisateurs frauduleux par ids"
