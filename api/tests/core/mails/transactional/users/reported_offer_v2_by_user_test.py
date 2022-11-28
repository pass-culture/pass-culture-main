import pytest

from pcapi.core.mails.transactional.users.reported_offer_by_user import get_reported_offer_email_data
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.models import Reason
from pcapi.core.testing import override_features
from pcapi.core.users.factories import BeneficiaryGrant18Factory
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


class ReportedOfferByUserEmailTest:
    @override_features(OFFER_FORM_V3=False)
    def test_get_email_metadata(self):

        # Given
        user = BeneficiaryGrant18Factory()
        offer = OfferFactory()
        reason = Reason.INAPPROPRIATE.value

        # when
        email_data = get_reported_offer_email_data(user, offer, reason)

        # Then
        assert email_data.params == {
            "USER_ID": user.id,
            "OFFER_ID": offer.id,
            "OFFER_NAME": offer.name,
            "REASON": "Le contenu est inapproprié",
            "OFFER_URL": "http://localhost:3001/offre/" + f"{humanize(offer.id)}/individuel/edition",
        }
