from pcapi.core.finance import factories as finance_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories
from pcapi.sandboxes.scripts.utils.helpers import get_pro_user_helper


def create_pro_user_with_venue_bank_account_and_userofferer() -> dict:
    pro_user = users_factories.ProFactory()
    venue = offerers_factories.VenueFactory()

    finance_factories.BankAccountFactory(offerer=venue.managingOfferer)
    offerers_factories.UserOffererFactory(user=pro_user, offerer=venue.managingOfferer)
    return {"user": get_pro_user_helper(pro_user)}
