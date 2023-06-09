import datetime

import pytest

from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.pro.wake_up_after_inactivity_to_pro import send_wake_up_after_inactivity_to_pros
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.repository.repository import db


@pytest.mark.usefixtures("db_session")
class SendWakeUpEmailToOffererTest:
    fourty_days_ago = datetime.date.today() - datetime.timedelta(days=40)

    def test_send_send_mail_with_params_aggregated(self):
        user_offerer = offerers_factories.UserOffererFactory()

        expired_event_offer = offers_factories.EventOfferFactory(venue__managingOfferer=user_offerer.offerer)
        expired_event_stock = offers_factories.EventStockFactory(offer=expired_event_offer, quantity=0)
        expired_event_stock.dateModified = self.fourty_days_ago

        expired_product_offer = offers_factories.ThingOfferFactory(venue__managingOfferer=user_offerer.offerer)
        expired_product_stock = offers_factories.ThingStockFactory(offer=expired_product_offer, quantity=0)
        expired_product_stock.dateModified = self.fourty_days_ago

        db.session.add_all([expired_event_stock, expired_product_stock])

        send_wake_up_after_inactivity_to_pros()

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["To"] == user_offerer.user.email
        assert mails_testing.outbox[0].sent_data["params"] == {"CAN_EXPIRE": True, "IS_EVENT": True}
