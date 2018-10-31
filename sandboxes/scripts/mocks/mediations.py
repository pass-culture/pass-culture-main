from sandboxes.scripts.mocks.offers import ALL_TYPED_EVENT_OFFER_MOCKS,\
                                           ALL_TYPED_THING_OFFER_MOCKS
from sandboxes.scripts.mocks import get_all_typed_event_stock_mocks,\
                                    get_all_typed_thing_stock_mocks

MEDIATION_MOCKS = []

ALL_TYPED_EVENT_MEDIATION_MOCKS = get_all_typed_event_stock_mocks(ALL_TYPED_EVENT_OFFER_MOCKS)
ALL_TYPED_THING_MEDIATION_MOCKS = get_all_typed_thing_stock_mocks(ALL_TYPED_THING_OFFER_MOCKS)
ALL_TYPED_MEDIATION_MOCKS = ALL_TYPED_EVENT_MEDIATION_MOCKS + ALL_TYPED_THING_MEDIATION_MOCKS
MEDIATION_MOCKS += ALL_TYPED_MEDIATION_MOCKS
