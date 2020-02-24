from decimal import Decimal

from local_providers import AllocineStocks, LibrairesStocks, TiteLiveStocks
from models import AllocineVenueProvider, VenueProvider, VenueProviderPriceRule
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue
from tests.model_creators.provider_creators import activate_provider
from use_cases.connect_provider_to_venue import connect_provider_to_venue
from utils.human_ids import humanize


class UseCaseTest:
    class ConnectProviderToVenueTest:
        class WhenProviderIsAllocine:
            @clean_database
            def test_should_connect_venue_to_allocine_provider(self, app):
                #Given
                offerer = create_offerer()
                venue = create_venue(offerer)
                provider = activate_provider('AllocineStocks')

                repository.save(venue)

                provider_type = AllocineStocks

                venue_provider_payload = {
                    'providerId': humanize(provider.id),
                    'venueId': humanize(venue.id),
                    'price': '9.99',
                    'isDuo': True,
                    'available': 50
                }

                #When
                connect_provider_to_venue(provider_type, venue_provider_payload)

                #Then
                allocine_venue_provider = AllocineVenueProvider.query.one()
                venue_provider_price_rule = VenueProviderPriceRule.query.one()

                assert allocine_venue_provider.venue == venue
                assert allocine_venue_provider.isDuo
                assert allocine_venue_provider.available == 50
                assert venue_provider_price_rule.price == Decimal('9.99')


        class WhenProviderIsLibraires:
            @clean_database
            def test_should_connect_venue_to_libraires_provider(self, app):
                #Given
                offerer = create_offerer()
                venue = create_venue(offerer)
                provider = activate_provider('LibrairesStocks')

                repository.save(venue)

                provider_type = LibrairesStocks

                venue_provider_payload = {
                    'providerId': humanize(provider.id),
                    'venueId': humanize(venue.id),
                }

                #When
                connect_provider_to_venue(provider_type, venue_provider_payload)

                #Then
                libraires_venue_provider = VenueProvider.query.one()
                assert libraires_venue_provider.venue == venue


        class WhenProviderIsTiteLive:
            @clean_database
            def test_should_connect_venue_to_titelive_provider(self, app):
                #Given
                offerer = create_offerer()
                venue = create_venue(offerer)
                provider = activate_provider('TiteLiveStocks')

                repository.save(venue)

                provider_type = TiteLiveStocks

                venue_provider_payload = {
                    'providerId': humanize(provider.id),
                    'venueId': humanize(venue.id),
                }

                #When
                connect_provider_to_venue(provider_type, venue_provider_payload)

                #Then
                titelive_venue_provider = VenueProvider.query.one()
                assert titelive_venue_provider.venue == venue