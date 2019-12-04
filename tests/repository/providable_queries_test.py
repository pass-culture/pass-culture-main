from datetime import datetime

from models import Stock
from repository.providable_queries import get_last_update_for_provider


def test_get_last_update_for_provider_should_return_date_modified_at_last_provider_when_provided():
    # Given
    provider_id = 1
    modification_date = datetime(2019, 1, 1)
    pc_object = Stock()
    pc_object.lastProviderId = provider_id
    pc_object.dateModifiedAtLastProvider = modification_date

    # When
    date_modified_at_last_provider = get_last_update_for_provider(provider_id=provider_id, pc_obj=pc_object)

    # Then
    assert date_modified_at_last_provider == modification_date


def test_get_last_update_for_provider_should_return_none_when_last_provider_id_does_not_match_given_id():
    # Given
    provider_id = 1
    modification_date = datetime(2019, 1, 1)
    pc_object = Stock()
    pc_object.lastProviderId = 2
    pc_object.dateModifiedAtLastProvider = modification_date

    # When
    date_modified_at_last_provider = get_last_update_for_provider(provider_id=provider_id, pc_obj=pc_object)

    # Then
    assert date_modified_at_last_provider is None


def test_get_last_update_for_provider_should_return_none_when_last_provider_id_matches_given_id_and_date_modified_at_last_provider_is_none():
    # Given
    provider_id = 1
    pc_object = Stock()
    pc_object.lastProviderId = provider_id
    pc_object.dateModifiedAtLastProvider = None

    # When
    date_modified_at_last_provider = get_last_update_for_provider(provider_id=provider_id, pc_obj=pc_object)

    # Then
    assert date_modified_at_last_provider is None
