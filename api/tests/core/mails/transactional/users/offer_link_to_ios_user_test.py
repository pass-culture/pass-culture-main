import pytest

from pcapi import settings
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.offer_link_to_ios_user import get_offer_link_to_ios_user_email_data
from pcapi.core.mails.transactional.users.offer_link_to_ios_user import send_offer_link_to_ios_user_email
from pcapi.core.offers import factories
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories


@pytest.mark.usefixtures("db_session")
class MailjetEmailOfferLinkIosUserTest:
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    def test_get_email_correct_metadata(self):
        # Given
        user = users_factories.UserFactory.build(email="fabien+test@example.net", firstName="Fabien")
        offer = factories.ThingOfferFactory()

        # When
        data = get_offer_link_to_ios_user_email_data(user, offer)

        # Then
        assert data == {
            "MJ-TemplateID": 2826195,
            "MJ-TemplateLanguage": True,
            "Vars": {
                "offer_name": offer.name,
                "offer_webapp_link": f"{settings.WEBAPP_V2_REDIRECT_URL}/offre/{offer.id}",
                "user_first_name": user.firstName,
                "venue_name": offer.venue.name,
            },
        }

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    def test_send_correct_mail(self):
        # Given
        user = users_factories.UserFactory.build(email="fabien+test@example.net", firstName="Fabien")
        offer = factories.ThingOfferFactory()
        # When
        send_offer_link_to_ios_user_email(user, offer)

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data == {
            "FromEmail": "support@example.com",
            "MJ-TemplateID": 2826195,
            "MJ-TemplateLanguage": True,
            "To": "fabien+test@example.net",
            "Vars": {
                "env": "-development",
                "offer_name": offer.name,
                "offer_webapp_link": f"{settings.WEBAPP_V2_REDIRECT_URL}/offre/{offer.id}",
                "user_first_name": user.firstName,
                "venue_name": offer.venue.name,
            },
        }


@pytest.mark.usefixtures("db_session")
class SendinblueEmailOfferLinkIosUserTest:
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_get_email_correct_metadata(self):
        # Given
        user = users_factories.UserFactory.build(email="fabien+test@example.net", firstName="Fabien")
        offer = factories.ThingOfferFactory()
        # When
        data = get_offer_link_to_ios_user_email_data(user, offer)

        # Then
        assert data.template == TransactionalEmail.OFFER_WEBAPP_LINK_TO_IOS_USER.value
        assert data.params == {
            "FIRSTNAME": user.firstName,
            "OFFER_NAME": offer.name,
            "OFFER_WEBAPP_LINK": f"{settings.WEBAPP_V2_REDIRECT_URL}/offre/{offer.id}",
            "VENUE_NAME": offer.venue.name,
        }

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_send_correct_mail(self):
        # Given
        user = users_factories.UserFactory.build(email="fabien+test@example.net", firstName="Fabien")
        offer = factories.ThingOfferFactory()
        # When
        send_offer_link_to_ios_user_email(user, offer)

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.OFFER_WEBAPP_LINK_TO_IOS_USER.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == "fabien+test@example.net"
        assert mails_testing.outbox[0].sent_data["params"] == {
            "FIRSTNAME": user.firstName,
            "OFFER_NAME": offer.name,
            "OFFER_WEBAPP_LINK": f"{settings.WEBAPP_V2_REDIRECT_URL}/offre/{offer.id}",
            "VENUE_NAME": offer.venue.name,
        }
