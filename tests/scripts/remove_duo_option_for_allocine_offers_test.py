import pytest
from tests.model_creators.generic_creators import create_offerer, create_venue
from tests.model_creators.specific_creators import create_offer_with_event_product, create_offer_with_thing_product

from models import OfferSQLEntity
from repository import repository
from repository.provider_queries import get_provider_by_local_class
from scripts.remove_duo_option_for_allocine_offers import remove_duo_option_for_allocine_offers


class RemoveDuoOptionForAllocineOffersTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_set_duo_option_as_false_only_for_allocine_offers(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)

        allocine_provider = get_provider_by_local_class('AllocineStocks')
        allocine_offer_1 = create_offer_with_thing_product(venue, idx=1,
                                                           last_provider_id=allocine_provider.id,
                                                           id_at_providers='offer1', last_provider=allocine_provider)
        allocine_offer_2 = create_offer_with_event_product(venue, idx=2,
                                                           last_provider_id=allocine_provider.id,
                                                           id_at_providers='offer2', last_provider=allocine_provider)

        other_offer = create_offer_with_thing_product(venue, idx=3)

        allocine_offer_1.isDuo = True
        allocine_offer_2.isDuo = True
        other_offer.isDuo = True

        repository.save(allocine_offer_1, allocine_offer_2, other_offer)

        # When
        remove_duo_option_for_allocine_offers()

        # Then
        OfferSQLEntity.query.all()

        assert OfferSQLEntity.query.get(1).isDuo is False
        assert OfferSQLEntity.query.get(2).isDuo is False
        assert OfferSQLEntity.query.get(3).isDuo is True
