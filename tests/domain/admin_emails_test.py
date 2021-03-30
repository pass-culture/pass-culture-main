from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

import pcapi.core.mails.testing as mails_testing
from pcapi.domain.admin_emails import maybe_send_offerer_validation_email
from pcapi.domain.admin_emails import send_offer_creation_notification_to_administration
from pcapi.domain.admin_emails import send_payment_details_email
from pcapi.domain.admin_emails import send_payments_report_emails
from pcapi.domain.admin_emails import send_wallet_balances_email
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product


@patch("pcapi.connectors.api_entreprises.requests.get")
def test_maybe_send_offerer_validation_email_sends_email_to_pass_culture_when_objects_to_validate(
    mock_api_entreprise, app
):
    # Given
    response_return_value = MagicMock(status_code=200, text="")
    response_return_value.json = MagicMock(
        return_value={
            "unite_legale": {"etablissement_siege": {"siret": ""}, "etablissements": [], "activite_principale": ""}
        }
    )
    mock_api_entreprise.return_value = response_return_value

    offerer = create_offerer(validation_token="12345")
    user = create_user(validation_token="98765")
    user_offerer = create_user_offerer(user, offerer)

    # When
    maybe_send_offerer_validation_email(offerer, user_offerer)

    # Then
    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["To"] == "administration@example.com"


def test_maybe_send_offerer_validation_email_does_not_send_email_if_all_validated(app):
    # Given
    offerer = create_offerer(
        siren="732075312",
        address="122 AVENUE DE FRANCE",
        city="Paris",
        postal_code="75013",
        name="Accenture",
        validation_token=None,
    )

    user = create_user(
        is_beneficiary=False,
        departement_code="75",
        email="user@accenture.com",
        public_name="Test",
        validation_token=None,
    )

    user_offerer = create_user_offerer(user, offerer, validation_token=None)

    # When
    maybe_send_offerer_validation_email(offerer, user_offerer)

    # Then
    assert not mails_testing.outbox


def test_send_payment_details_email_sends_email_to_pass_culture(app):
    # Given
    csv = '"header A","header B","header C","header D"\n"part A","part B","part C","part D"\n'
    recipients = ["comptable1@culture.fr", "comptable2@culture.fr"]

    # When
    send_payment_details_email(csv, recipients)

    # Then
    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["To"] == "comptable1@culture.fr, comptable2@culture.fr"


def test_send_wallet_balances_email_sends_email_to_recipients(app):
    # Given
    csv = '"header A","header B","header C","header D"\n"part A","part B","part C","part D"\n'
    recipients = ["comptable1@culture.fr", "comptable2@culture.fr"]

    mocked_send_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_email.return_value = return_value

    # When
    send_wallet_balances_email(csv, recipients)

    # Then
    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["To"] == "comptable1@culture.fr, comptable2@culture.fr"


def test_send_payments_report_email_ssends_email_to_recipients(app):
    # Given
    not_processable_csv = '"header A","header B","header C","header D"\n"part A","part B","part C","part D"\n'
    error_csv = '"header 1","header 2","header 3","header 4"\n"part 1","part 2","part 3","part 4"\n'
    grouped_payments = {"ERROR": [Mock(), Mock()], "SENT": [Mock()], "PENDING": [Mock(), Mock(), Mock()]}

    # When
    send_payments_report_emails(not_processable_csv, error_csv, grouped_payments, ["recipient@example.com"])

    # Then
    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["To"] == "recipient@example.com"


class SendOfferCreationNotificationToAdministrationTest:
    def test_when_mailjet_status_code_200_sends_email_to_administration_email(self, app):
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        author = create_user(email="author@email.com")

        # When
        send_offer_creation_notification_to_administration(offer, author)

        # Then
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["To"] == "administration@example.com"
