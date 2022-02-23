import pytest

from pcapi.core.offers.models import Stock
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.repository import repository
from pcapi.scripts.delete_corrupted_allocine_stocks import delete_corrupted_allocine_stocks


@pytest.mark.usefixtures("db_session")
def test_should_delete_stock_from_allocine_provider_with_specific_id_at_provider_format(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    allocine_provider = get_provider_by_local_class("AllocineStocks")
    offer = create_offer_with_thing_product(venue)
    stock = create_stock(
        id_at_providers="TW92aWU6MjczNjU5%38986972800011-1",
        is_soft_deleted=True,
        last_provider_id=allocine_provider.id,
        offer=offer,
    )
    repository.save(stock)

    # When
    delete_corrupted_allocine_stocks()

    # Then
    assert Stock.query.count() == 0


@pytest.mark.usefixtures("db_session")
def test_should_not_delete_stock_from_allocine_with_new_id_format(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    allocine_provider = get_provider_by_local_class("AllocineStocks")
    offer = create_offer_with_thing_product(venue)
    stock = create_stock(
        id_at_providers="TW92aWU6MjczNTc5%31940406700021#LOCAL/2020-01-18T14:00:00",
        is_soft_deleted=True,
        last_provider_id=allocine_provider.id,
        offer=offer,
    )
    repository.save(stock)

    # When
    delete_corrupted_allocine_stocks()

    # Then
    assert Stock.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_should_not_delete_stock_from_other_provider_than_allocine(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    provider = providers_factories.ProviderFactory(localClass="not allociné")
    offer = create_offer_with_thing_product(venue)
    stock = create_stock(
        id_at_providers="TW92aWU6MjczNjU5%38986972800011-1",
        is_soft_deleted=True,
        last_provider_id=provider.id,
        offer=offer,
    )
    repository.save(stock)

    # When
    delete_corrupted_allocine_stocks()

    # Then
    assert Stock.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_should_not_delete_stock_from_allocine_when_not_sof_deleted(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    allocine_provider = get_provider_by_local_class("AllocineStocks")
    offer = create_offer_with_thing_product(venue)
    stock = create_stock(
        id_at_providers="TW92aWU6MjczNjU5%38986972800011-1",
        is_soft_deleted=False,
        last_provider_id=allocine_provider.id,
        offer=offer,
    )
    repository.save(stock)

    # When
    delete_corrupted_allocine_stocks()

    # Then
    assert Stock.query.count() == 1
