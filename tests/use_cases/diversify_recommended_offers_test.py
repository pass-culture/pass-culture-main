from models import DiscoveryViewV3, ThingType
from use_cases.diversify_recommended_offers import order_offers_by_diversified_types


class OrderOffersByDiversifiedTypesTest:
    def test_should_return_ordered_offers_by_diversified_types(self):
        # given
        discovery_view_1 = DiscoveryViewV3()
        discovery_view_1.type = ThingType.LIVRE_EDITION

        discovery_view_2 = DiscoveryViewV3()
        discovery_view_2.type = ThingType.SPECTACLE_VIVANT_ABO

        discovery_view_3 = DiscoveryViewV3()
        discovery_view_3.type = ThingType.LIVRE_EDITION

        # when
        ordered_offers = order_offers_by_diversified_types([discovery_view_2, discovery_view_3, discovery_view_1])

        # then
        ordered_offers_types = [offer.type for offer in ordered_offers]
        assert ordered_offers_types == [ThingType.LIVRE_EDITION, ThingType.SPECTACLE_VIVANT_ABO, ThingType.LIVRE_EDITION]

    def test_should_return_ordered_offers_by_diversified_oneliness(self):
        # given
        discovery_view_1 = DiscoveryViewV3()
        discovery_view_1.type = ThingType.LIVRE_EDITION

        discovery_view_2 = DiscoveryViewV3()
        discovery_view_2.url = 'https:test.com'
        discovery_view_2.type = ThingType.LIVRE_EDITION

        discovery_view_3 = DiscoveryViewV3()
        discovery_view_3.type = ThingType.LIVRE_EDITION

        # when
        ordered_offers = order_offers_by_diversified_types([discovery_view_2, discovery_view_3, discovery_view_1])

        # then
        ordered_offers_url = [offer.url for offer in ordered_offers]
        assert ordered_offers_url == [None, 'https:test.com', None]
