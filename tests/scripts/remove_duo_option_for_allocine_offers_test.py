from models import Offer
from repository import repository
from repository.provider_queries import get_provider_by_local_class
from scripts.remove_duo_option_for_allocine_offers import remove_duo_option_for_allocine_offers
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue
from tests.model_creators.specific_creators import create_offer_with_thing_product, create_offer_with_event_product


class RemoveDuoOptionForAllocineOffersTest:
    @clean_database
    def test_should_set_duo_option_as_false_only_for_allocine_offers(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)

        allocine_provider = get_provider_by_local_class('AllocineStocks')
        allocine_offer_1 = create_offer_with_thing_product(venue, last_provider_id=allocine_provider.id, id_at_providers='offer1')
        allocine_offer_2 = create_offer_with_event_product(venue, last_provider_id=allocine_provider.id, id_at_providers='offer2')

        other_offer = create_offer_with_thing_product(venue, idx=999)

        allocine_offer_1.isDuo = True
        allocine_offer_2.isDuo = True
        other_offer.isDuo = True

        repository.save(allocine_offer_1, allocine_offer_2, other_offer)

        # When
        remove_duo_option_for_allocine_offers()

        # Then
        offers = Offer.query.all()

        assert offers[0].id == 999 and offers[0].isDuo
        assert not offers[1].isDuo
        assert not offers[2].isDuo
