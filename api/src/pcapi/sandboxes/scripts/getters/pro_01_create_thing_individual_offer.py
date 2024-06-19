from flask import jsonify

from pcapi.core.finance import factories as finance_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories
from pcapi.serialization.decorator import spectree_serialize


def setup_data_for_create_thing_individual_offer_e2e_test() -> dict:
    pro_user = users_factories.ProFactory()
    venue = offerers_factories.VenueFactory()

    finance_factories.BankAccountFactory(offerer=venue.managingOfferer)
    offerers_factories.UserOffererFactory(user=pro_user, offerer=venue.managingOfferer)
    return {"email": pro_user.email}
