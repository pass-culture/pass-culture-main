from unittest.mock import patch

import pytest

from models import OfferSQLEntity, ApiErrors
from repository import repository
from repository.provider_queries import get_provider_by_local_class
import pytest
from tests.model_creators.generic_creators import create_venue, create_offerer
from tests.model_creators.specific_creators import create_offer_with_thing_product
from use_cases.update_an_offer import update_an_offer


class UseCaseTest:
    class UpdateAnOfferTest:
        class WhenTheOfferIsFromAllocine:
            @pytest.mark.usefixtures("db_session")
            @patch('use_cases.update_an_offer.feature_queries.is_active', return_value=True)
            @patch('use_cases.update_an_offer.redis.add_offer_id')
            def test_keep_track_of_updated_fields_so_they_wont_be_overriden(self, mock_redis, mock_feature, app):
                # Given
                provider = get_provider_by_local_class('AllocineStocks')
                offerer = create_offerer()
                venue = create_venue(offerer)
                offer = create_offer_with_thing_product(venue, last_provider=provider)
                repository.save(offer)

                # When
                modifications = {'isDuo': 'true'}
                update_an_offer(offer, modifications)

                # Then
                offer = OfferSQLEntity.query.one()
                assert offer.fieldsUpdated == ['isDuo']

            @pytest.mark.usefixtures("db_session")
            @patch('use_cases.update_an_offer.feature_queries.is_active', return_value=True)
            @patch('use_cases.update_an_offer.redis.add_offer_id')
            def test_preserve_already_updated_fields_so_they_wont_be_overriden(self, mock_redis, mock_feature, app):
                # Given
                provider = get_provider_by_local_class('AllocineStocks')
                offerer = create_offerer()
                venue = create_venue(offerer)
                offer = create_offer_with_thing_product(venue, last_provider=provider)
                offer.fieldsUpdated = ['isActive']

                repository.save(offer)

                # When
                modifications = {'isDuo': 'true'}
                update_an_offer(offer, modifications)

                # Then
                offer = OfferSQLEntity.query.one()
                assert set(offer.fieldsUpdated) == set(['isDuo', 'isActive'])

            class WhenUpdatingForbiddenFields:
                @pytest.mark.usefixtures("db_session")
                @patch('use_cases.update_an_offer.feature_queries.is_active', return_value=True)
                @patch('use_cases.update_an_offer.redis.add_offer_id')
                def test_should_raise_an_error_when_field_has_changed(self, mock_redis, mock_feature, app):
                    # Given
                    provider = get_provider_by_local_class('AllocineStocks')
                    offerer = create_offerer()
                    venue = create_venue(offerer)
                    offer = create_offer_with_thing_product(venue, last_provider=provider)

                    repository.save(offer)

                    # When
                    modifications = {'bookingEmail': 'company@example.net'}

                    with pytest.raises(ApiErrors) as error:
                        update_an_offer(offer, modifications)

                    # Then
                    assert error.value.errors['bookingEmail'] == ['Vous ne pouvez pas modifier ce champ']

                @pytest.mark.usefixtures("db_session")
                @patch('use_cases.update_an_offer.feature_queries.is_active', return_value=True)
                @patch('use_cases.update_an_offer.redis.add_offer_id')
                def test_should_not_raise_an_error_when_field_has_not_changed(self, mock_redis, mock_feature, app):
                    # Given
                    booking_email = 'company@example.net'
                    provider = get_provider_by_local_class('AllocineStocks')
                    offerer = create_offerer()
                    venue = create_venue(offerer)
                    offer = create_offer_with_thing_product(venue, last_provider=provider, booking_email=booking_email)
                    repository.save(offer)

                    # When

                    modifications = {'bookingEmail': booking_email}

                    try:
                        update_an_offer(offer, modifications)
                    except:
                        assert False

        class WhenTheOfferIsFromAnotherProvider:
            @pytest.mark.usefixtures("db_session")
            def test_offer_should_not_be_updated(self, app):
                # Given
                provider = get_provider_by_local_class('LibrairesStocks')
                offerer = create_offerer()
                venue = create_venue(offerer)
                offer = create_offer_with_thing_product(venue, last_provider=provider)
                repository.save(offer)

                # When
                modifications = {'isDuo': 'true'}
                with pytest.raises(ApiErrors) as api_error:
                    update_an_offer(offer, modifications)

                # Then
                assert api_error.value.errors['global'] == ['Les offres importées ne sont pas modifiables']
